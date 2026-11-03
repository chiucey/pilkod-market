#!/usr/bin/env python3
"""
用 mmx search query 补全 A 股策略周报的行业 + 资金面数据。

【2026-06-23 实测背景】
daily_report_v2.py 的 get_industry_data() / get_capital_flow_data() 只走 akshare 东财接口，
连续 3 天限流导致行业数据缺失。用户 2026-06-19 策略明确：
  - ✅ 首选：mmx search query（实测可拿到真实数据）
  - ❌ 禁止：akshare stock_board_industry_name_em 等东财接口

【用法】
  python3 scripts/mmx_search_data_completion.py <report_date>
  # 例：python3 scripts/mmx_search_data_completion.py 2026-06-23

【输出】
  每个 query 返回 markdown 摘要到 stdout（可直接 copy-paste 到报告）

【退避策略】
  - 每个 query 失败重试 2 次（间隔 2s）
  - 全部失败时打印 [数据缺失] + 用户可查的替代源
"""

import json
import subprocess
import sys
import time


# 5 个核心 query（覆盖报告需要的全部数据）
QUERIES = [
    {
        "key": "industry_change",
        "title": "[行业板块涨跌]",
        "q": "{date} A股 行业板块涨跌幅 申万一级",
        "extract": "industry_change",
    },
    {
        "key": "industry_rotation",
        "title": "[银行/券商/保险分化]",
        "q": "{date} A股 行业 涨幅 银行 券商 保险",
        "extract": "industry_rotation",
    },
    {
        "key": "limit_up_down",
        "title": "[涨停/跌停数量]",
        "q": "{date} A股 涨停数量 跌停数量",
        "extract": "limit_up_down",
    },
    {
        "key": "north_bound",
        "title": "[北向资金净流入]",
        "q": "{date} 北向资金 净流入 净卖出",
        "extract": "north_bound",
    },
    {
        "key": "main_capital",
        "title": "[主力资金行业净流入]",
        "q": "{date} A股 主力资金 行业 净流入",
        "extract": "main_capital",
    },
]


def run_mmx_search(query: str, max_retries: int = 2, timeout: int = 30) -> dict | None:
    """跑 mmx search query，失败重试。返回 organic 列表或 None。"""
    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                ["mmx", "search", "query", query, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                return None

            data = json.loads(result.stdout)
            organic = data.get("organic", [])
            if organic:
                return organic
            if attempt < max_retries:
                time.sleep(2)
                continue
            return None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            if attempt < max_retries:
                time.sleep(2)
                continue
            return None
    return None


def extract_today_results(organic: list, report_date: str, key: str) -> list[dict]:
    """从 organic 列表过滤出当日的条目（title 或 date 包含 report_date 或 "X月X日"）。"""
    # 把 2026-06-23 转成 "6月23日" 用于匹配
    try:
        y, m, d = report_date.split("-")
        cn_date = f"{int(m)}月{int(d)}日"
    except ValueError:
        cn_date = ""

    today_results = []
    for item in organic:
        title = item.get("title", "")
        date_str = item.get("date", "")
        # 命中条件：date 是当日 / title 含 "X月X日" / date 含 "2026-06-23"
        is_today = (
            date_str.startswith(report_date)
            or cn_date in title
            or report_date in date_str
        )
        if is_today:
            today_results.append(item)

    # 如果过滤后没结果，取前 5 条（fallback）
    return today_results[:5] if today_results else organic[:5]


def format_section(query_def: dict, organic: list | None, report_date: str) -> str:
    """格式化单个 query 的输出为 markdown section。"""
    section = f"\n## {query_def['title']}\n\n"
    section += f"**查询**: `mmx search query \"{query_def['q'].format(date=report_date)}\" --output json`\n\n"

    if not organic:
        section += "**[数据缺失]** mmx search 返回空。可能原因：\n"
        section += "  - mmx 服务暂不可用\n"
        section += "  - 关键词无匹配结果\n"
        section += "**[替代源]** Wind / Choice / 东方财富 APP（盘后 18:00-20:00 更新）\n"
        return section

    today_results = extract_today_results(organic, report_date, query_def["key"])

    section += f"**命中条目数**: {len(today_results)}（取前 5 条最相关）\n\n"

    for i, item in enumerate(today_results[:5], 1):
        title = item.get("title", "")
        snippet = item.get("snippet", "")[:400]  # 截断到 400 字
        date_str = item.get("date", "")
        link = item.get("link", "")

        section += f"### {i}. {title}\n"
        section += f"**日期**: {date_str}\n"
        if link:
            section += f"**链接**: {link}\n"
        section += f"\n{snippet}\n\n"

    return section


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/mmx_search_data_completion.py <report_date>", file=sys.stderr)
        print("Example: python3 scripts/mmx_search_data_completion.py 2026-06-23", file=sys.stderr)
        sys.exit(1)

    report_date = sys.argv[1]
    print(f"# mmx search 数据补全结果")
    print(f"# 报告日期: {report_date}")
    print(f"# 数据源: minimax-cli mmx search query (实测可用)")
    print()

    summary = {"total": len(QUERIES), "success": 0, "failed": 0}

    for query_def in QUERIES:
        q = query_def["q"].format(date=report_date)
        organic = run_mmx_search(q)
        section = format_section(query_def, organic, report_date)
        print(section)
        print("---")
        if organic:
            summary["success"] += 1
        else:
            summary["failed"] += 1

    print()
    print(f"# 汇总: {summary['success']}/{summary['total']} query 成功, {summary['failed']}/{summary['total']} 失败")
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
