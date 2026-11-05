"""
Product PK Comparison Generator - 后端比价PK产品明细生成逻辑
支持懂车帝/Rtings/WhatHiFi等评测网站的Category权重体系
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


# ============== Category权重体系 ==============

class CategoryPriority(Enum):
    """权重等级枚举"""
    P0 = 0  # 最高优先级
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    P5 = 5  # 最低优先级


@dataclass
class SubCategory:
    """子类别定义"""
    name: str
    weight: float  # 子类别权重 (0-1)
    source: str  # 数据来源: dongchedi/rtings/whathifi/soundguys/versus
    unit: Optional[str] = None  # 单位
    higher_is_better: bool = True  # 是否越高越好


@dataclass
class Category:
    """主类别定义"""
    name: str
    priority: CategoryPriority
    subcategories: List[SubCategory]
    description: str = ""


# ============== 汽车行业 Category权重矩阵（懂车帝SOP） ==============

CAR_CATEGORIES: List[Category] = [
    Category(
        name="价格/性价比",
        priority=CategoryPriority.P0,
        description="购车首要考虑因素",
        subcategories=[
            SubCategory(name="官方指导价", weight=0.15, source="dongchedi", unit="万元"),
            SubCategory(name="参考落地价", weight=0.12, source="dongchedi", unit="万元"),
            SubCategory(name="性价比指数", weight=0.10, source="dongchedi"),
            SubCategory(name="保值率", weight=0.08, source="dongchedi", unit="%"),
            SubCategory(name="能耗成本", weight=0.05, source="dongchedi", unit="元/百公里"),
        ]
    ),
    Category(
        name="动力性能",
        priority=CategoryPriority.P1,
        description="核心驾驶体验",
        subcategories=[
            SubCategory(name="最大功率", weight=0.12, source="dongchedi", unit="kW"),
            SubCategory(name="峰值扭矩", weight=0.10, source="dongchedi", unit="N·m"),
            SubCategory(name="百公里加速", weight=0.08, source="dongchedi", unit="秒", higher_is_better=False),
            SubCategory(name="最高车速", weight=0.05, source="dongchedi", unit="km/h"),
            SubCategory(name="懂车帝实测分", weight=0.05, source="dongchedi"),
        ]
    ),
    Category(
        name="续航/充电",
        priority=CategoryPriority.P1,
        description="新能源汽车关键指标",
        subcategories=[
            SubCategory(name="CLTC续航", weight=0.12, source="dongchedi", unit="km"),
            SubCategory(name="电池容量", weight=0.08, source="dongchedi", unit="kWh"),
            SubCategory(name="快充时间", weight=0.06, source="dongchedi", unit="分钟", higher_is_better=False),
            SubCategory(name="慢充时间", weight=0.04, source="dongchedi", unit="小时", higher_is_better=False),
        ]
    ),
    Category(
        name="车身尺寸",
        priority=CategoryPriority.P2,
        description="空间实用性",
        subcategories=[
            SubCategory(name="长×宽×高", weight=0.08, source="dongchedi"),
            SubCategory(name="轴距", weight=0.07, source="dongchedi", unit="mm"),
            SubCategory(name="行李厢容积", weight=0.05, source="dongchedi", unit="L"),
            SubCategory(name="整备质量", weight=0.03, source="dongchedi", unit="kg"),
        ]
    ),
    Category(
        name="安全配置",
        priority=CategoryPriority.P2,
        description="主被动安全",
        subcategories=[
            SubCategory(name="气囊数量", weight=0.08, source="dongchedi", unit="个"),
            SubCategory(name="主动刹车", weight=0.06, source="dongchedi"),
            SubCategory(name="车道偏离预警", weight=0.04, source="dongchedi"),
            SubCategory(name="盲点监测", weight=0.04, source="dongchedi"),
        ]
    ),
    Category(
        name="智能驾驶",
        priority=CategoryPriority.P3,
        description="辅助驾驶能力",
        subcategories=[
            SubCategory(name="智能驾驶等级", weight=0.08, source="dongchedi"),
            SubCategory(name="高速NOA", weight=0.05, source="dongchedi"),
            SubCategory(name="城市NOA", weight=0.05, source="dongchedi"),
            SubCategory(name="自动泊车", weight=0.04, source="dongchedi"),
        ]
    ),
    Category(
        name="舒适配置",
        priority=CategoryPriority.P3,
        description="乘坐体验",
        subcategories=[
            SubCategory(name="座椅材质", weight=0.05, source="dongchedi"),
            SubCategory(name="座椅调节方式", weight=0.04, source="dongchedi"),
            SubCategory(name="音响系统", weight=0.04, source="dongchedi"),
            SubCategory(name="空调类型", weight=0.03, source="dongchedi"),
        ]
    ),
    Category(
        name="科技配置",
        priority=CategoryPriority.P4,
        description="车机与互联",
        subcategories=[
            SubCategory(name="中控屏尺寸", weight=0.05, source="dongchedi", unit="英寸"),
            SubCategory(name="车机芯片", weight=0.05, source="dongchedi"),
            SubCategory(name="OTA升级", weight=0.04, source="dongchedi"),
            SubCategory(name="手机互联", weight=0.03, source="dongchedi"),
        ]
    ),
    Category(
        name="用户口碑",
        priority=CategoryPriority.P4,
        description="社会化验证",
        subcategories=[
            SubCategory(name="懂车分", weight=0.08, source="dongchedi"),
            SubCategory(name="综合评分", weight=0.06, source="dongchedi"),
            SubCategory(name="车主评价数", weight=0.04, source="dongchedi", unit="条"),
            SubCategory(name="好评率", weight=0.05, source="dongchedi", unit="%"),
        ]
    ),
    Category(
        name="售后保障",
        priority=CategoryPriority.P5,
        description="购买后保障",
        subcategories=[
            SubCategory(name="整车质保", weight=0.06, source="dongchedi", unit="年/万公里"),
            SubCategory(name="三电质保", weight=0.05, source="dongchedi", unit="年/万公里"),
            SubCategory(name="保养间隔", weight=0.03, source="dongchedi"),
            SubCategory(name="配件价格", weight=0.03, source="dongchedi"),
        ]
    ),
]


# ============== 耳机/音响 Category权重矩阵（Rtings SOP） ==============

HEADPHONE_CATEGORIES: List[Category] = [
    Category(
        name="音质 Sound",
        priority=CategoryPriority.P0,
        description="Rtings权重30%",
        subcategories=[
            SubCategory(name="低频表现", weight=0.10, source="rtings"),
            SubCategory(name="中频表现", weight=0.08, source="rtings"),
            SubCategory(name="高频表现", weight=0.06, source="rtings"),
            SubCategory(name="音场", weight=0.04, source="rtings"),
            SubCategory(name="解析力", weight=0.02, source="rtings"),
        ]
    ),
    Category(
        name="降噪 ANC",
        priority=CategoryPriority.P1,
        description="Rtings权重25%",
        subcategories=[
            SubCategory(name="主动降噪深度", weight=0.12, source="rtings"),
            SubCategory(name="被动隔音", weight=0.08, source="rtings"),
            SubCategory(name="环境音模式", weight=0.05, source="rtings"),
        ]
    ),
    Category(
        name="舒适度 Comfort",
        priority=CategoryPriority.P2,
        description="Rtings权重20%",
        subcategories=[
            SubCategory(name="佩戴感", weight=0.08, source="rtings"),
            SubCategory(name="重量", weight=0.06, source="rtings", unit="g", higher_is_better=False),
            SubCategory(name="夹耳感", weight=0.04, source="rtings"),
            SubCategory(name="材质", weight=0.02, source="rtings"),
        ]
    ),
    Category(
        name="续航 Battery",
        priority=CategoryPriority.P3,
        description="Rtings权重15%",
        subcategories=[
            SubCategory(name="电池续航", weight=0.10, source="rtings", unit="小时"),
            SubCategory(name="充电速度", weight=0.03, source="rtings"),
            SubCategory(name="无线充电", weight=0.02, source="rtings"),
        ]
    ),
    Category(
        name="功能 Features",
        priority=CategoryPriority.P4,
        description="Rtings权重10%",
        subcategories=[
            SubCategory(name="蓝牙版本", weight=0.04, source="rtings"),
            SubCategory(name="多设备连接", weight=0.03, source="rtings"),
            SubCategory(name="APP支持", weight=0.03, source="rtings"),
        ]
    ),
]


# ============== 产品数据模型 ==============

@dataclass
class ProductSpec:
    """产品规格数据"""
    product_id: str
    product_name: str
    brand: str
    category_type: str  # car/headphone/tv/laptop/appliance
    specs: Dict[str, Any]  # {子类别名: 值}
    ratings: Dict[str, float]  # {来源: 评分} e.g. {"dongchedi": 4.5, "rtings": 8.2}
    price: Optional[float] = None
    currency: str = "CNY"
    image_url: Optional[str] = None
    source_url: Optional[str] = None


@dataclass
class ComparisonResult:
    """对比结果"""
    category: Category
    subcategory_results: List[Dict[str, Any]]
    best_product_id: str
    advantage_products: List[str]


@dataclass
class PKReport:
    """PK对比报告"""
    main_product_id: str
    compared_products: List[str]
    comparison_date: str
    report_type: str  # car/headphone/tv/laptop/appliance
    categories: List[ComparisonResult]
    recommendation: Dict[str, Any]
    source_urls: List[str]


# ============== 核心对比引擎 ==============

class PKComparisonEngine:
    """比价PK对比引擎"""

    def __init__(self, report_type: str = "car"):
        self.report_type = report_type
        self.categories = self._get_categories_by_type(report_type)

    def _get_categories_by_type(self, report_type: str) -> List[Category]:
        """根据产品类型获取Category权重矩阵"""
        category_map = {
            "car": CAR_CATEGORIES,
            "headphone": HEADPHONE_CATEGORIES,
            # 可扩展其他类型...
        }
        return category_map.get(report_type, CAR_CATEGORIES)

    def generate_pk_report(
        self,
        main_product: ProductSpec,
        compared_products: List[ProductSpec],
        user_scenario: Optional[str] = None
    ) -> PKReport:
        """
        生成PK对比报告

        Args:
            main_product: 主产品（用户选择的产品）
            compared_products: 对比产品列表
            user_scenario: 用户使用场景 (可选)

        Returns:
            PKReport: 完整的PK对比报告
        """
        all_products = [main_product] + compared_products

        # 1. 按Category权重排序执行对比
        comparison_results = []
        for category in sorted(self.categories, key=lambda x: x.priority.value):
            subcategory_results = self._compare_subcategories(
                category, all_products
            )
            best_id = self._determine_best_product(subcategory_results, all_products)
            advantage_ids = self._get_advantage_products(subcategory_results, all_products)

            comparison_results.append(ComparisonResult(
                category=category,
                subcategory_results=subcategory_results,
                best_product_id=best_id,
                advantage_products=advantage_ids
            ))

        # 2. 生成推荐
        recommendation = self._generate_recommendation(
            all_products, comparison_results, user_scenario
        )

        # 3. 收集来源URL
        source_urls = self._collect_source_urls(all_products)

        return PKReport(
            main_product_id=main_product.product_id,
            compared_products=[p.product_id for p in compared_products],
            comparison_date=self._get_current_date(),
            report_type=self.report_type,
            categories=comparison_results,
            recommendation=recommendation,
            source_urls=source_urls
        )

    def _compare_subcategories(
        self,
        category: Category,
        products: List[ProductSpec]
    ) -> List[Dict[str, Any]]:
        """对比子类别"""
        results = []
        for sub in category.subcategories:
            sub_result = {
                "subcategory_name": sub.name,
                "weight": sub.weight,
                "unit": sub.unit,
                "higher_is_better": sub.higher_is_better,
                "source": sub.source,
                "products": []
            }

            for product in products:
                value = product.specs.get(sub.name, None)
                sub_result["products"].append({
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "value": value,
                    "display_value": self._format_value(value, sub.unit)
                })

            results.append(sub_result)
        return results

    def _determine_best_product(
        self,
        subcategory_results: List[Dict],
        products: List[ProductSpec]
    ) -> str:
        """根据加权评分确定最佳产品"""
        scores = {p.product_id: 0.0 for p in products}

        for sub_result in subcategory_results:
            values = [p["value"] for p in sub_result["products"]]
            if not all(values):
                continue

            if sub_result["higher_is_better"]:
                best_idx = values.index(max(values))
            else:
                best_idx = values.index(min(values))

            for i, p in enumerate(sub_result["products"]):
                if i == best_idx:
                    scores[p["product_id"]] += sub_result["weight"]

        return max(scores, key=scores.get)

    def _get_advantage_products(
        self,
        subcategory_results: List[Dict],
        products: List[ProductSpec]
    ) -> List[str]:
        """获取各子类别优势产品列表"""
        advantages = []
        for sub_result in subcategory_results:
            values = [(i, v["value"]) for i, v in enumerate(sub_result["products"]) if v["value"] is not None]
            if not values:
                continue

            if sub_result["higher_is_better"]:
                best_idx = max(values, key=lambda x: x[1])[0]
            else:
                best_idx = min(values, key=lambda x: x[1])[0]

            advantages.append(sub_result["products"][best_idx]["product_id"])

        return list(set(advantages))

    def _generate_recommendation(
        self,
        products: List[ProductSpec],
        comparison_results: List[ComparisonResult],
        user_scenario: Optional[str]
    ) -> Dict[str, Any]:
        """生成选购建议"""
        # 计算综合得分
        scores = {}
        for product in products:
            score = 0.0
            for comp in comparison_results:
                for sub in comp.subcategory_results:
                    for p in sub["products"]:
                        if p["product_id"] == product.product_id:
                            score += sub["weight"] * (p["value"] or 0)
            scores[product.product_id] = score

        best_id = max(scores, key=scores.get)

        return {
            "overall_best": best_id,
            "scores": scores,
            "recommendations": [
                {
                    "scenario": "性价比优先",
                    "product_id": self._find_best_value_product(products),
                    "reason": "价格最低，性能表现良好"
                },
                {
                    "scenario": "性能优先",
                    "product_id": best_id,
                    "reason": "综合性能最强"
                },
                {
                    "scenario": "口碑优先",
                    "product_id": self._find_best_rating_product(products),
                    "reason": "用户评分最高"
                }
            ]
        }

    def _find_best_value_product(self, products: List[ProductSpec]) -> str:
        """找到性价比最高的产品"""
        value_products = [(p.product_id, p.price, p.ratings)
                        for p in products if p.price]
        if not value_products:
            return products[0].product_id
        return min(value_products, key=lambda x: x[1])[0]

    def _find_best_rating_product(self, products: List[ProductSpec]) -> str:
        """找到评分最高的产品"""
        rating_products = [(p.product_id, p.ratings) for p in products if p.ratings]
        if not rating_products:
            return products[0].product_id

        def avg_rating(r):
            return sum(r.values()) / len(r) if r else 0

        return max(rating_products, key=lambda x: avg_rating(x[1]))[0]

    def _collect_source_urls(self, products: List[ProductSpec]) -> List[str]:
        """收集数据来源URL"""
        urls = []
        for p in products:
            if p.source_url:
                urls.append(p.source_url)
        return list(set(urls))

    def _format_value(self, value: Any, unit: Optional[str]) -> str:
        """格式化数值显示"""
        if value is None:
            return "-"
        if unit:
            return f"{value}{unit}"
        return str(value)

    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def to_markdown(self, report: PKReport) -> str:
        """将报告转换为Markdown格式"""
        from datetime import datetime

        md = f"""# {report.report_type.upper()} 产品PK对比报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据来源：懂车帝 / Rtings / WhatHiFi / SoundGuys / Versus

