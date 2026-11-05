---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5b507ee1e702166b9cde0bab2c17f2ec
    PropagateID: 5b507ee1e702166b9cde0bab2c17f2ec
    ReservedCode1: 304402203e101c1cbf7ca7cc8ff66986eaf9dd566256d7c89af0c441139d0cd873645edf02205954b119ec689bfa83276be8ecc9c6fe537fa2cafdd99eb6d21b1231fe9cb472
    ReservedCode2: 3046022100823a1f8ac376421bfd97799721bd42a6d27d5cef87a5325fc04e8eb72c1c9911022100a61ac6ea63e2a6115950a8b4c22db4c74d53f892802711db3c056e8cb98b63e1
description: A股企业价值分析技能。基于22本投资经典、15大分析技能、七层投资框架的全面分析。当用户要求分析股票、进行估值、查找合理买入区间、评估基本面、长期持有建议时触发。支持触发词：企业价值分析、估值、合理区间、基本面、长期持有、分析+股票名称/代码。
name: value-investor-suite
---

# A股企业价值分析套件

## 技能概述

本技能提供完整的A股企业价值分析服务，涵盖从宏观定位到长期持有的七层分析框架。用户只需提供股票名称或代码，即可获得结构化、专业化的投资分析报告。

## 触发条件

- 用户请求分析特定股票
- 用户询问股票估值或合理价格区间
- 用户评估股票基本面或长期投资价值
- 用户寻求买入/持有决策建议

**触发词示例**：
- "分析建设银行"
- "估值 601939"
- "企业价值分析 紫金矿业"
- "帮我看看贵州茅台的基本面"

## 输入要求

### 必需信息
- 股票名称或代码（6位数字，如 601939、000001）

### 可选配置（config）
| 配置项 | 类型 | 说明 |
|--------|------|------|
| eastmoney_api_key | string | 东方财富官方 Skills 接口 API Key |
| pdf_extractor_service | string | PDF提取服务：parseur/google_docai/azure |
| pdf_extractor_api_key | string | PDF服务API Key |
| webhook_url | string | 企业微信/钉钉Webhook地址 |

## 七层分析框架

### 第1层：宏观定位
- 康波周期阶段判断
- 政策方向解读
- 十五五规划主线匹配
- 地缘政治影响评估

### 第2层：行业分析
- 行业竞争格局（五力模型）
- 国产替代进度评估
- Agent/AI渗透率分析
- 反内卷信号识别

### 第3层：市场定位
- 当前估值历史分位
- 市场情绪指标
- 量化因子综合评分

### 第4层：财务估值
- EPS预测（2025E）
- DCF内在价值计算
- PB历史分位
- 股息率分析

### 第5层：买入决策
- 86体系综合评分
- 39体系状态判断
- 王子落难信号匹配
- 安全边际计算

### 第6层：心理控制
- 认知偏误检查
- 群体疯狂识别
- 逆向思考建议

### 第7层：长期持有
- 让跑的继续跑信号
- 定期复盘建议

## 输出格式

技能返回结构化报告，包含：
- 公司基本信息（名称、代码、当前股价）
- 七层框架各层分析结论
- 综合估值区间
- 投资建议（买入/持有/观察）
- 风险提示

## 执行流程

1. **解析输入**：从用户query中提取股票代码
2. **数据获取**：调用东方财富API获取实时行情和财务数据
3. **并行分析**：调用各技能模块进行专项分析
4. **结论整合**：综合各层分析生成最终报告

## 依赖模块

本技能调用以下配套技能：
- macro_data_skill：宏观数据分析
- valuation_automation：估值自动化
- research_report_miner：研报挖掘
- policy_decoder：政策解读
- commodity_geo_monitor：地缘商品监控
- earnings_season_scanner：财报季扫描
- anti_involution_screener：反内卷筛选
- fifteen_five_scanner：十五五规划扫描
- quant_ai_fusion：量化AI融合

## 注意事项

- 本分析仅供参考，不构成投资建议
- 投资决策需综合个人风险承受能力
- 建议配合PDF年报进行深度分析
