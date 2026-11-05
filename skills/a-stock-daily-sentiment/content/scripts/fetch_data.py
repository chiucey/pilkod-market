#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股每日数据获取脚本
使用AKShare获取市场数据

依赖安装: pip install akshare pandas
"""

import json
import datetime
from typing import Dict, List, Any, Optional

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("请先安装依赖: pip install akshare pandas")
    raise


def get_trade_date() -> str:
    """获取最近一个交易日"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    return today


def get_market_overview() -> Dict[str, Any]:
    """获取市场概览数据"""
    try:
        # 沪深两市实时行情
        df = ak.stock_zh_a_spot_em()

        # 基本统计
        total = len(df)
        up = len(df[df['涨跌幅'] > 0])
        down = len(df[df['涨跌幅'] < 0])
        flat = len(df[df['涨跌幅'] == 0])

        # 涨跌停统计（过滤ST）
        non_st = df[~df['名称'].str.contains('ST', na=False)]
        limit_up = len(non_st[non_st['涨跌幅'] >= 9.5])  # 接近涨停
        limit_down = len(non_st[non_st['涨跌幅'] <= -9.5])  # 接近跌停

        # 涨跌幅分布
        ranges = {
            '>7%': len(non_st[(non_st['涨跌幅'] > 7) & (non_st['涨跌幅'] <= 100)]),
            '5-7%': len(non_st[(non_st['涨跌幅'] >= 5) & (non_st['涨跌幅'] < 7)]),
            '3-5%': len(non_st[(non_st['涨跌幅'] >= 3) & (non_st['涨跌幅'] < 5)]),
            '2-3%': len(non_st[(non_st['涨跌幅'] >= 2) & (non_st['涨跌幅'] < 3)]),
            '0-2%': len(non_st[(non_st['涨跌幅'] >= 0) & (non_st['涨跌幅'] < 2)]),
            '-2-0%': len(non_st[(non_st['涨跌幅'] >= -2) & (non_st['涨跌幅'] < 0)]),
            '-3--2%': len(non_st[(non_st['涨跌幅'] >= -3) & (non_st['涨跌幅'] < -2)]),
            '-5--3%': len(non_st[(non_st['涨跌幅'] >= -5) & (non_st['涨跌幅'] < -3)]),
            '-7--5%': len(non_st[(non_st['涨跌幅'] >= -7) & (non_st['涨跌幅'] < -5)]),
            '<-7%': len(non_st[(non_st['涨跌幅'] < -7) & (non_st['涨跌幅'] >= -100)]),
        }

        # 成交量统计（沪市和深市分开）
        sh_df = df[df['代码'].str.startswith(('600', '601', '603', '605', '688'))]
        sz_df = df[df['代码'].str.startswith(('000', '001', '002', '003', '300'))]

        sh_volume = sh_df['成交额'].sum() / 1e8  # 亿元
        sz_volume = sz_df['成交额'].sum() / 1e8

        return {
            'trade_date': get_trade_date(),
            'total': total,
            'up': up,
            'down': down,
            'flat': flat,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'range_distribution': ranges,
            'shanghai_volume': round(sh_volume, 2),
            'shenzhen_volume': round(sz_volume, 2),
            'total_volume': round(sh_volume + sz_volume, 2)
        }
    except Exception as e:
        return {'error': str(e)}


def get_limit_up_stocks() -> List[Dict[str, Any]]:
    """获取涨停个股数据"""
    try:
        # 涨停股详情
        df = ak.stock_zt_pool_em(date=get_trade_date())

        # 过滤ST股
        df = df[~df['股票名称'].str.contains('ST', na=False)]

        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                'code': row.get('代码', ''),
                'name': row.get('股票名称', ''),
                'close': float(row.get('最新价', 0)),
                'change_pct': float(row.get('涨跌幅', 0)),
                'turnover': row.get('成交额', ''),
                'reason': row.get('涨停统计', '') or row.get('连板数', ''),
                'consecutive_days': int(row.get('连板数', 1))
            })

        return stocks
    except Exception as e:
        return [{'error': str(e)}]


def get_limit_down_stocks() -> List[Dict[str, Any]]:
    """获取跌停个股数据"""
    try:
        # 跌停股详情
        df = ak.stock_zt_pool_dt_em(date=get_trade_date())

        # 过滤ST股
        df = df[~df['股票名称'].str.contains('ST', na=False)]

        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                'code': row.get('代码', ''),
                'name': row.get('股票名称', ''),
                'close': float(row.get('最新价', 0)),
                'change_pct': float(row.get('涨跌幅', 0))
            })

        return stocks
    except Exception as e:
        return [{'error': str(e)}]


def get_sector_flow() -> Dict[str, Any]:
    """获取板块资金流向"""
    try:
        # 行业板块资金流向
        df = ak.stock_sector_fund_flow_rank(indicator="今日")

        # 按净流入排序
        df_sorted = df.sort_values('今日主力净流入-净额', ascending=False)

        # 获取TOP10
        top10 = []
        for _, row in df_sorted.head(10).iterrows():
            top10.append({
                'sector': row.get('名称', ''),
                'change_pct': float(row.get('涨跌幅', 0)),
                'net_inflow': round(float(row.get('今日主力净流入-净额', 0)) / 1e8, 2),
                'count': int(row.get('上涨数', 0)) + int(row.get('下跌数', 0))
            })

        # 概念板块
        concept_df = ak.stock_board_concept_name_em()
        concept_flow = ak.stock_board_concept_fund_flow()

        return {
            'industry_top10': top10,
            'concept_flow': concept_flow.head(10).to_dict('records') if concept_flow is not None else []
        }
    except Exception as e:
        return {'error': str(e)}


