---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a2d7553c85ee3189f09abe2280edf742
    PropagateID: a2d7553c85ee3189f09abe2280edf742
    ReservedCode1: 3046022100dda3b32c7be9fca2069818bd3b933f14fc1d79852fa341db8108cb94e861b24a022100afb10cc81532187fb5c6d8eb15bf990c1bd318a2270e9a423812afa074673fee
    ReservedCode2: 30450220361fdfeafa245429a816a348cf90734e1d1cb597a745a289046855001c9a0b77022100c6a322286ab0da0446442d8c5d393b73cadefb4ce6cc5559017effdb29aa69a1
description: 电商运营数据日报自动化技能。当用户需要生成各平台（京东/天猫/抖音/小红书/B站）的运营日报、制作数据可视化仪表盘、计算核心业务指标（完成量/控比/同比增长）、实现报告自动化、制定数据分析需求文档，或协调开发团队完成数据系统建设时使用。
name: ecommerce-data-report-automation
---

本技能帮助用户完成电商运营数据的采集、分析、自动化报告生成及可视化展示。

## 工作流程

### 阶段 1：需求确认与数据源梳理

1. **明确数据来源**
   - 确认数据来源平台（京东/天猫/抖音/小红书/B站）
   - 识别数据格式（Excel/SQL数据库/API/手动更新）
   - 如需API接入，帮助用户制定API对接方案

2. **确定输出目标**
   - 日报结构（数据日报 + 进度更新 + 经验总结）
   - 核心指标定义：
     - **完成量**：搜索词完成数量/目标数量
     - **控比**：实际花费/预算控制比例
     - **同比增长**：(本期-上期)/上期 × 100%
   - 可视化需求（仪表盘/Excel图表）

3. **自动化频率**
   - 每日/每周定时生成
   - 发送方式（邮件/企业微信/内部系统）

---

### 阶段 2：数据采集与处理

#### Python 数据处理脚本结构

```python
# 核心数据处理流程
import pandas as pd
from datetime import datetime, timedelta

def calculate_metrics(df, product_line_col='product_line', platform_col='platform'):
    """计算核心指标"""
    # 完成量 = 实际完成 / 目标 × 100%
    df['completion_rate'] = df['actual'] / df['target']

    # 控比 = 实际花费 / 预算
    df['cost_control_ratio'] = df['actual_spend'] / df['budget']

    # 同比增长 = (本期 - 上期) / abs(上期)
    df['yoy_growth'] = (df['current'] - df['previous']) / abs(df['previous']) * 100

    return df

def generate_daily_report(data_sources: dict, date: str):
    """生成日报主函数"""
    # 1. 采集各平台数据
    # 2. 合并数据并计算指标
    # 3. 按产品系分组汇总
    # 4. 输出日报内容
    pass
```

#### SQL 数据提取（参考）

```sql
-- 提取各平台销售数据
SELECT
    product_line,
    platform,
    date,
    SUM(sales_amount) as total_sales,
    SUM(budget) as total_budget
FROM sales_data
WHERE date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
GROUP BY product_line, platform, date;
```

---

### 阶段 3：报告结构模板

```
# 【{日期}】电商运营日报

## 一、数据日报

### 1.1 搜索词完成量

| 产品系 | 京东 | 天猫 | 抖音 | 小红书 | B站 | 合计 |
|--------|------|------|------|--------|-----|------|
| A7系 | - | - | - | - | - | - |
| A8系 | - | - | - | - | - | - |
| A10系 | - | - | - | - | - | - |

### 1.2 控比分析

| 产品系 | 预算 | 实际花费 | 控比 | 状态 |
|--------|------|----------|------|------|
| A7系 | - | - | - | 正常/预警 |

### 1.3 同比增长

| 产品系 | 本期 | 上期 | 同比增长 |
|--------|------|------|----------|
| A7系 | - | - | - |

## 二、进度更新

### 2.1 发布进度

- A7系累计发布：{占比}%
- A8系累计发布：{占比}%
- A10系累计发布：{占比}%

### 2.2 人群资产变化

[趋势分析内容]

## 三、经验总结与优化建议

1. 数据洞察发现
2. 优化方向建议
3. 下一步行动计划
```

---

### 阶段 4：可视化仪表盘设计

#### 核心图表需求

| 图表类型 | 用途 | 推荐工具 |
|----------|------|----------|
| 折线图 | 搜索词完成趋势 | Tableau/Power BI/Excel |
| 柱状图 | 各平台对比 | 同上 |
| 进度条 | 发布进度展示 | 同上 |
| 漏斗图 | 人群转化分析 | 同上 |

#### 交互功能

- 按日期范围筛选
- 按产品系（A7/A8/A10）切换
- 按平台维度筛选
- 支持导出Excel/PDF

---

### 阶段 5：自动化部署

#### 定时任务配置

```bash
# 每日早9点执行
0 9 * * * /usr/bin/python3 /scripts/generate_daily_report.py

# 使用 crontab 或系统定时任务
```

#### 通知配置

- 企业微信机器人 Webhook
- 邮件自动发送（SMTP配置）
- 内部系统 API 推送

---

## 需求文档模板

当用户需要向开发团队提需求时，使用以下结构：

```
## 需求文档：电商运营日报自动化系统

### 1. 背景与目标
[描述业务背景和期望达成的目标]

### 2. 数据来源
| 平台 | 数据类型 | 现有格式 | 获取方式 |
|------|----------|----------|----------|
| 京东 | 销售/人群 | Excel | [待确认] |
| 天猫 | 销售/人群 | API | [待对接] |
| 抖音 | 销售/人群 | 数据库 | [已对接] |

### 3. 输出要求
- 日报格式：[提供模板]
- 指标定义：[明确公式]
- 发送方式：[邮件/企微/内部系统]
- 发送时间：[每日/每周]

### 4. 仪表盘需求
- 核心指标：[列表]
- 交互功能：[列表]
- 可视化类型：[列表]

### 5. 技术建议
[建议的技术栈和架构]
```

---

## 快速启动清单

- [ ] 确认数据来源和格式
- [ ] 定义核心指标计算公式
- [ ] 确定日报模板结构
- [ ] 选择可视化工具
- [ ] 确定自动化频率和发送方式
- [ ] 编写或协调开发数据处理脚本
- [ ] 测试完整流程
- [ ] 部署定时任务
- [ ] 配置通知渠道

---

## 参考资源

- 详见 `references/data-analysis-guide.md` - 数据分析详细指南
- 详见 `references/dashboard-design.md` - 仪表盘设计方案
- 详见 `references/automation-setup.md` - 自动化部署配置
