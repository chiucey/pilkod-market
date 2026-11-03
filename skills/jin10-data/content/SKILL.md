---
name: jin10-data
description: 金十数据财经资讯 MCP 工具技能。当用户问黄金价格、原油报价、美联储动态、财经日历、实时快讯、资讯搜索等财经数据时触发。直接调用金十数据 MCP HTTP 接口获取实时行情、K线、快讯、资讯和财经日历数据。
---

# 金十数据财经 MCP Skill

## 触发场景

当用户问以下内容时触发：
- "黄金现在多少钱"、"原油价格"、"白银报价"
- "美联储最新动态"、"央行决议"
- "今天的财经日历"、"本周重要数据"
- "最新快讯"、"资讯搜索"、"关于通胀的新闻"
- "比特币行情"、"外汇报价"

## 工作原理

通过 Python 脚本直接调用金十数据 MCP HTTP 接口（`https://mcp.jin10.com/mcp`），
每次调用独立发请求，不依赖会话状态。

## 常用工具调用

### 📈 实时行情（常用品种）
```bash
python3 /workspace/skills/jin10_mcp_final.py quote XAUUSD
python3 /workspace/skills/jin10_mcp_final.py quote USOIL
python3 /workspace/skills/jin10_mcp_final.py quote EURUSD
python3 /workspace/skills/jin10_mcp_final.py quote USDJPY
python3 /workspace/skills/jin10_mcp_final.py quote COPPER
```

### 📊 K线数据
```bash
python3 /workspace/skills/jin10_mcp_final.py kline XAUUSD 10
python3 /workspace/skills/jin10_mcp_final.py kline USOIL 20
```

### 📰 最新快讯
```bash
python3 /workspace/skills/jin10_mcp_final.py flash
```

### 🔍 搜索快讯
```bash
python3 /workspace/skills/jin10_mcp_final.py search_flash 美联储
python3 /workspace/skills/jin10_mcp_final.py search_flash 黄金
```

### 📋 财经日历
```bash
python3 /workspace/skills/jin10_mcp_final.py calendar
```

### 📄 资讯列表
```bash
python3 /workspace/skills/jin10_mcp_final.py news
```

### 🔍 搜索资讯
```bash
python3 /workspace/skills/jin10_mcp_final.py search_news 通胀
```

## Python 调用器

路径: `/workspace/skills/jin10_mcp_final.py`

用法: `python3 /workspace/skills/jin10_mcp_final.py <cmd> [args]`

命令列表:
- `quote <code>` - 实时行情，例如 `quote XAUUSD`
- `kline <code> <count>` - K线数据，例如 `kline XAUUSD 10`
- `flash [cursor]` - 最新快讯列表
- `search_flash <keyword>` - 搜索快讯
- `calendar` - 财经日历
- `news [cursor]` - 最新资讯列表
- `search_news <keyword> [cursor]` - 搜索资讯
- `news_detail <id>` - 资讯详情

## 输出格式

解析后按以下格式返回：

**实时行情：**
```
🌟 [品种名称] 实时行情
价格: xxx.xx USD
涨跌: +x.xx (+x.xx%)
最高: xxx.xx | 最低: xxx.xx
成交量: xxx
时间: xxxx-xx-xx xx:xx
```

**快讯/资讯：**
```
📰 [标题]
[摘要内容]
时间: xxxx-xx-xx xx:xx
来源: 金十数据
```

**财经日历：**
```
📅 财经日历 - [日期]
• [事件名称]
  前值: x.xx | 预期: x.xx | 今值: x.xx
  影响: [影响说明]
```

## 常用品种代码

| 代码 | 品种 |
|------|------|
| XAUUSD | 现货黄金 |
| XAGUSD | 现货白银 |
| USOIL | WTI原油 |
| UKOIL | 布伦特原油 |
| COPPER | 现货铜 |
| USDJPY | 美元/日元 |
| EURUSD | 欧元/美元 |
| USDCNH | 美元/人民币 |
| BTCUSD | 比特币 |

## 注意事项

- 报价工具返回 `data.close`（价格）、`data.ups_percent`（涨跌%）
- 快讯/资讯列表返回 `data.items` 数组，分页用 `data.next_cursor`
- 财经日历返回 `data` 数组，每项含 `title / previous / consensus / actual / affect_txt`
- MCP 返回 SSE 格式，解析时提取 `data:` 开头的 JSON 行