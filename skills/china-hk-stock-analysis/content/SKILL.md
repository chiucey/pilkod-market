---
name: china-hk-stock-analysis
description: "This skill should be used when the user asks to analyze a specific A-share or HK stock (e.g., 美的集团, 腾讯控股, 章源钨业); compare multiple stocks (e.g., 对比美的和格力); screen stocks by criteria (e.g., 帮我筛选家电行业高股息股票); get stock valuation, PE/PB/PEG analysis, DCF intrinsic value; perform technical analysis, RSI/MACD/trend analysis; get buy/sell rating, target price, investment recommendation; assess stock risk, financial health, moat rating; backtest trading strategies or scoring models. 机构级股票诊断神器 v2.8 | 专注A股/港股 | 8维度量化评分体系（含投行预期维度）| 投行标准模块（分析师预期/盈利预测/业务拆解/催化剂）| 多数据源交叉验证（Baostock优先/腾讯财经/akshare）| DCF内在价值计算 | 目标价预测 | 投资评级 | 回测框架 | 适合价值投资者、成长股猎手、短线交易者"
---

# A股港股个股深度分析技能 v2.8

## 简介

本技能为投资者提供专业、客观、深度的股票分析服务，专注A股和港股市场。

**核心功能**:
- 8维度量化评分体系（估值/基本面/技术/情绪/宏观/行业/风险/投行预期）
- 投行标准研报模块（分析师预期/盈利预测/业务拆解）
- 多数据源交叉验证（Baostock/akshare/腾讯财经）
- 回测框架验证评分有效性（含三层回测结构）
- 个股操作建议 + 稳健优化（参数区间 + 过拟合检测）
- DCF内在价值计算
- 持续监测与预警

---

## 文档结构

```
SKILL.md (主入口)
├── references/
│   ├── 01_framework.md       # 核心理念、8阶段框架、输入参数
│   ├── 02_data_sources.md    # 数据来源、分层架构、时效性
│   ├── 03_scoring.md         # 8维度量化评分体系(含投行预期)
│   ├── 04_monitoring.md       # 回测能力、持续监测、预警
│   ├── 05_comparison.md      # 多票对比、筛选条件
│   ├── 06_report_export.md    # 研报生成、导出格式
│   ├── 07_cross_validation.md # 多数据源交叉验证体系
│   └── 08_operation_backtest.md # 个股操作建议 + 回测 + 稳健优化
├── output_structure.md       # 报告输出结构模板(v2.8)
├── backtest_framework.md      # 量化回测框架(v2.0)
└── meta.json               # 技能元数据
```

---

## 快速开始

### 基本分析

```
用户: 帮我分析下美的集团
AI: 使用 Baostock 数据源获取美的集团(000333.SZ)完整分析
    按照 output_structure.md 格式输出完整报告
```

### 对比分析

```
用户: 对比下美的和格力
AI: 同时分析两只股票，按 references/05_comparison.md 格式输出对比报告
```

### 筛选股票

```
用户: 帮我筛选家电行业高股息股票
AI: 按预设筛选条件执行，输出符合条件的股票列表
```

### 设置监测

```
用户: 设置美的集团的监测预警
AI: 按 references/04_monitoring.md 配置监测任务
```

### 导出报告

```
用户: 生成这份分析的Word报告
AI: 按 references/06_report_export.md 格式导出
```

---

## 支持的市场

| 市场 | 代码格式 | 交易时间 | 货币 | 主要数据源 |
|------|----------|----------|------|------------|
| A股 | 600519.SH, 000001.SZ | 09:30-15:00北京时间 | CNY | **Baostock**(主), akshare, 腾讯财经 |
| 港股 | 0700.HK, 9988.HK | 09:30-16:00香港时间 | HKD | akshare, AASTOCKS, 腾讯财经, 东方财富 |

---

## 报告输出

> **完整报告格式**: 请参考 [output_structure.md](output_structure.md)

每个分析报告必须包含:
- 报告头部（基本信息）
- 执行摘要（核心结论）
- 8维度评分（量化计算）
- 投行标准模块（分析师预期/盈利预测等）
- 回测信号数据

---

## 数据质量要求

- 所有关键结论必须标注数据来源
- 争议性观点需标注多空双方论据
- 引用可信度评级（A=权威/B=可靠/C=一般/D=需验证）
- 数据必须标注新鲜度（采集时间）

---

## 免责声明

本分析基于公开数据和量化模型，仅供参考，不构成投资建议。投资有风险，决策需谨慎。

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.8 | 2026-04-20 | 去除美股,专注A股/港股;强化数据来源标注;添加数据校验模块;改进评分计算透明度 |
| v2.7 | 2026-04-12 | 重构第五部分为完整回测优化输出;含三层回测+稳健优化结果 |
| v2.6 | 2026-04-12 | 合并3.8与第五部分为统一8维度;添加权重设定依据说明 |
| v2.5 | 2026-04-12 | 投行预期整合为第8维度,8维度统一评分体系形成 |
| v2.4 | 2026-04-12 | 模块化拆分(7个模块文件),投行标准模块,量化评分体系,回测接口 |
| v2.3 | 2026-04-12 | Baostock数据源集成 |
| v2.2 | 2026-04-12 | 回测能力、持续监测、多票对比、研报导出 |
| v2.1 | 2026-04-12 | 数据保障体系增强、信号评级系统、护城河评级 |
| v2.0 | 2026-04-09 | 维度评分体系 |
| v1.0 | 2026-04-09 | 初始版本 |
