#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["aiohttp", "argparse", "PyYAML", "scikit-learn", "flask"]
# ///

"""
API 服务器 - 供应商商品比价管理系统

启动方式: python api_server.py
访问地址: http://localhost:3001
"""

import os
import sys
import io
import csv
import json
import yaml
import asyncio
import aiohttp
import argparse
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 添加父目录到路径以便导入 main.py 的模块
sys.path.insert(0, str(Path(__file__).parent))
from main import (
    SupplierGoods, MarketMatch, PriceAnalysis, DataStore, NLPMatcher,
    get_market_price, analyze_price, should_list, search,
    HEADERS, PLATFORM_MAP,
)

def api_get_market_price(brand: str, model: str, spec: str, name: str = "",
                         source: int = 0, page: int = 1) -> List[Dict]:
    """获取市场价格 - 使用同步 requests"""
    import requests

    keyword = f"{brand} {model} {spec} {name}".strip()

    headers = {
        **HEADERS,
        "User-Agent": "MaiShouApp/3.7.7 (iPhone; iOS 26.3; Scale/3.00)",
        "openid": "564bdce0fa408fc9e1d5d42fd022ef0b",
        "version": "3.7.7.2",
    }

    data = {
        "isCoupon": 0,
        "keyword": keyword,
        "openid": "564bdce0fa408fc9e1d5d42fd022ef0b",
        "order": "desc",
        "page": page,
        "pddListId": "",
        "sort": "",
        "sourceType": str(source),
        "user_id": "",
    }

    try:
        resp = requests.post(
            "https://appapi.maishou88.com/api/v1/homepage/searchList",
            headers=headers,
            data=data,
            timeout=10
        )
        resp.encoding = "utf-8-sig"
        json_data = resp.json() or {}

        # 兼容两种响应格式
        rows = json_data.get("data", [])
        if not isinstance(rows, list):
            rows = []

        if not rows:
            return []

        # 转换数据格式
        results = []
        for v in rows:
            platform = PLATFORM_MAP.get(v.get("sourceType", 0), "未知")

            # 解析销量数据（支持 "3.8万+" 格式）
            month_sales_str = v.get("monthSales", "0")
            month_sales = 0
            if isinstance(month_sales_str, str):
                # 处理 "3.8万+" 格式
                if '万' in month_sales_str:
                    try:
                        num = float(month_sales_str.replace('万', '').replace('+', ''))
                        month_sales = int(num * 10000)
                    except:
                        month_sales = 0
                else:
                    try:
                        month_sales = int(float(month_sales_str.replace('+', '')))
                    except:
                        month_sales = 0
            else:
                month_sales = int(month_sales_str or 0)

            results.append({
                "platform": platform,
                "title": v.get("title", ""),
                "shop_name": v.get("shopName", ""),
                "originalPrice": v.get("originalPrice", 0),
                "actualPrice": v.get("actualPrice", 0),
                "couponPrice": v.get("couponPrice", 0),
                "monthSales": month_sales,
                "goodsId": v.get("goodsId", ""),
                "sourceType": v.get("sourceType", 0),
            })

        return results
    except Exception as e:
        print(f"获取市场数据失败: {e}")
        return []

