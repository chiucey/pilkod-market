#!/usr/bin/env python3
"""Fetch A股 market breadth (涨跌家数) from EastMoney hsgtV2.html via browser.

For 15:05 close cron tasks when push2.eastmoney.com is 100% down (per skill §35/§41).
This script uses Playwright sync API to drive a headless browser.

Usage:
    python3 scripts/fetch_market_breadth.py
    python3 scripts/fetch_market_breadth.py --output /tmp/market_breadth.json

Output (JSON to stdout or file):
    {
        "sh_up": 482,
        "sh_flat": 22,
        "sh_down": 1132,
        "sz_up": 506,
        "sz_flat": 21,
        "sz_down": 1342,
        "total_up": 988,
        "total_down": 2474,
        "total_flat": 43,
        "total": 3505,
        "bearish_pct": 0.7058,
        "hsgt_sh_status": "收盘, 额度充足 (北向净买额 18:00 后盘后公告)",
        "hsgt_sz_status": "收盘, 额度充足 (北向净买额 18:00 后盘后公告)",
        "south_net_sh_yi": -10.87,
        "south_net_sz_yi": -18.32,
        "south_net_total_yi": -29.19,
        "sh_index": "4120.28 +0.23%",
        "sz_index": "16344.08 +1.82%",
        "fetch_time": "2026-06-25 15:08"
    }

6/25 实战实测: 沪市 482/22/1132 + 深市 506/21/1342 → 988/43/2474 → bearish_pct 70.58%
6/24 实战实测: 沪市 ~422/~18/~1196 + 深市 ~440/~21/~1301 → ~862/39/2497 → bearish_pct 72.39%

替代方案:
- push2 涨/跌统计接口 (fs=m:0+s:3,m:1+s:2) — 15:00+ 100% 失败 (skill §35)
- 浏览器抓 data.eastmoney.com/bkzj/hy.html — 只能拿行业板块, 拿不到市场宽度 (skill §40)
- 浏览器抓 quote.eastmoney.com/ztb/ — 只能拿涨跌停 + 赚钱效应, 拿不到涨/跌家数

本脚本的 data.eastmoney.com/hsgt/hsgtV2.html 是唯一稳定源 (skill §22/§23 实战验证)

依赖:
- pip install playwright
- playwright install chromium
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path


def parse_breadth_table(table_rows: list) -> dict:
    """Parse the hsgtV2.html table rows to extract breadth data.

    Expected row format (per 6/25 实战):
    ["陆股通", "港>沪", "收盘", "<领涨股>", "-", "额度充足",
     "482", "22", "1132", "<相关指数>", "<涨跌幅>"]
    ["", "港>深", "收盘", "<领涨股>", "-", "额度充足",
     "506", "21", "1342", "<相关指数>", "<涨跌幅>"]

    Returns dict with sh_*/sz_* fields.
    """
    result = {
        "sh_up": None, "sh_flat": None, "sh_down": None,
        "sz_up": None, "sz_flat": None, "sz_down": None,
        "south_net_sh_yi": None, "south_net_sz_yi": None,
        "sh_index": None, "sz_index": None,
    }

    for row in table_rows:
        # Skip header rows
        if not row or row[0] in ("类型", "港股通", "陆股通") and len(row) > 1 and row[1] not in ("沪>港", "深>港", "港>沪", "港>深"):
            continue

        # 港股通 (南向) rows
        if row[0] == "港股通" and len(row) > 8:
            try:
                # 沪>港: 净买额, 成交总额, 上涨, 持平, 下跌
                net_str = row[3].replace("亿元", "").replace(",", "")
                net = float(net_str) if net_str and net_str != "-" else None
                if row[1] == "沪>港":
                    result["south_net_sh_yi"] = net
                elif row[1] == "深>港":
                    result["south_net_sz_yi"] = net
            except (ValueError, IndexError):
                pass

        # 陆股通 rows (港>沪 / 港>深) — 这是涨跌家数来源
        if row[0] == "陆股通" and len(row) >= 11:
            try:
                up = int(row[6])
                flat = int(row[7])
                down = int(row[8])
                index_str = f"{row[9]} {row[10]}"
                if row[1] == "港>沪":
                    result["sh_up"] = up
                    result["sh_flat"] = flat
                    result["sh_down"] = down
                    result["sh_index"] = index_str
                elif row[1] == "港>深":
                    result["sz_up"] = up
                    result["sz_flat"] = flat
                    result["sz_down"] = down
                    result["sz_index"] = index_str
            except (ValueError, IndexError):
                pass

    # 合并 + 计算 bearish_pct
    if result["sh_up"] is not None and result["sz_up"] is not None:
        result["total_up"] = result["sh_up"] + result["sz_up"]
        result["total_flat"] = (result["sh_flat"] or 0) + (result["sz_flat"] or 0)
        result["total_down"] = result["sh_down"] + result["sz_down"]
        result["total"] = result["total_up"] + result["total_flat"] + result["total_down"]
        result["bearish_pct"] = round(result["total_down"] / result["total"], 4) if result["total"] else None

    if result["south_net_sh_yi"] is not None and result["south_net_sz_yi"] is not None:
        result["south_net_total_yi"] = round(result["south_net_sh_yi"] + result["south_net_sz_yi"], 2)

    return result


def fetch_via_playwright(headless: bool = True) -> dict:
    """Drive Chromium browser to fetch hsgtV2.html and extract breadth table."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page.goto("https://data.eastmoney.com/hsgt/hsgtV2.html", wait_until="domcontentloaded", timeout=30000)
        # Wait for the breadth table to load
        page.wait_for_selector("table tr", timeout=15000)
        time.sleep(2)  # Buffer for late-rendering data

        # Extract all table rows
        rows_json = page.evaluate("""
            (() => {
                const rows = document.querySelectorAll('table tr');
                const result = [];
                rows.forEach((row) => {
                    const cells = row.querySelectorAll('td, th');
                    if (cells.length > 0) {
                        const cellTexts = Array.from(cells).map(c => c.innerText.trim().slice(0, 50));
                        result.push(cellTexts);
                    }
                });
                return result;
            })()
        """)

        browser.close()

    breadth = parse_breadth_table(rows_json)

    if breadth.get("sh_up") is None or breadth.get("sz_up") is None:
        # Diagnostic: dump rows for debugging
        print("WARN: failed to parse breadth. Raw table rows:", file=sys.stderr)
        for r in rows_json[:15]:
            print(f"  {r}", file=sys.stderr)

    breadth["fetch_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return breadth


def fetch_via_curl_fallback() -> dict:
    """Curl fallback — sometimes the page HTML is more parseable than JS rendering."""
    import subprocess
    import re

    result = {"sh_up": None, "sh_flat": None, "sh_down": None,
              "sz_up": None, "sz_flat": None, "sz_down": None,
              "south_net_sh_yi": None, "south_net_sz_yi": None,
              "sh_index": None, "sz_index": None,
              "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    try:
        # Use curl with referer
        html = subprocess.run(
            ["curl", "-s", "-L",
             "-H", "User-Agent: Mozilla/5.0",
             "-H", "Referer: https://data.eastmoney.com/",
             "--connect-timeout", "10", "-m", "30",
             "https://data.eastmoney.com/hsgt/hsgtV2.html"],
            capture_output=True, text=True, timeout=35
        ).stdout

        # Try to find 港>沪 / 港>深 pattern with breadth numbers
        # The page is mostly JS-rendered, so this often fails — playwright is preferred
        sh_match = re.search(r'港>沪.*?(\d{3,4}).*?(\d{1,3}).*?(\d{3,4})', html, re.DOTALL)
        sz_match = re.search(r'港>深.*?(\d{3,4}).*?(\d{1,3}).*?(\d{3,4})', html, re.DOTALL)
        if sh_match:
            result["sh_up"] = int(sh_match.group(1))
            result["sh_flat"] = int(sh_match.group(2))
            result["sh_down"] = int(sh_match.group(3))
        if sz_match:
            result["sz_up"] = int(sz_match.group(1))
            result["sz_flat"] = int(sz_match.group(2))
            result["sz_down"] = int(sz_match.group(3))

        if result["sh_up"] is not None and result["sz_up"] is not None:
            result["total_up"] = result["sh_up"] + result["sz_up"]
            result["total_flat"] = (result["sh_flat"] or 0) + (result["sz_flat"] or 0)
            result["total_down"] = result["sh_down"] + result["sz_down"]
            result["total"] = result["total_up"] + result["total_flat"] + result["total_down"]
            result["bearish_pct"] = round(result["total_down"] / result["total"], 4) if result["total"] else None

    except Exception as e:
        print(f"WARN: curl fallback failed: {e}", file=sys.stderr)

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch A股 market breadth from EastMoney hsgtV2.html")
    parser.add_argument("--output", "-o", help="Output JSON file path (default: stdout)")
    parser.add_argument("--method", choices=["playwright", "curl", "auto"], default="auto",
                        help="Fetch method (default: auto — playwright first, curl fallback)")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful mode (for debugging)")
    args = parser.parse_args()

    breadth = None
    if args.method in ("playwright", "auto"):
        try:
            breadth = fetch_via_playwright(headless=not args.headful)
        except Exception as e:
            print(f"WARN: playwright fetch failed: {e}", file=sys.stderr)
            if args.method == "auto":
                breadth = fetch_via_curl_fallback()
    elif args.method == "curl":
        breadth = fetch_via_curl_fallback()

    if not breadth or breadth.get("sh_up") is None:
        print("ERROR: failed to fetch market breadth from any method", file=sys.stderr)
        sys.exit(1)

    # Output
    output = json.dumps(breadth, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote breadth to {args.output}", file=sys.stderr)
        # Also print summary to stderr
        print(f"  bearish_pct: {breadth.get('bearish_pct')}", file=sys.stderr)
        print(f"  total: {breadth.get('total_up')} up / {breadth.get('total_flat')} flat / {breadth.get('total_down')} down", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