def get_institution_trades() -> Dict[str, Any]:
    """获取机构席位买卖数据"""
    try:
        # 龙虎榜数据
        df = ak.stock_lhb_detail_em(date=get_trade_date())

        if df is None or df.empty:
            return {'daily': [], 'three_day': []}

        # 提取机构席位数据
        institution_df = df[df['买方机构'].notna() & (df['买方机构'] > 0)]

        daily = []
        for _, row in institution_df.head(10).iterrows():
            daily.append({
                'code': row.get('代码', ''),
                'name': row.get('名称', ''),
                'close': float(row.get('收盘价', 0)),
                'change_pct': float(row.get('涨跌幅', 0)),
                'buy_inst': int(row.get('买方机构', 0)),
                'sell_inst': int(row.get('卖方机构', 0)),
                'buy_amount': round(float(row.get('买方机构买入金额', 0)) / 1e4, 2),
                'sell_amount': round(float(row.get('卖方机构卖出金额', 0)) / 1e4, 2),
                'net_amount': round(float(row.get('买方机构买入金额', 0) - row.get('卖方机构卖出金额', 0)) / 1e4, 2)
            })

        return {'daily': daily, 'three_day': []}
    except Exception as e:
        return {'error': str(e), 'daily': [], 'three_day': []}


def get_hot_money_trades() -> Dict[str, Any]:
    """获取游资席位动向"""
    try:
        # 营业部排行
        df = ak.stock_lhb_yyb_ph_em(date=get_trade_date())

        if df is None or df.empty:
            return {'buy': [], 'sell': []}

        buy_trades = []
        sell_trades = []

        for _, row in df.iterrows():
            trade = {
                'seat': row.get('营业部名称', ''),
                'stock': row.get('股票代码', ''),
                'amount': round(float(row.get('成交金额', 0)) / 1e8, 2)
            }

            if '买入' in str(row.get('买卖方向', '')):
                buy_trades.append(trade)
            else:
                sell_trades.append(trade)

        return {'buy': buy_trades[:10], 'sell': sell_trades[:10]}
    except Exception as e:
        return {'error': str(e), 'buy': [], 'sell': []}


def get_new_high_stocks() -> List[Dict[str, Any]]:
    """获取股价创新高个股"""
    try:
        # 历史新高
        df = ak.stock_zt_pool_strong_em(date=get_trade_date())

        if df is None or df.empty:
            return []

        # 过滤ST股
        df = df[~df['股票名称'].str.contains('ST', na=False)]

        stocks = []
        for _, row in df.head(20).iterrows():
            stocks.append({
                'code': row.get('代码', ''),
                'name': row.get('股票名称', ''),
                'close': float(row.get('最新价', 0)),
                'change_pct': float(row.get('涨跌幅', 0)),
                'sector': row.get('所属行业', ''),
                'highlight': row.get('涨停统计', '')
            })

        return stocks
    except Exception as e:
        return [{'error': str(e)}]


def get_index_data() -> Dict[str, Any]:
    """获取主要指数数据"""
    try:
        indices = {
            '上证指数': '000001',
            '深证成指': '399001',
            '创业板指': '399006',
            '科创50': '000688'
        }

        result = {}
        for name, code in indices.items():
            try:
                df = ak.stock_zh_index_spot_em(symbol=code)
                if df is not None and not df.empty:
                    result[name] = {
                        'close': float(df.iloc[0]['最新价']),
                        'change_pct': float(df.iloc[0]['涨跌幅']),
                        'volume': float(df.iloc[0]['成交量'])
                    }
            except:
                continue

        return result
    except Exception as e:
        return {'error': str(e)}


def fetch_all_data() -> Dict[str, Any]:
    """获取所有市场数据"""
    print("开始获取A股市场数据...")

    data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'market_overview': get_market_overview(),
        'index_data': get_index_data(),
        'limit_up_stocks': get_limit_up_stocks(),
        'limit_down_stocks': get_limit_down_stocks(),
        'sector_flow': get_sector_flow(),
        'institution_trades': get_institution_trades(),
        'hot_money': get_hot_money_trades(),
        'new_high_stocks': get_new_high_stocks()
    }

    return data


def save_data(data: Dict[str, Any], filepath: str = 'a_stock_data.json'):
    """保存数据到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filepath}")


if __name__ == '__main__':
    # 测试数据获取
    data = fetch_all_data()

    # 打印概览
    overview = data.get('market_overview', {})
    if 'error' not in overview:
        print(f"\n=== 市场概览 ===")
        print(f"涨停: {overview.get('limit_up', 0)}家")
        print(f"跌停: {overview.get('limit_down', 0)}家")
        print(f"上涨: {overview.get('up', 0)}家")
        print(f"下跌: {overview.get('down', 0)}家")
        print(f"总成交: {overview.get('total_volume', 0)}亿")

    # 保存完整数据
    save_data(data)
