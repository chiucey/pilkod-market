#!/usr/bin/env python3
"""
持仓截图解析模块
使用AI视觉识别从券商App截图提取持仓数据
用法:
  python3 parse_holdings_screenshot.py <图片路径>
  python3 parse_holdings_screenshot.py --demo  # 用示例图片测试
"""

import sys
import re
import base64
import json
from typing import List, Optional

# 常见券商截图字段布局（用于辅助AI识别）
# 格式：字段名 -> 常见关键词
FIELD_KEYWORDS = {
    "stock_name": ["股票名称", "名称", "证券名称", "持仓证券"],
    "stock_code": ["代码", "证券代码", "股票代码"],
    "shares": ["持仓数量", "股票数量", "持有数量", "数量"],
    "cost": ["成本价", "买入成本", "持仓成本", "成本"],
    "current_price": ["当前价", "现价", "最新价", "市场价"],
    "market_value": ["市值", "持仓市值", "参考市值"],
    "profit": ["浮动盈亏", "盈亏", "持仓盈亏", "盈亏金额"],
    "profit_pct": ["盈亏比例", "收益率", "盈亏%"],
}

# 券商App特征（用于识别哪家券商）
BROKER_FEATURES = {
    "国泰海通": ["国泰海通", "gtahq"],
    "东方财富": ["东方财富", "eastmoney"],
    "同花顺": ["同花顺", "ths"],
    "中信建投": ["中信建投"],
    "华泰证券": ["涨乐财富通"],
    "中信证券": ["中信证券", "citics"],
    "广发证券": ["广发证券"],
    "招商证券": ["智远一户通"],
}

def parse_screenshot_ai(image_path: str) -> List[dict]:
    """
    通过AI多模态识别截图持仓
    返回标准持仓列表：[{"code": "sh600519", "name": "示例股票A", "shares": 500, "cost": 1800.0}, ...]
    """
    # 延迟导入，避免不需要时也加载
    try:
        from openclaw_images_understand import images_understand
    except ImportError:
        # fallback: 使用 images_understand MCP 工具
        return None

    prompt = """
你是一个专业的股票持仓数据提取专家。请从这张券商App截图（国泰海通证券持仓页面）中提取所有持仓股票的信息。

返回格式要求（严格JSON数组）：
[
  {
    "name": "示例股票A",
    "code": "600176",
    "market": "sh",
    "shares": 500,
    "cost": 1800.0,
    "current_price": 37.93,
    "profit": 4415.0,
    "profit_pct": 30.34
  }
]

提取规则：
1. code 必须是6位数字，如"600176"，不带sh/sz前缀
2. market 根据代码判断：6开头=sh，0/3开头=sz
3. shares 是持仓数量（股数）
4. cost 是成本价（元）
5. profit 是浮动盈亏金额（元）
6. profit_pct 是盈亏比例（%），正数是盈利，负数是亏损
7. 只提取"持仓"部分，不提取已清仓或现金部分
8. 如果某字段无法从图片读取，设为 null

请输出纯JSON数组，不要有其他文字。
"""
    
    result = images_understand(
        image_info=[{"file": image_path, "prompt": prompt}]
    )
    
    if not result or "error" in result:
        return []
    
    content = result.get("content", [])
    if not content:
        return []
    
    text = content[0].get("text", "")
    # 尝试解析JSON
    return extract_json_from_text(text)


def extract_json_from_text(text: str) -> List[dict]:
    """从AI返回的文本中提取JSON持仓数据"""
    # 尝试各种JSON包裹格式
    patterns = [
        r'\[\s*\{[^\]]+\}\s*\]',  # [...]
        r'\{[^{}]*\}',  # 单个对象
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
                if isinstance(data, list):
                    return normalize_holdings(data)
                elif isinstance(data, dict):
                    return normalize_holdings([data])
            except json.JSONDecodeError:
                continue
    return []


def normalize_holdings(raw_list: List[dict]) -> List[dict]:
    """
    统一持仓格式：
    - 添加市场前缀（sh/sz）
    - 确保字段完整
    """
    holdings = []
    for item in raw_list:
        code = str(item.get("code", "")).strip()
        if len(code) != 6:
            continue
        market = "sh" if code.startswith(("6", "9")) else "sz"
        holdings.append({
            "name": item.get("name", "").strip(),
            "code": f"{market}{code}",
            "market": market,
            "shares": int(item.get("shares") or 0),
            "cost": float(item.get("cost") or 0),
            "current_price": float(item.get("current_price") or 0),
            "profit": float(item.get("profit") or 0),
            "profit_pct": float(item.get("profit_pct") or 0),
        })
    return holdings


def holdings_to_json(holdings: List[dict]) -> str:
    """输出用于命令行的JSON字符串（单行）"""
    return json.dumps(holdings, ensure_ascii=False, separators=(',', ':'))


def print_holdings_table(holdings: List[dict]) -> None:
    """打印持仓表格"""
    if not holdings:
        print("❌ 未识别到持仓数据，请检查截图是否清晰")
        return
    print(f"\n📸 识别到 {len(holdings)} 只持仓：\n")
    print(f"  {'股票名称':<10}{'代码':<10}{'持股数':>8}{'成本价':>8}{'现价':>8}{'盈亏额':>10}{'盈亏率':>8}")
    print(f"  {'-'*70}")
    for h in holdings:
        sign = "+" if h["profit"] >= 0 else ""
        print(f"  {h['name']:<10}{h['code']:<10}{h['shares']:>8}{h['cost']:>8.2f}"
              f"{h['current_price']:>8.2f}{sign}{h['profit']:>9,.0f}"
              f"{sign}{h['profit_pct']:>7.2f}%")
    print(f"\n✅ 复制以下JSON给持仓顾问使用：")
    print(f"  {holdings_to_json(holdings)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法示例：")
        print("  python3 parse_holdings_screenshot.py /path/to/screenshot.jpg")
        print("  python3 parse_holdings_screenshot.py --demo")
        sys.exit(0)

    if sys.argv[1] == "--demo":
        print("ℹ️  演示模式：请提供券商App截图路径")
        print("   支持格式：JPG/PNG，截图需包含持仓列表（名称+代码+持股数+成本）")
        print("   示例：python3 parse_holdings_screenshot.py ~/持仓截图.png")
        return

    image_path = sys.argv[1]
    print(f"📸 正在解析截图：{image_path}")

    holdings = parse_screenshot_ai(image_path)
    if holdings is None:
        print("⚠️ AI解析功能不可用，请通过对话直接提供持仓信息")
        print("   格式示例：示例股票A sh600519 500股 成本1800.0元")
        return

    print_holdings_table(holdings)


if __name__ == "__main__":
    main()
