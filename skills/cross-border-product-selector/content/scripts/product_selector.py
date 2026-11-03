#!/usr/bin/env python3
"""
跨境电商选品分析工具
支持选品热点更新、爆品发现、市场趋势分析
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import random

class ProductSelector:
    """跨境电商选品工具类"""

    def __init__(self, data_dir: str = None):
        """初始化选品工具"""
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(exist_ok=True)

        # 数据文件路径
        self.hot_topics_file = self.data_dir / "hot_topics.json"
        self.best_sellers_file = self.data_dir / "best_sellers.json"
        self.market_trends_file = self.data_dir / "market_trends.json"
        self.categories_file = self.data_dir / "categories.json"

    def _load_json(self, file_path: Path, default: dict = None) -> dict:
        """加载JSON文件"""
        if default is None:
            default = {}
        if file_path.exists():
            try:
                return json.loads(file_path.read_text(encoding='utf-8'))
            except:
                return default
        return default

    def _save_json(self, file_path: Path, data: dict) -> bool:
        """保存JSON文件"""
        try:
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return True
        except:
            return False

    def get_hot_topics(self) -> Dict:
        """获取选品热点数据"""
        return self._load_json(self.hot_topics_file, {
            "last_updated": datetime.now().isoformat(),
            "topics": []
        })

    def update_hot_topics(self, topics: List[Dict] = None) -> bool:
        """更新选品热点数据"""
        if topics is None:
            # 生成默认热点数据
            topics = self._generate_sample_topics()

        data = {
            "last_updated": datetime.now().isoformat(),
            "topics": topics
        }
        return self._save_json(self.hot_topics_file, data)

    def _generate_sample_topics(self) -> List[Dict]:
        """生成示例热点数据"""
        categories = [
            {"name": "家居用品", "trend": "上升", "heat_score": 95},
            {"name": "户外运动", "trend": "上升", "heat_score": 92},
            {"name": "宠物用品", "trend": "稳定", "heat_score": 88},
            {"name": "美妆护肤", "trend": "上升", "heat_score": 85},
            {"name": "3C电子配件", "trend": "稳定", "heat_score": 82},
            {"name": "母婴用品", "trend": "下降", "heat_score": 78},
            {"name": "厨房用品", "trend": "上升", "heat_score": 90},
            {"name": "健身器材", "trend": "上升", "heat_score": 87},
        ]
        return categories

    def get_best_sellers(self) -> Dict:
        """获取爆品数据"""
        return self._load_json(self.best_sellers_file, {
            "last_updated": datetime.now().isoformat(),
            "products": []
        })

    def update_best_sellers(self, products: List[Dict] = None) -> bool:
        """更新爆品数据"""
        if products is None:
            products = self._generate_sample_products()

        data = {
            "last_updated": datetime.now().isoformat(),
            "products": products
        }
        return self._save_json(self.best_sellers_file, data)

    def _generate_sample_products(self) -> List[Dict]:
        """生成示例爆品数据"""
        products = [
            {
                "name": "便携式充电宝 20000mAh",
                "platform": "Amazon",
                "market": "北美",
                "price_range": "$25-35",
                "monthly_sales": 15000,
                "review_count": 8500,
                "rating": 4.5,
                "differentiation": "大容量、快充、轻薄",
                "entry_time": "2025-06",
                "growth_rate": "45%"
            },
            {
                "name": "智能跳绳计数器",
                "platform": "TikTok Shop",
                "market": "东南亚",
                "price_range": "$15-25",
                "monthly_sales": 25000,
                "review_count": 5000,
                "rating": 4.6,
                "differentiation": "智能计数、APP联动、运动社交",
                "entry_time": "2025-09",
                "growth_rate": "120%"
            },
            {
                "name": "折叠收纳购物车",
                "platform": "eBay",
                "market": "欧洲",
                "price_range": "€30-45",
                "monthly_sales": 8000,
                "review_count": 4200,
                "rating": 4.4,
                "differentiation": "可折叠、万向轮、可爬楼梯",
                "entry_time": "2025-07",
                "growth_rate": "65%"
            },
            {
                "name": "宠物自动饮水机",
                "platform": "Amazon",
                "market": "北美",
                "price_range": "$30-50",
                "monthly_sales": 12000,
                "review_count": 9800,
                "rating": 4.7,
                "differentiation": "循环过滤、静音设计、大容量",
                "entry_time": "2025-05",
                "growth_rate": "35%"
            },
            {
                "name": "多功能厨房砧板",
                "platform": "Temu",
                "market": "北美",
                "price_range": "$12-18",
                "monthly_sales": 35000,
                "review_count": 12000,
                "rating": 4.3,
                "differentiation": "分类切菜、沥水功能、材质安全",
                "entry_time": "2025-08",
                "growth_rate": "88%"
            }
        ]
        return products

    def get_market_trends(self) -> Dict:
        """获取市场趋势数据"""
        return self._load_json(self.market_trends_file, {
            "last_updated": datetime.now().isoformat(),
            "trends": []
        })

    def update_market_trends(self, trends: List[Dict] = None) -> bool:
        """更新市场趋势数据"""
        if trends is None:
            trends = self._generate_sample_trends()

        data = {
            "last_updated": datetime.now().isoformat(),
            "trends": trends
        }
        return self._save_json(self.market_trends_file, data)

    def _generate_sample_trends(self) -> List[Dict]:
        """生成示例趋势数据"""
        trends = [
            {
                "trend_name": "健康生活",
                "description": "后疫情时代，消费者更加关注健康和免疫力提升",
                "related_categories": ["健身器材", "营养保健品", "空气净化器"],
                "market": "北美、欧洲",
                "growth_rate": "+35%"
            },
            {
                "trend_name": "居家办公经济",
                "description": "远程办公常态化，家居办公用品需求持续增长",
                "related_categories": ["人体工学椅", "桌面收纳", "照明设备"],
                "market": "全球",
                "growth_rate": "+28%"
            },
            {
                "trend_name": "智能家居",
                "description": "IoT设备普及，智能家居产品进入快速增长期",
                "related_categories": ["智能灯泡", "智能插座", "安防摄像头"],
                "market": "北美、欧洲、东南亚",
                "growth_rate": "+42%"
            },
            {
                "trend_name": "宠物拟人化",
                "description": "宠物被视为家庭成员，宠物消费持续升级",
                "related_categories": ["宠物家具", "智能喂食器", "宠物服装"],
                "market": "北美、日本、韩国",
                "growth_rate": "+38%"
            },
            {
                "trend_name": "户外探险",
                "description": "疫情后户外活动增加，露营、徒步装备需求爆发",
                "related_categories": ["露营帐篷", "折叠桌椅", "便携炊具"],
                "market": "北美、欧洲、澳大利亚",
                "growth_rate": "+55%"
            }
        ]
        return trends

    def get_categories(self) -> Dict:
        """获取品类基础数据"""
        return self._load_json(self.categories_file, {
            "last_updated": datetime.now().isoformat(),
            "categories": []
        })

    def update_categories(self, categories: List[Dict] = None) -> bool:
        """更新品类基础数据"""
        if categories is None:
            categories = self._generate_sample_categories()

        data = {
            "last_updated": datetime.now().isoformat(),
            "categories": categories
        }
        return self._save_json(self.categories_file, data)

    def _generate_sample_categories(self) -> List[Dict]:
        """生成示例品类数据"""
        categories = [
            {"name": "家居用品", "competition": "高", "profit_margin": "中", "entry_difficulty": "中"},
            {"name": "3C电子配件", "competition": "高", "profit_margin": "低", "entry_difficulty": "高"},
            {"name": "服装鞋包", "competition": "高", "profit_margin": "中", "entry_difficulty": "中"},
            {"name": "美妆护肤", "competition": "高", "profit_margin": "高", "entry_difficulty": "高"},
            {"name": "母婴用品", "competition": "中", "profit_margin": "高", "entry_difficulty": "高"},
            {"name": "户外运动", "competition": "中", "profit_margin": "高", "entry_difficulty": "中"},
            {"name": "宠物用品", "competition": "低", "profit_margin": "中", "entry_difficulty": "低"},
            {"name": "厨房用品", "competition": "中", "profit_margin": "中", "entry_difficulty": "低"},
            {"name": "办公文具", "competition": "低", "profit_margin": "中", "entry_difficulty": "低"},
            {"name": "汽车配件", "competition": "中", "profit_margin": "高", "entry_difficulty": "中"}
        ]
        return categories

    def add_custom_topic(self, topic: Dict) -> bool:
        """添加自定义热点"""
        data = self.get_hot_topics()
        topics = data.get("topics", [])

        # 检查是否已存在
        for t in topics:
            if t.get("name") == topic.get("name"):
                t.update(topic)
                break
        else:
            topics.append(topic)

        data["topics"] = topics
        data["last_updated"] = datetime.now().isoformat()
        return self._save_json(self.hot_topics_file, data)

    def add_custom_product(self, product: Dict) -> bool:
        """添加自定义爆品"""
        data = self.get_best_sellers()
        products = data.get("products", [])

        # 检查是否已存在
        for i, p in enumerate(products):
            if p.get("name") == product.get("name") and p.get("platform") == product.get("platform"):
                products[i].update(product)
                break
        else:
            products.append(product)

        data["products"] = products
        data["last_updated"] = datetime.now().isoformat()
        return self._save_json(self.best_sellers_file, data)

    def analyze_product_opportunity(self, category: str) -> Dict:
        """分析品类市场机会"""
        categories_data = self.get_categories()
        trends_data = self.get_market_trends()
        hot_topics_data = self.get_hot_topics()

        # 查找品类信息
        category_info = None
        for cat in categories_data.get("categories", []):
            if cat.get("name") == category:
                category_info = cat
                break

        # 查找相关趋势
        related_trends = []
        for trend in trends_data.get("trends", []):
            if category in trend.get("related_categories", []):
                related_trends.append(trend)

        # 查找热度
        heat_score = 0
        for topic in hot_topics_data.get("topics", []):
            if topic.get("name") == category:
                heat_score = topic.get("heat_score", 0)
                break

        # 生成机会评估
        opportunity_score = 50
        if category_info:
            if category_info.get("competition") == "低":
                opportunity_score += 20
            elif category_info.get("competition") == "中":
                opportunity_score += 10

            if category_info.get("profit_margin") == "高":
                opportunity_score += 15

            if category_info.get("entry_difficulty") == "低":
                opportunity_score += 15

        # 趋势加成
        opportunity_score += len(related_trends) * 5
        if heat_score > 80:
            opportunity_score += 10

        opportunity_score = min(100, opportunity_score)

        # 生成建议
        if opportunity_score >= 80:
            recommendation = "强烈推荐"
        elif opportunity_score >= 60:
            recommendation = "建议关注"
        elif opportunity_score >= 40:
            recommendation = "谨慎考虑"
        else:
            recommendation = "不建议"

        return {
            "category": category,
            "opportunity_score": opportunity_score,
            "recommendation": recommendation,
            "category_info": category_info,
            "related_trends": related_trends,
            "heat_score": heat_score,
            "analysis_time": datetime.now().isoformat()
        }

    def generate_report(self, report_type: str = "full") -> str:
        """生成选品分析报告"""
        report_lines = []

        if report_type in ["full", "hot_topics"]:
            report_lines.append("=" * 60)
            report_lines.append("选品热点分析报告")
            report_lines.append("=" * 60)
            report_lines.append(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")

            hot_data = self.get_hot_topics()
            report_lines.append(f"共 {len(hot_data.get('topics', []))} 个热门品类")
            report_lines.append("")

            for topic in hot_data.get("topics", []):
                report_lines.append(f"【{topic.get('name', 'N/A')}】")
                report_lines.append(f"  热度指数: {topic.get('heat_score', 0)}")
                report_lines.append(f"  趋势: {topic.get('trend', '未知')}")
                report_lines.append("")

        if report_type in ["full", "best_sellers"]:
            report_lines.append("=" * 60)
            report_lines.append("爆品分析报告")
            report_lines.append("=" * 60)
            report_lines.append("")

            best_data = self.get_best_sellers()
            for product in best_data.get("products", []):
                report_lines.append(f"【{product.get('name', 'N/A')}】")
                report_lines.append(f"  平台: {product.get('platform', 'N/A')}")
                report_lines.append(f"  市场: {product.get('market', 'N/A')}")
                report_lines.append(f"  价格区间: {product.get('price_range', 'N/A')}")
                report_lines.append(f"  月销量: ~{product.get('monthly_sales', 0):,}")
                report_lines.append(f"  评分: {product.get('rating', 0)} ({product.get('review_count', 0):,} 条评论)")
                report_lines.append(f"  差异化: {product.get('differentiation', 'N/A')}")
                report_lines.append(f"  增长率: {product.get('growth_rate', 'N/A')}")
                report_lines.append("")

        if report_type in ["full", "trends"]:
            report_lines.append("=" * 60)
            report_lines.append("市场趋势分析")
            report_lines.append("=" * 60)
            report_lines.append("")

            trends_data = self.get_market_trends()
            for trend in trends_data.get("trends", []):
                report_lines.append(f"【{trend.get('trend_name', 'N/A')}】")
                report_lines.append(f"  描述: {trend.get('description', 'N/A')}")
                report_lines.append(f"  相关品类: {', '.join(trend.get('related_categories', []))}")
                report_lines.append(f"  目标市场: {trend.get('market', 'N/A')}")
                report_lines.append(f"  增长率: {trend.get('growth_rate', 'N/A')}")
                report_lines.append("")

        return "\n".join(report_lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='跨境电商选品分析工具')
    parser.add_argument('--action', '-a', required=True,
                        choices=['get-topics', 'update-topics', 'get-products',
                                'update-products', 'get-trends', 'update-trends',
                                'analyze', 'report'],
                        help='执行的操作')
    parser.add_argument('--category', '-c',
                        help='分析的品类')
    parser.add_argument('--report-type', '-t', default='full',
                        choices=['full', 'hot_topics', 'best_sellers', 'trends'],
                        help='报告类型')
    parser.add_argument('--data-dir',
                        help='数据目录路径')

    args = parser.parse_args()
    selector = ProductSelector(args.data_dir)

    if args.action == 'get-topics':
        data = selector.get_hot_topics()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.action == 'update-topics':
        if selector.update_hot_topics():
            print("热点数据更新成功")
        else:
            print("更新失败")

    elif args.action == 'get-products':
        data = selector.get_best_sellers()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.action == 'update-products':
        if selector.update_best_sellers():
            print("爆品数据更新成功")
        else:
            print("更新失败")

    elif args.action == 'get-trends':
        data = selector.get_market_trends()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.action == 'update-trends':
        if selector.update_market_trends():
            print("趋势数据更新成功")
        else:
            print("更新失败")

    elif args.action == 'analyze':
        if not args.category:
            print("错误: --category 参数必填")
            return 1
        result = selector.analyze_product_opportunity(args.category)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == 'report':
        print(selector.generate_report(args.report_type))

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
