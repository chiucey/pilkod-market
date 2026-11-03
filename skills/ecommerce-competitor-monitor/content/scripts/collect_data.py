#!/usr/bin/env python3
"""
电商竞品数据采集脚本
用于辅助采集京东、天猫竞品数据并生成结构化JSON
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_data_structure():
    """创建标准数据结构"""
    return {
        "category": "",
        "platform": "",
        "采集时间": "",
        "采集人员": "MiniMax Agent",
        "version": "1.0.0",
        "products": [],
        "summary": {
            "total_products": 0,
            "price_range": {"min": 0, "max": 0, "avg": 0},
            "sales_volume_total": 0,
            "revenue_total": 0
        }
    }

def add_product(data, product_info):
    """添加产品到数据结构"""
    product = {
        "rank": product_info.get("rank", len(data["products"]) + 1),
        "name": product_info.get("name", ""),
        "brand": product_info.get("brand", ""),
        "model": product_info.get("model", ""),
        "price": float(product_info.get("price", 0)),
        "sales_volume": int(product_info.get("sales_volume", 0)),
        "estimated_revenue": 0,
        "estimated_roi": 0.0,
        "url": product_info.get("url", ""),
        "main_image": product_info.get("main_image", ""),
        "shop_name": product_info.get("shop_name", ""),
        "tags": product_info.get("tags", []),
        "price_change": product_info.get("price_change", 0),
        "sales_change": product_info.get("sales_change", 0)
    }

    # 计算预估销售额和ROI
    product["estimated_revenue"] = product["price"] * product["sales_volume"]
    # ROI估算：假设行业平均转化率为2%，平均客单价为产品价格的1.5倍
    estimated_orders = product["sales_volume"] * 0.02
    estimated_profit = estimated_orders * product["price"] * 0.1  # 假设利润率10%
    estimated_cost = product["price"] * estimated_orders * 0.9  # 成本
    if estimated_cost > 0:
        product["estimated_roi"] = round(estimated_profit / estimated_cost, 2)

    data["products"].append(product)

def update_summary(data):
    """更新汇总数据"""
    products = data["products"]
    if not products:
        return

    prices = [p["price"] for p in products]
    total_sales = sum(p["sales_volume"] for p in products)
    total_revenue = sum(p["estimated_revenue"] for p in products)

    data["summary"]["total_products"] = len(products)
    data["summary"]["price_range"]["min"] = min(prices)
    data["summary"]["price_range"]["max"] = max(prices)
    data["summary"]["price_range"]["avg"] = round(sum(prices) / len(prices), 2)
    data["summary"]["sales_volume_total"] = total_sales
    data["summary"]["revenue_total"] = total_revenue

def save_data(data, filename):
    """保存数据到JSON文件"""
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(filepath)

def load_history(category, platform):
    """加载历史数据进行对比"""
    base_dir = Path("/workspace/competitor-data")
    pattern = f"{category}_{platform}_*.json"

    files = sorted(base_dir.glob(pattern), reverse=True)
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def compare_with_history(current_data, history_data):
    """与历史数据对比"""
    if not history_data:
        return {"has_history": False, "changes": []}

    changes = []
    history_products = {p["name"]: p for p in history_data.get("products", [])}

    for product in current_data["products"]:
        name = product["name"]
        if name in history_products:
            hist = history_products[name]
            price_change = product["price"] - hist["price"]
            sales_change = product["sales_volume"] - hist["sales_volume"]

            if price_change != 0 or sales_change != 0:
                changes.append({
                    "product": name,
                    "price_change": price_change,
                    "price_change_pct": round(price_change / hist["price"] * 100, 2) if hist["price"] > 0 else 0,
                    "sales_change": sales_change,
                    "sales_change_pct": round(sales_change / hist["sales_volume"] * 100, 2) if hist["sales_volume"] > 0 else 0
                })

    return {"has_history": True, "changes": changes}

def generate_report(data, changes, platform):
    """生成Markdown格式分析报告"""
    timestamp = data["采集时间"]
    category = data["category"]

    report = f"""# {category} 品类竞品监控分析报告

**生成时间**: {timestamp}
**监控平台**: {platform.upper()}
**分析机构**: MiniMax Agent

---

## 一、市场概览

| 指标 | 数值 |
|------|------|
| 监控品类 | {category} |
| 监控平台 | {platform.upper()} |
| TOP产品数量 | {data['summary']['total_products']} |
| 价格区间 | ¥{data['summary']['price_range']['min']} - ¥{data['summary']['price_range']['max']} |
| 平均价格 | ¥{data['summary']['price_range']['avg']} |
| 总预估销量 | {data['summary']['sales_volume_total']:,} 件 |
| 总预估销售额 | ¥{data['summary']['revenue_total']:,.0f} |

"""

    # 价格与销量分析表格
    report += """## 二、价格与销量分析

