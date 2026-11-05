#!/usr/bin/env python3
"""
A股+港股实时行情抓取脚本
东方财富免费行情接口，无需认证
"""

import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

# API 基础地址
BASE_URL = "http://push2.eastmoney.com/api/qt/stock/get"

# 字段定义
FIELDS = "f43,f44,f45,f46,f47,f48,f57,f58,f169,f170"


def identify_stock_type(code: str) -> tuple:
    """
    识别股票类型并返回 secid
    """
    code = code.strip()

    if len(code) == 6 and code.isdigit():
        # A股: 0=上海, 1=深圳
        prefix = "0"
        return f"{prefix}.{code}", "A"
    elif len(code) == 5 and code.isdigit():
        # 港股
        return f"1.{code}", "HK"
    else:
        return None, None


def fetch_single_quote(code: str) -> Optional[Dict]:
    """
    获取单个股票行情
    """
    secid, market = identify_stock_type(code)

    if not secid:
        return {"code": code, "error": "Invalid code format"}

    url = f"{BASE_URL}?secid={secid}&fields={FIELDS}"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('data'):
            d = data['data']
            return {
                "code": d.get('f57', code),
                "name": d.get('f58', ''),
                "price": round(d.get('f43', 0) / 100, 2) if d.get('f43') else 0,
                "change": round(d.get('f169', 0) / 100, 2) if d.get('f169') else 0,
                "changePercent": round(d.get('f170', 0) / 100, 2) if d.get('f170') else 0,
                "high": round(d.get('f44', 0) / 100, 2) if d.get('f44') else 0,
                "low": round(d.get('f45', 0) / 100, 2) if d.get('f45') else 0,
                "open": round(d.get('f46', 0) / 100, 2) if d.get('f46') else 0,
                "volume": d.get('f47', 0),
                "amount": d.get('f48', 0),
                "market": market
            }
        else:
            return {"code": code, "error": "No data available"}

    except urllib.error.URLError as e:
        return {"code": code, "error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"code": code, "error": f"Error: {str(e)}"}


def fetch_batch_quotes(codes: List[str], max_workers: int = 5) -> List[Dict]:
    """
    批量获取股票行情
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(fetch_single_quote, code): code for code in codes}

        for future in as_completed(future_to_code):
            result = future.result()
            results.append(result)

    return results


def format_json_output(data: List[Dict]) -> str:
    """格式化 JSON 输出"""
    success_data = [item for item in data if "error" not in item]
    errors = [item for item in data if "error" in item]

    output = {
        "success": len(success_data) > 0,
        "count": len(success_data),
        "data": success_data
    }

    if errors:
        output["errors"] = errors

    return json.dumps(output, ensure_ascii=False, indent=2)


def format_table_output(data: List[Dict]) -> str:
    """格式化表格输出"""
    success_data = [item for item in data if "error" not in item]

    if not success_data:
        return "No valid data to display"

    header = "| 代码 | 名称 | 最新价 | 涨跌额 | 涨跌幅 | 成交量 | 成交额 |"
    separator = "|-----|------|-------|-------|-------|-------|-------|"

    rows = []
    for item in success_data:
        change_sign = "+" if item['change'] >= 0 else ""
        pct_sign = "+" if item['changePercent'] >= 0 else ""

        row = f"| {item['code']} | {item['name']} | {item['price']} | {change_sign}{item['change']} | {pct_sign}{item['changePercent']}% | {item['volume']:,} | {item['amount']:,} |"
        rows.append(row)

    return "\n".join([header, separator] + rows)


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fetch_quote.py <code1> [code2] ... [-json|-table]")
        sys.exit(1)

    # 解析参数
    codes = []
    output_format = "json"

    for arg in sys.argv[1:]:
        if arg in ['-json', '--json']:
            output_format = "json"
        elif arg in ['-table', '--table']:
            output_format = "table"
        else:
            codes.append(arg)

    if not codes:
        print("Error: No stock codes provided")
        sys.exit(1)

    # 获取数据
    results = fetch_batch_quotes(codes)

    # 输出结果
    if output_format == "table":
        print(format_table_output(results))
    else:
        print(format_json_output(results))


if __name__ == "__main__":
    main()
