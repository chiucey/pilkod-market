---
name: jin10-mcp
description: 金十数据财经 MCP 服务调用技能。当用户问黄金价格、原油报价、美联储动态、财经日历、实时快讯、资讯搜索等财经数据时触发。使用标准 MCP JSON-RPC 2.0 协议调用金十数据 MCP 服务。
---

# 金十数据 MCP Skill

## 触发场景

- 用户问"黄金现在多少钱"、"原油价格"、"美联储最新动态"
- 用户问"今天有什么重要数据"、"财经日历"
- 用户问"最新快讯"、"资讯搜索"、"关于通胀的新闻"
- 任何需要实时行情、K线数据、快讯、资讯、财经日历的场景

## 调用流程

### 第一步：初始化（仅首次启动时调用一次）

```bash
bash /workspace/skills/jin10-mcp.sh init
```

返回 `protocolVersion: "2025-11-25"` 则成功。

### 第二步：发送初始化完成通知（仅调用一次）

```bash
bash /workspace/skills/jin10-mcp.sh notify
```

### 第三步：列工具（可选，用于发现可用工具）

```bash
bash /workspace/skills/jin10-mcp.sh list
```

### 第四步：调用具体工具

#### 📈 实时行情
```bash
bash /workspace/skills/jin10-mcp.sh call get_quote '{"code":"XAUUSD"}'
bash /workspace/skills/jin10-mcp.sh call get_quote '{"code":"USOIL"}'
```

#### 📊 K线数据
```bash
# 获取最近10根K线
bash /workspace/skills/jin10-mcp.sh call get_kline '{"code":"XAUUSD","count":10}'
```

#### 📰 最新快讯
```bash
bash /workspace/skills/jin10-mcp.sh call list_flash '{"cursor":""}'
```

#### 🔍 搜索快讯
```bash
bash /workspace/skills/jin10-mcp.sh call search_flash '{"keyword":"美联储"}'
```

#### 📋 最新资讯
```bash
bash /workspace/skills/jin10-mcp.sh call list_news '{"cursor":""}'
```

#### 🔍 搜索资讯
```bash
bash /workspace/skills/jin10-mcp.sh call search_news '{"keyword":"通胀","cursor":""}'
```

#### 📄 资讯详情
```bash
bash /workspace/skills/jin10-mcp.sh call get_news '{"id":"资讯ID"}'
```

#### 📅 财经日历
```bash
bash /workspace/skills/jin10-mcp.sh call list_calendar '{}'
```

## 数据解析规范

- **优先读取** `result.structuredContent` 字段
- `result.content` 仅作为可读文本补充，不作为主要解析来源
- 分页参数统一使用 `cursor`，响应中用 `data.next_cursor`，更多数据用 `data.has_more`

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

## 输出格式

解析后按以下格式返回给用户：

**实时行情格式：**
```
🌟 [品种名称] 实时行情
价格: xxx.xx
涨跌: +x.xx (+x.xx%)
时间: xxxx-xx-xx xx:xx
```

**快讯/资讯格式：**
```
📰 [标题]
[摘要/内容摘要]
时间: xxxx-xx-xx xx:xx
来源: 金十数据
```

**财经日历格式：**
```
📅 财经日历 - [日期]
• [事件名称]
  前值: x.xx  预期: x.xx  今值: x.xx
  影响: [影响说明]
```