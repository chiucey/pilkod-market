---
name: daily-fund-report
description: 每日基金收益报表生成与飞书推送。当用户要求生成基金收益报告、查看基金每日收益、分析持仓收益、设置基金定投报表，或需要每日自动推送基金收益到飞书时使用。
---

# 每日基金收益报表技能

## 功能概述

自动化获取基金净值数据，分析持仓收益，生成美观的飞书消息卡片并定时推送。

## 核心流程

### 1. 数据获取

**数据源**：天天基金网（东方财富）公开API

**获取方式**：
```python
# 基金净值实时查询
url = "https://fundgz.1234567.com.cn/js/{fund_code}.js?rt=1700000000"
# 返回JSON格式：净值、估算值、日增长率
```

### 2. 持仓配置

用户需提供持仓数据，格式为 `assets/portfolio.json`：

```json
{
  "holdings": [
    {
      "code": "000001",
      "name": "示例基金A",
      "shares": 1000,
      "cost": 1.5000,
      "buy_date": "2024-01-15"
    }
  ],
  "total_investment": 1500.00
}
```

### 3. 收益分析

计算指标：
- **当日收益** = (当前净值 - 昨日净值) × 份额
- **累计收益** = (当前净值 - 成本价) × 份额
- **收益率** = 收益 / 成本 × 100%
- **持仓分布** = 各基金市值占比

### 4. 飞书消息推送

**消息类型**：富文本消息卡片（Interactive Card）

**消息格式**：
```
📊 每日基金收益报表
📅 2024年12月20日

💰 总资产：¥12,345.67
📈 今日收益：+¥123.45 (+1.01%)
📊 累计收益：+¥1,234.56 (+10.02%)

【持仓明细】
1. 示例基金A
   持有份额：1000份
   今日收益：+¥12.34
   累计收益：+¥123.45
   收益率：+8.23%
...
```

### 5. 定时任务配置

使用 `create_cron_job` 工具设置每日执行：

```javascript
{
  "job_title": "每日基金收益报表",
  "job_instruction": "执行 /workspace/temp-skills/daily-fund-report/scripts/generate_report.py 生成基金收益报表并推送到飞书",
  "cron_expression": "0 16 * * 1-5"  // 每周一至周五16:00执行
}
```

## 使用方式

### 首次设置

1. 准备持仓数据文件 `portfolio.json`
2. 配置飞书Webhook地址（存入环境变量或配置文件）
3. 测试手动执行一次

### 手动执行

```bash
python scripts/generate_report.py --portfolio assets/portfolio.json --feishu-webhook "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

### 查看历史报表

报表数据保存在 `data/reports/` 目录，按日期归档。

## 错误处理

- **净值获取失败**：重试3次，间隔5秒，超时后发送告警消息
- **Webhook发送失败**：记录日志，保留报表文件供手动补发
- **无持仓数据**：发送提示消息，要求用户配置持仓

## 依赖

- Python 3.8+
- requests（HTTP请求）
- pandas（数据分析）
- json（配置读取）

## 文件结构

```
daily-fund-report/
├── SKILL.md                    # 本文件
├── _meta.json                   # 元数据
├── scripts/
│   ├── generate_report.py      # 主报告生成脚本
│   ├── fetch_fund_data.py       # 基金数据获取
│   ├── analyze_returns.py       # 收益分析
│   └── send_feishu.py           # 飞书推送
├── references/
│   └── fund_data_source.md     # 数据源文档
└── assets/
    ├── portfolio_template.json  # 持仓模板
    └── feishu_card_template.json # 消息卡片模板