# ==================== API 服务器 ====================
async def api_server():
    """启动 API 服务器"""
    from flask import Flask, jsonify, request

    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    @app.after_request
    def add_cors_headers(response):
        # Allow frontend dev servers (localhost:5173/5174) to access API.
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response

    # 初始化存储和匹配器
    store = DataStore()
    matcher = NLPMatcher()

    global API_SESSION
    API_SESSION = aiohttp.ClientSession()

    @app.route('/api/products', methods=['GET'])
    def get_products():
        """获取商品列表"""
        try:
            suppliers = store.load_suppliers()
            return jsonify([asdict(s) for s in suppliers])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/products', methods=['POST'])
    def add_product():
        """添加商品"""
        try:
            data = request.json
            goods = SupplierGoods(
                id=store.generate_id(),
                name=data.get('name', ''),
                brand=data.get('brand', ''),
                model=data.get('model', ''),
                spec=data.get('spec', ''),
                price=float(data.get('price', 0)),
                supplier_name=data.get('supplier_name', ''),
                created_at=store._get_timestamp(),
                updated_at=store._get_timestamp(),
                status='pending'
            )
            suppliers = store.load_suppliers()
            suppliers.append(goods)
            store.save_suppliers(suppliers)
            return jsonify(asdict(goods))
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

    @app.route('/api/products/<product_id>', methods=['DELETE'])
    def delete_product(product_id):
        """删除商品"""
        try:
            suppliers = store.load_suppliers()
            suppliers = [s for s in suppliers if s.id != product_id]
            store.save_suppliers(suppliers)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/products/<product_id>', methods=['PUT'])
    def update_product(product_id):
        """更新商品"""
        try:
            data = request.json
            suppliers = store.load_suppliers()
            for s in suppliers:
                if s.id == product_id:
                    if 'price' in data:
                        s.price = float(data['price'])
                    if 'status' in data:
                        s.status = data['status']
                    s.updated_at = store._get_timestamp()
                    store.save_suppliers(suppliers)
                    return jsonify(asdict(s))
            return jsonify({'error': 'Product not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analyze/<product_id>', methods=['GET'])
    def analyze_product(product_id):
        """分析商品价格 - 从 maishou88.com 获取真实数据"""
        try:
            source = request.args.get('source', '0')
            page = request.args.get('page', '1')

            suppliers = store.load_suppliers()
            target = None
            for s in suppliers:
                if s.id == product_id:
                    target = s
                    break

            if not target:
                return jsonify({'error': 'Product not found'}), 404

            # 从 maishou88.com 获取真实数据
            market_results = api_get_market_price(
                target.brand, target.model, target.spec, target.name,
                int(source), int(page)
            )

            # NLP 匹配
            matches = matcher.match(target, market_results, threshold=0.5)

            # 价格分析 + 上下架结论（与批量分析一致）
            analysis = analyze_price(target, matches)
            action, reason = should_list(analysis, getattr(target, 'sales_count', 0) or 0)

            # 同步写入商品状态，列表里会显示「已上架 / 审核中」等
            status_map = {
                'listed': 'listed',
                'review': 'review',
                'delisted': 'delisted',
                'rejected': 'review',
            }
            new_status = status_map.get(action, 'review')
            suppliers = store.load_suppliers()
            for s in suppliers:
                if s.id == product_id:
                    s.status = new_status
                    s.updated_at = store._get_timestamp()
                    break
            store.save_suppliers(suppliers)

            return jsonify({
                'supplier_price': analysis.supplier_price,
                'lowest_price': analysis.lowest_price,
                'lowest_price_with_coupon': analysis.lowest_price_with_coupon,
                'avg_price': analysis.avg_price,
                'deviation_rate': analysis.deviation_rate,
                'deviation_rate_with_coupon': analysis.deviation_rate_with_coupon,
                'deviation_from_avg': analysis.deviation_from_avg,
                'lowest_platform': analysis.lowest_platform,
                'action': action,
                'reason': reason,
                'market_matches': [
                    {
                        'platform': m.platform,
                        'title': m.title,
                        'shop_name': m.shop_name,
                        'original_price': m.original_price,
                        'actual_price': m.actual_price,
                        'coupon_price': m.coupon_price,
                        'month_sales': m.month_sales,
                        'similarity': m.similarity,
                        'match_type': m.match_type,
                        'goods_id': m.goods_id
                    }
                    for m in analysis.market_matches
                ]
            })
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

    @app.route('/api/batch-analyze', methods=['POST'])
    def batch_analyze():
        """批量分析商品"""
        try:
            data = request.json or {}
            status_filter = data.get('status', 'pending')
            source = int(data.get('source', 0))

            suppliers = store.load_suppliers()
            if status_filter:
                # 与前端待分析口径对齐：传 pending 时同时包含 review（待复核）
                if status_filter == 'pending':
                    targets = [s for s in suppliers if s.status in ('pending', 'review')]
                else:
                    targets = [s for s in suppliers if s.status == status_filter]
            else:
                targets = [s for s in suppliers if s.status in ('pending', 'review')]

            results = []
            for target in targets:
                # 与单商品分析保持同一取数路径，避免同商品单条/批量结果不一致
                market_results = api_get_market_price(
                    target.brand, target.model, target.spec, target.name,
                    source, 1
                )
                matches = matcher.match(target, market_results, threshold=0.5)
                analysis = analyze_price(target, matches)
                action, reason = should_list(analysis, target.sales_count)

                status_map = {
                    'listed': 'listed',
                    'review': 'review',
                    'delisted': 'delisted',
                    'rejected': 'review',
                }
                target.status = status_map.get(action, 'review')
                target.updated_at = store._get_timestamp()

                results.append({
                    'id': target.id,
                    'name': f'{target.brand} {target.model}',
                    'price': target.price,
                    'lowest_price': analysis.lowest_price,
                    'deviation_rate': analysis.deviation_from_avg,
                    'deviation_from_avg': analysis.deviation_from_avg,
                    'action': action,
                    'reason': reason
                })

            # 批量分析后持久化状态，刷新列表与分析结论保持一致
            store.save_suppliers(suppliers)
            return jsonify(results)
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

    @app.route('/api/search', methods=['GET'])
    def search_products():
        """搜索市场商品"""
        try:
            keyword = request.args.get('keyword', '')
            source = request.args.get('source', '0')
            page = request.args.get('page', '1')

            if not keyword:
                return jsonify({'error': 'Keyword required'}), 400

            result = asyncio.run(search(keyword, int(source), page=int(page)))
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/health', methods=['GET'])
    def health():
        """健康检查"""
        return jsonify({'status': 'ok'})

    print("=" * 50)
    print("API 服务器已启动!")
    print("访问地址: http://localhost:3001")
    print("=" * 50)

    # 使用 threading 在独立线程中运行 Flask
    def run_flask():
        app.run(host='0.0.0.0', port=3001, debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 保持主线程运行
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    print("正在启动 API 服务器...")
    asyncio.run(api_server())