| 排名 | 产品名称 | 品牌 | 价格 | 销量 | 预估销售额 | 预估ROI |
|------|----------|------|------|------|------------|---------|
"""

    for p in sorted(data["products"], key=lambda x: x["rank"]):
        report += f"| {p['rank']} | {p['name'][:20]} | {p['brand']} | ¥{p['price']} | {p['sales_volume']:,} | ¥{p['estimated_revenue']:,.0f} | {p['estimated_roi']} |\n"

    # TOP5深度分析
    report += """
## 三、TOP5产品深度分析

"""

    for i, p in enumerate(data["products"][:5], 1):
        report += f"""### 3.{i} {p['name']}

**基本信息**
- 品牌: {p['brand']}
- 型号: {p['model']}
- 价格: ¥{p['price']}
- 销量: {p['sales_volume']:,} 件
- 预估ROI: {p['estimated_roi']}

**主图分析**
- [待补充：主图风格描述]

**详情页结构**
- [待补充：详情页结构描述]

**投流特点**
- [待补充：投流策略推断]

"""

    # 波动预警
    if changes and changes.get("changes"):
        report += """## 四、波动预警

"""
        for change in changes["changes"]:
            if abs(change["price_change_pct"]) > 5 or abs(change["sales_change_pct"]) > 20:
                report += f"""### ⚠️ {change['product']}

- 价格变动: {'↑' if change['price_change'] > 0 else '↓'} ¥{abs(change['price_change'])} ({change['price_change_pct']}%)
- 销量变动: {'↑' if change['sales_change'] > 0 else '↓'} {abs(change['sales_change']):,} 件 ({change['sales_change_pct']}%)
- 建议: [待分析]

"""
    else:
        report += """## 四、波动预警

暂无历史数据对比，将作为下次监控的基准数据。

"""

    # 运营策略建议
    report += """## 五、运营策略建议

"""

    # 基于分析的策略建议
    high_roi_products = [p for p in data["products"] if p["estimated_roi"] > 2.0][:3]
    if high_roi_products:
        report += f"""### 5.1 高ROI产品特征分析

以下产品预估ROI较高，值得重点关注：
"""
        for p in high_roi_products:
            report += f"- **{p['name']}** (ROI: {p['estimated_roi']}) - 价格 ¥{p['price']}，销量 {p['sales_volume']:,}\n"

    avg_price = data["summary"]["price_range"]["avg"]
    mid_price_products = [p for p in data["products"] if abs(p["price"] - avg_price) < avg_price * 0.3][:3]

    if mid_price_products:
        report += f"""
### 5.2 价格带分布建议

市场主流价格带集中在 ¥{avg_price * 0.8:.0f} - ¥{avg_price * 1.2:.0f}，建议重点布局：

"""
        for p in mid_price_products:
            report += f"- ¥{p['price']} 价位: {p['name']}\n"

    report += """
### 5.3 主图优化建议

基于TOP5产品分析，建议：
1. [待补充：根据实际主图分析结果]
2. [待补充：根据实际详情页分析结果]
3. [待补充：根据实际投流特点分析]

### 5.4 投流策略建议

1. [待补充：基于ROI分析的投放建议]
2. [待补充：基于销量分析的投放建议]

---

## 六、数据来源

- 京东商城: https://search.jd.com/Search?keyword={category}
- 天猫商城: https://list.tmall.com/search_product.htm?q={category}

---

*报告由 MiniMax Agent 自动生成，如需详细信息请查阅对应JSON数据文件。*
"""

    return report

def main():
    """主函数演示"""
    # 示例数据结构
    data = create_data_structure()
    data["category"] = "手机"
    data["platform"] = "jd"
    data["采集时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 添加示例产品
    sample_products = [
        {"rank": 1, "name": "小米14 Pro", "brand": "小米", "model": "14 Pro", "price": 4999, "sales_volume": 50000, "shop_name": "小米官方旗舰店"},
        {"rank": 2, "name": "iPhone 15", "brand": "苹果", "model": "iPhone 15", "price": 5999, "sales_volume": 45000, "shop_name": "Apple官方旗舰店"},
        {"rank": 3, "name": "华为Mate 60", "brand": "华为", "model": "Mate 60", "price": 5499, "sales_volume": 40000, "shop_name": "华为官方旗舰店"},
    ]

    for product in sample_products:
        add_product(data, product)

    update_summary(data)

    # 保存数据
    filename = f"/workspace/competitor-data/{data['category']}_{data['platform']}_{datetime.now().strftime('%Y%m%d')}.json"
    saved_path = save_data(data, filename)
    print(f"数据已保存至: {saved_path}")

    # 生成报告
    report = generate_report(data, None, data["platform"])
    report_path = f"/workspace/competitor-data/{data['category']}_{data['platform']}_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"报告已生成至: {report_path}")

if __name__ == "__main__":
    main()