---

## 选购快速通道

| 您的需求 | 推荐产品 | 核心优势 |
|----------|----------|----------|
"""

        for rec in report.recommendation.get("recommendations", []):
            md += f"| {rec['scenario']} | {rec['product_id']} | {rec['reason']} |\n"

        md += "\n---\n"

        # 按Category权重顺序输出
        for comp in report.categories:
            cat = comp.category
            md += f"\n## 【P{cat.priority.value}】{cat.name}\n"
            md += f"*{cat.description}*\n\n"

            for sub in comp.subcategory_results:
                md += f"### {sub['subcategory_name']}\n"
                md += "| 产品 | "
                md += " | ".join([p["product_name"] for p in sub["products"]])
                md += " |\n|------|"
                md += "|" + "|".join(["---"] * len(sub["products"]))
                md += "|\n| 值 | "
                md += " | ".join([p["display_value"] for p in sub["products"]])
                md += " |\n"
                if sub["source"]:
                    md += f"*来源: {sub['source']}*\n"
                md += "\n"

        # 专业评测参考
        md += "\n---\n\n## 专业评测参考\n\n"
        md += "| 评测源 | "
        all_products = report.categories[0].subcategory_results[0]["products"]
        md += " | ".join([p["product_name"] for p in all_products])
        md += " |\n|--------|"
        md += "|" + "|".join(["---"] * len(all_products))
        md += "|\n"

        for source in ["dongchedi", "rtings", "whathifi", "soundguys", "versus"]:
            md += f"| {source.upper()} | "
            md += " | ".join(["-"] * len(all_products))
            md += " |\n"

        # 最终建议
        md += "\n---\n\n## 最终选购建议\n\n"

        overall_best_id = report.recommendation.get("overall_best", "")
        md += f"**综合最优**: {overall_best_id}\n\n"

        for rec in report.recommendation.get("recommendations", []):
            md += f"### {rec['scenario']}\n"
            md += f"- 推荐: {rec['product_id']}\n"
            md += f"- 理由: {rec['reason']}\n\n"

        # 参考链接
        if report.source_urls:
            md += "\n---\n\n## 参考链接\n\n"
            for url in report.source_urls:
                md += f"- {url}\n"

        return md


# ============== 示例使用 ==============

def demo():
    """演示示例"""
    # 创建示例产品数据
    products = [
        ProductSpec(
            product_id="xiaomi_su7_max",
            product_name="小米SU7 Max",
            brand="小米",
            category_type="car",
            price=29.99,
            specs={
                "最大功率": 495,
                "峰值扭矩": 838,
                "百公里加速": 2.78,
                "CLTC续航": 800,
                "电池容量": 101,
                "轴距": 3000,
                "气囊数量": 12,
                "官方指导价": 29.99,
            },
            ratings={"dongchedi": 4.8, "懂车帝实测": 92},
            source_url="https://www.dongchedi.com/auto/xxx"
        ),
        ProductSpec(
            product_id="tesla_model3_performance",
            product_name="特斯拉Model 3 Performance",
            brand="特斯拉",
            category_type="car",
            price=33.59,
            specs={
                "最大功率": 486,
                "峰值扭矩": 659,
                "百公里加速": 3.1,
                "CLTC续航": 713,
                "电池容量": 78.4,
                "轴距": 2875,
                "气囊数量": 8,
                "官方指导价": 33.59,
            },
            ratings={"dongchedi": 4.6, "懂车帝实测": 88},
            source_url="https://www.dongchedi.com/auto/yyy"
        ),
        ProductSpec(
            product_id="byd_han_ev",
            product_name="比亚迪汉EV",
            brand="比亚迪",
            category_type="car",
            price=25.98,
            specs={
                "最大功率": 380,
                "峰值扭矩": 700,
                "百公里加速": 3.9,
                "CLTC续航": 715,
                "电池容量": 85.4,
                "轴距": 2920,
                "气囊数量": 11,
                "官方指导价": 25.98,
            },
            ratings={"dongchedi": 4.7, "懂车帝实测": 90},
            source_url="https://www.dongchedi.com/auto/zzz"
        ),
    ]

    # 生成PK报告
    engine = PKComparisonEngine(report_type="car")
    report = engine.generate_pk_report(
        main_product=products[0],
        compared_products=products[1:],
        user_scenario="追求性价比与性能平衡"
    )

    # 输出Markdown报告
    print(engine.to_markdown(report))

    # 也可以输出JSON
    print("\n\n=== JSON格式 ===\n")
    print(json.dumps({
        "main_product": report.main_product_id,
        "compared_products": report.compared_products,
        "comparison_date": report.comparison_date,
        "recommendation": report.recommendation,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demo()
