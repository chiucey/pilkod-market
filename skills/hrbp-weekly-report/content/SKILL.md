---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9ade5288a58c40471687be3bd7cc0abd
    PropagateID: 9ade5288a58c40471687be3bd7cc0abd
    ReservedCode1: 3045022100fcd0cb8ac64d8c601739bd0fa2e64225f12dc5e7a4de952978e155fa4654b562022005ed1e043c26c1d04694822a7b34a608f6d5eafb739da45b184ed191d56eb029
    ReservedCode2: 3045022100f6c116d4469f677af3cc9e0cb239108b1ef0ed49a90d7827cdb92683db369d83022001b64997e605387b4978b1102e7121aa74a889585a553c3418ec2fe92949c6ca
description: 生成HRBP周报邮件内容。当用户需要撰写周报、汇报本周HR工作数据、或需要从Excel数据生成周报邮件时使用。
name: hrbp-weekly-report
---

# HRBP周报邮件技能

根据动态格式模板和Excel数据自动生成周报邮件内容。

## 输入要求

用户提供以下信息：
1. **Excel文件路径** - 包含本周HR数据的Excel文件
2. **Word文件路径** - 包含本周工作进展和组织观测的Word文件
2. **周次** - 如"本周"或"下周"
3. **部门/团队名称** - T1如"出行技术",T2如"乘客业务技术"
4. **其他补充说明** - T1部门是T2部门的更高层级部门,是包含关系

## 数据来源

Excel文件应包含以下Sheet:
- `本周` - 包含所有T1/T2的本周HC数据
- `上周` - 包含所有T1/T2的上周HC数据

## 执行流程

### 步骤1：读取Excel数据

读取用户提供的Excel文件，从"本周"和"上周"两个Sheet中提取所有T1/T2数据。

### 步骤2：计算核心指标

- **HC变化**：读取"2026新目标HC"列，对比本周与上周差值；正值=增加，负值=减少；T1差值=0时不体现该条；所有T1差值均为0时整个【HC变化】板块不体现。
- **在职人员体量变化**：自动识别各T1下所有T2，对比本周与上周在职人数，diff≠0的T2才体现，diff=0的T2整条不体现。

### 步骤3：生成HC预测

自动读取本周Sheet中社招在途、活入在途、离职在途、活出在途、校招在途、预测GAP共6个字段；数值=0的字段整条不体现，非零字段如实填写。

### 步骤4：生成邮件

将计算结果填入固定格式模板，生成完整周报邮件。

## 输出格式

生成格式规范的周报邮件，包含：
- 标题
- 本周HC：【HC变化】（识别2026新目标HC，正值=增加，负值=减少，差值=0不体现）、【在职人员体量变化】（T2自动展开，diff=0不体现）、【HC预测】（数值为0的字段不体现）
- 本周工作进展（在word中查找摘取，固定格式）
- 组织观测（在word中查找摘取）

## 邮件模板

详见 `references/email_template.md`

## 数据结构

详见 `references/data_schema.md`

## 计算脚本

使用 `scripts/calculate_metrics.py` 进行指标计算。
