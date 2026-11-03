---
name: wall-street-quant-team
description: 华尔街级AI多代理量化投资团队。当用户需要：创建AI投资团队、配置多代理协作、实施投资决策流程、获取股票行情、分析趋势方向、行为金融分析、AI量化策略时使用。触发场景如"我想分析某只股票"、"帮我配置投资团队"、"量化策略开发"等。
dependency:
  python:
    - yfinance>=0.2.28
    - pandas>=2.0.0
    - numpy>=1.24.0
    - scikit-learn>=1.3.0
    - torch>=2.0.0
---

# 华尔街AI多代理量化投资团队

## 任务目标

- 构建类似华尔街基金公司的AI多代理投资团队
- 实现专业代理协同工作、投资决策流程化、风险控制自动化
- 提供AI时代最前沿的量化分析能力

## 核心投资理念

- **顺势而为**：趋势是第一准则，永远不要与趋势为敌
- **行为金融**：精准分析投资人群行为，理解大众心理才能预判市场走向
- **AI量化**：AI时代最专业最具深度的量化分析能力
- **风险控制**：投资是极少数人赚钱的活动，必须专业、精准、严格

## 投资分析规范（强制执行）

### 免责声明（每次分析必须置于开头）

> **免责声明**：本文仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。任何人因本文内容而造成的投资损失，作者不承担任何责任。股票市场波动剧烈，历史收益不代表未来表现。在做出任何投资决策之前，请咨询您的投资顾问或进行独立研究。

### 禁止事项

- 明确给出"买入/卖出XXX"的指令
- 预测具体目标价位
- 承诺或暗示收益预期
- 直接荐股行为

### 允许事项

- 深度分析板块逻辑、产业链、竞争格局
- 分析公司核心竞争力、商业模式、财务质量
- 解读行业趋势、政策影响、供需关系
- 提示风险因素、潜在隐患
- 提供技术分析和量化视角

## 完整分析流程（强制遵循）

每当执行投资分析任务时，必须严格按以下顺序进行：

1. **宏观分析** - 经济周期与货币政策
2. **行业研判** - 行业生命周期与景气度
3. **公司研究** - 商业模式与核心竞争力
4. **技术/量化分析** - 趋势方向与AI量化验证
5. **风险评估** - 多维度风险识别
6. **综合研判** - 机会与风险对比

## 多代理团队架构

### 7个专业代理

| 代理 | 核心职责 | 适用场景 |
|------|---------|---------|
| 策略总监 | 团队协调、投资决策、风险把控 | 全局决策、任务分配 |
| 基本面分析师 | 财务报表、商业模式、估值建模 | 价值评估、财务质量 |
| 技术分析师 | K线形态、趋势判断、买卖点位 | 入场出场时机 |
| 行业研究员 | 产业链、竞争格局、政策影响 | 赛道选择、行业趋势 |
| 舆情监控 | 新闻舆情、市场情绪、事件驱动 | 突发事件、情绪把控 |
| 风控专员 | 风险识别、仓位管理、合规审查 | 风险控制、止损执行 |
| 量化研究员 | AI量化模型、因子挖掘、策略回测 | 机器学习、深度学习、强化学习 |

### 代理人格模板

详细人格定义请参考：
- `assets/agent-templates/chief.md` - 策略总监
- `assets/agent-templates/fundamental.md` - 基本面分析师
- `assets/agent-templates/technical.md` - 技术分析师
- `assets/agent-templates/industry.md` - 行业研究员
- `assets/agent-templates/sentiment.md` - 舆情监控
- `assets/agent-templates/risk.md` - 风控专员
- `assets/agent-templates/quant.md` - 量化研究员

## 工作流编排

### 投资分析工作流（9步流程）

1. 任务分解 → 2. 基本面分析 → 3. 技术面分析 → 4. 行业研究 → 5. 舆情监控 → 6. 汇总整合 → 7. 投资决策 → 8. 风控审查 → 9. 主人汇报

详细工作流配置见：`references/workflow-orchestration.md`

## 核心能力

### 1. 股票数据获取

```bash
python scripts/stock_data_fetcher.py AAPL --type quote  # 实时报价
python scripts/stock_data_fetcher.py 600519.SS --type technical  # 技术指标
python scripts/stock_data_fetcher.py 0700.HK --type history --period 1y  # 历史数据
```

### 2. 趋势分析

顺势而为第一准则，参考：
- `scripts/trend_analyzer.py` - 趋势识别脚本
- `references/trend-analysis.md` - 趋势分析指南

### 3. 行为金融分析

- `scripts/behavior_analyzer.py` - 市场情绪分析
- `references/behavior-finance.md` - 行为金融指南

### 4. AI量化分析

AI时代最前沿量化技术：
- `scripts/advanced_quant.py` - 高级量化脚本
- 机器学习：XGBoost、LightGBM、CatBoost
- 深度学习：LSTM、Transformer、CNN
- 强化学习：DQN、PPO、A2C

## 资源索引

| 资源类型 | 文件路径 | 用途 |
|---------|---------|------|
| 配置模板 | `assets/config-templates/openclaw-config.json` | 主配置文件 |
| 代理人格 | `assets/agent-templates/*.md` | 7个代理人格定义 |
| 工作流编排 | `references/workflow-orchestration.md` | 工作流配置 |
| 监控部署 | `references/monitoring-system.md` | 监控观测系统 |
| 成本优化 | `references/cost-control.md` | 成本控制策略 |
| 数据获取 | `scripts/stock_data_fetcher.py` | 股票数据获取 |
| 趋势分析 | `scripts/trend_analyzer.py` | 趋势识别分析 |
| 行为分析 | `scripts/behavior_analyzer.py` | 行为金融分析 |
| 量化分析 | `scripts/advanced_quant.py` | AI量化模型 |
| 分析规范 | `references/investment-analysis-guide.md` | 强制分析规范 |
| 股票使用指南 | `references/stock-data-usage.md` | 数据使用说明 |
| 智囊邀请机制 | `references/advisor-invitation.md` | 智囊团邀请 |

## 使用示例

### 示例1：构建基础投资团队

- 读取配置模板和代理人格模板
- 根据需求调整代理数量和模型配置
- 测试代理响应能力

### 示例2：分析特定标的

```
【免责声明】

【板块/个股深度分析】

一、宏观环境
...

二、行业分析
...

三、公司研究
...

四、技术/量化视角
...

五、风险提示
...

六、综合研判
- 核心逻辑：
- 关注要点：
- 风险因素：
- **特别说明：本文不构成投资建议**
```

### 示例3：量化策略开发

1. 数据准备与特征工程
2. 机器学习模型构建（XGBoost/LightGBM）
3. 深度学习模型（LSTM/Transformer）
4. 强化学习策略（PPO/DQN）
5. 回测验证与优化

## 环境依赖

```bash
pip install yfinance>=0.2.28 pandas>=2.0.0 numpy>=1.24.0 scikit-learn>=1.3.0 torch>=2.0.0
```

## 智囊邀请机制

分析完成后可邀请智囊团专家参与决策讨论：

| 智囊 | 特点 | 适用场景 |
|------|------|---------|
| 马斯克 | 第一性原理、技术洞察 | 颠覆性创新、高成长赛道 |
| 巴菲特 | 价值投资、长期主义 | 价值投资、稳健配置 |

### 邀请话术

```
【智囊邀请】

经过团队深度分析后，是否需要邀请智囊团专家进一步探讨？

- 马斯克：擅长第一性原理思考，适合分析颠覆性创新机会
- 巴菲特：价值投资大师，适合评估长期投资价值
```
