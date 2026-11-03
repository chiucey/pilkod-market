---
name: report-generator
description: 【报告生成器】投资报告生成和预警监控技能。当用户要求生成股票投研报告、撰写分析报告、导出报告、设置价格预警、条件监控提醒等任务时使用。
---

# 报告生成与预警技能

## 模块一：报告生成

### generate_report

将分析结果汇总，生成自然语言投研报告。

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| title | str | 是 | 报告标题 |
| stocks | list[str] | 是 | 股票代码列表 |
| sections | list[str] | 否 | 报告章节 |
| output_format | str | 否 | 输出格式：markdown/html/pdf/json (默认: markdown) |
| template | str | 否 | 报告模板 |
| language | str | 否 | 报告语言：zh/en (默认: zh) |

**支持的报告章节：**

| 章节 | 说明 | 包含内容 |
|-----|------|---------|
| overview | 概览 | 市场环境、选股逻辑、整体评级 |
| fundamentals | 基本面 | 财务数据、估值分析、盈利能力 |
| technical | 技术面 | 趋势分析、指标信号、形态识别 |
| risk | 风险 | 风险评估、回撤分析、黑天鹅风险 |
| recommendation | 建议 | 操作建议、目标价位、止损位置 |

**预定义模板：**

1. **daily_brief**: 每日简报 - 快速市场概况
2. **weekly_review**: 周度复盘 - 一周走势回顾
3. **stock_deep_dive**: 深度研究 - 单股票全面分析
4. **portfolio_review**: 组合回顾 - 多股票组合评估

## 模块二：预警监控

### set_alert

创建实时监控条件，当条件满足时推送预警。

**条件类型：**

| 类型 | 参数 | 说明 |
|-----|------|------|
| price_change | threshold | 价格变动百分比 |
| volume | threshold | 成交量倍数 |
| technical | indicator_signal | 技术指标信号 |
| news | keywords | 新闻关键词触发 |

**条件示例：**

```python
{
  "conditions": [
    {"type": "price_change", "threshold": 5, "direction": "up"},
    {"type": "volume", "threshold": 2.0}
  ],
  "alert_name": "贵州茅台异动预警",
  "notification_channels": ["push", "email", "webhook"]
}
```

### get_alerts

查询已设置的预警列表。

### delete_alert

删除指定预警。

## 合规声明

> ⚠️ 预警信息基于预设条件自动触发，仅供参考。投资者应根据实际市场情况自主判断。