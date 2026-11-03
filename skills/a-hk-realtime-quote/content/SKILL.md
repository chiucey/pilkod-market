---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1a01e6d8a55d57841f76c5e416796135
    PropagateID: 1a01e6d8a55d57841f76c5e416796135
    ReservedCode1: 3045022100f1f7e08d53a5ed314a948eaf269c5a44986142dee126cddfd21208327d18fd8e0220229bb7dc4fd21db99e11466eea0981cdc4fe1bee64bf271bf68e8f66aebedcd3
    ReservedCode2: 3045022023d90081fb67f9c3bb6eeb78c473be618ce128b56fe51f4861b2c6cda42b1ea9022100ec27f084aa26cab639016eff965d643176348b9c2e7abc91e8c5070030aba9a8
description: A股和港股实时行情抓取工具。当用户要求查询股票实时行情、股票价格、涨跌情况、成交量、成交额时使用。触发短语包括："查一下[股票代码]"、"[股票]实时行情"、"股票报价"、"A股行情"、"港股行情"、"批量查询股票"、"查询[代码1][代码2]"、"股票数据"、"实时价格"、"[输出格式]格式股票数据"（JSON/表格）。
name: a-hk-realtime-quote
---

# A股 + 港股实时行情抓取

## 功能说明

支持查询 A 股（6 位代码）和港股（5 位代码）的实时行情数据，包括：
- 实时价格
- 涨跌额、涨跌幅
- 成交量、成交额
- 支持批量查询多个股票
- 支持 JSON 和表格两种输出格式

## 工作流程

### 1. 解析股票代码

接收用户输入的股票代码，进行类型判断：

| 股票类型 | 代码特征 | 市场标识 |
|---------|---------|---------|
| A 股 | 6 位数字，以 6/0/3 开头 | `0.` 前缀 |
| 港股 | 5 位数字 | `1.` 前缀 |

**代码示例：**
- `600519` → 识别为 A 股，secid = `0.600519`
- `0700` → 识别为港股，secid = `1.00700`
- `000001` → 识别为 A 股，secid = `0.000001`

### 2. 调用东方财富行情 API

使用东方财富免费行情接口获取实时数据：

```
http://push2.eastmoney.com/api/qt/stock/get?secid={市场代码}.{股票代码}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f107,f169,f170
```

**字段映射：**
| 字段 | 说明 |
|-----|------|
| f43 | 最新价（分→元） |
| f44 | 最高价 |
| f45 | 最低价 |
| f46 | 今开价 |
| f47 | 成交量（手） |
| f48 | 成交额（元） |
| f57 | 股票代码 |
| f58 | 股票名称 |
| f169 | 涨跌额 |
| f170 | 涨跌幅（%） |

### 3. 处理批量查询

- 支持多个股票代码同时查询
- 使用并发请求提升查询效率
- 收集所有结果后统一格式化输出

### 4. 格式化输出

根据用户指定格式输出：

**JSON 格式：**
```json
{
  "success": true,
  "data": [
    {
      "code": "600519",
      "name": "贵州茅台",
      "price": 1688.00,
      "change": 15.20,
      "changePercent": 0.91,
      "high": 1695.00,
      "low": 1670.50,
      "open": 1673.00,
      "volume": 25600,
      "amount": 430000000
    }
  ]
}
```

**表格格式：**
| 代码 | 名称 | 最新价 | 涨跌额 | 涨跌幅 | 成交量(手) | 成交额(元) |
|-----|------|-------|-------|-------|-----------|-----------|
| 600519 | 贵州茅台 | 1688.00 | +15.20 | +0.91% | 25,600 | 430,000,000 |

## 执行脚本

创建 `scripts/fetch_quote.py` 执行核心抓取逻辑：

```python
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
</script>

## 使用示例

### 单个股票查询
```
输入：查一下 600519 的实时行情
输出：返回贵州茅台的 JSON 数据或表格
```

### 批量查询
```
输入：查询 600519 0700 000001 的行情，JSON 格式
输出：返回多个股票的 JSON 数据
```

### 表格输出
```
输入：600519 0700 行情，表格格式
输出：返回格式化表格
```

## 注意事项

1. **网络要求**：需要能访问东方财富服务器
2. **频率限制**：避免短时间内大量请求
3. **数据延迟**：免费接口存在 1-3 秒延迟
4. **港股代码**：需补齐 5 位，如 0700 实际为 00700
