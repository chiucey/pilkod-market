# 流程 2：标题大纲生成（Outline Pipeline）

## 目标

基于流程 1 的结构化招标要求，按执行模式（全套/商务/技术）生成三级目录树，固定输出可供流程 3 消费的大纲 JSON。

## Minimax 与会话执行协议（防跳步、防漏步）

以下规则与「用 Minimax 官网模型 / 当前会话内模型执行」等价适用：**语义与格式以本文件 + 各步提示词字符串为准**。

1. **三步三停**：子流程 1 → 2 → 3 必须拆成**三次独立的生成动作**。单次模型调用或单次助手回复中，**禁止**同时产出步骤 2、步骤 3 的内容，也**禁止**在未落盘步骤 1 产物的情况下直接输出步骤 2/3 的完整大纲。
2. **提示词优先（强制）**：在生成该步 JSON **之前**，必须先读取对应 `references/prompt/*.py` 文件，将下表中的**提示词变量**所绑定的**完整三引号字符串**作为该轮系统/主指令（或等价地合并进用户消息首部）。**禁止**凭记忆复述或自行缩写提示词；若提示词与本文其它段落冲突，**以该步 `.py` 内字符串为准**，本文仅约束路径、文件名与步骤边界。
3. **模板对齐（强制）**：生成前须读取 `references/json-templates/outline.template.json`，保证字段层级与约定一致；最终输出须为合法 JSON（步骤内提示词若要求「仅 JSON、无 Markdown 代码块」，须严格遵守）。
4. **依赖链**：步骤 *n* 的输入 JSON 必须来自磁盘上已存在的上一步输出；**禁止**用「本对话中刚才口述的草稿」代替已写入文件的版本。
5. **每步结束动作**：该步 JSON 校验可读后，**立即**写入该步规定的输出路径；写入完成后，在对话中用**一句话**声明：`步骤 {n} 已完成，产物路径：…`，**不得**在同一条消息里继续执行下一步的正文生成。
6. **再开下一步**：仅当用户或流程明确进入下一步时，才加载**下一步**的提示词文件并重复上述协议。

| 子流程 | 必须先读的提示词文件 | 必须使用的提示词变量（三引号字符串） |
|--------|----------------------|--------------------------------------|
| 1 | `references/prompt/outline_level_1.py` | `generate_level1_headings` |
| 2 | `references/prompt/outline_score.py` | `generate_scoring_outline` |
| 3 | `references/prompt/outline_score_procurement.py` | `supplement_procurement_outline` |

## 执行方式（严格顺序）

**分步执行**：一步一步执行；每步须完成「读提示词 → 读模板与输入 → 仅生成该步 JSON → 落盘 → 声明完成」后，再开始下一步。

### 子流程 1：生成一级标题骨架

- **步骤 1**：读取 `output/parse_skill/requirements_extraction_{模块名称}.json`，在 `content_structured.modules` 中识别「投标文件组成」相关内容并生成一级标题骨架（仅 `level=1`，`children=[]`）。
- **提示词文件（必读）**：`references/prompt/outline_level_1.py`
- **提示词变量**：`generate_level1_headings`（将该变量赋值右侧的完整字符串作为该步主指令）
- **输入**：
  - `output/parse_skill/requirements_extraction_{模块名称}.json`
  - 执行模式（全套 / 商务 / 技术）
- **输出**：
  - `output/title_skill/outline_level_1.json`
- **输出格式参考**：
  - `references/json-templates/outline.template.json`
- **说明**：一级标题必须来源于"投标文件组成"原文；本步完成后**仅**写入 `outline_level_1.json`，**不得**在本步写入 `outline_score.json` 或 `outline_score_procurement.json`。

### 子流程 2：补评分标准二级/三级

- **步骤 2**：基于子流程 1 的一级标题骨架，识别评分标准（商务/技术/报价）并补齐评分相关二级、三级标题。
- **提示词文件（必读）**：`references/prompt/outline_score.py`
- **提示词变量**：`generate_scoring_outline`
- **前置条件**：`output/title_skill/outline_level_1.json` 已存在且为合法 JSON。
- **输入**：
  - `output/title_skill/outline_level_1.json`
  - `output/parse_skill/requirements_extraction_{模块名称}.json`（评分标准模块）
  - 执行模式（全套 / 商务 / 技术）
- **输出**：
  - `output/title_skill/outline_score.json`
- **输出格式参考**：
  - `references/json-templates/outline.template.json`
- **说明**：只补评分标准，不得混入采购需求；步骤完成后立即写入文件。

### 子流程 3：补采购需求二级/三级

- **步骤 3**：在 `outline_score.json` 基础上补采购需求相关二级、三级标题（技术模式必须在评分标准之后追加）。
- **提示词文件（必读）**：`references/prompt/outline_score_procurement.py`
- **提示词变量**：`supplement_procurement_outline`
- **前置条件**：`output/title_skill/outline_score.json` 已存在且为合法 JSON。
- **输入**：
  - `output/title_skill/outline_score.json`
  - `output/parse_skill/requirements_extraction_{模块名称}.json`（采购需求模块）
  - 执行模式（全套 / 商务 / 技术）
- **输出**：
  - `output/title_skill/outline_score_procurement.json`
- **输出格式参考**：
  - `references/json-templates/outline.template.json`
- **说明**：只能做补充，不得删改评分阶段已有节点；步骤完成后立即写入文件。下游唯一消费文件固定为 `output/title_skill/outline_score_procurement.json`。

## 输入

- `output/parse_skill/requirements_extraction_{模块名称}.json`
- 执行模式：全套 / 商务 / 技术
- `references/json-templates/outline.template.json`
- `references/prompt/outline_level_1.py`（步骤 1，`generate_level1_headings`）
- `references/prompt/outline_score.py`（步骤 2，`generate_scoring_outline`）
- `references/prompt/outline_score_procurement.py`（步骤 3，`supplement_procurement_outline`）

## 输出

- `output/title_skill/outline_level_1.json`（步骤 1）
- `output/title_skill/outline_score.json`（步骤 2）
- `output/title_skill/outline_score_procurement.json`（步骤 3；流程 3 唯一消费）

## 核心约束

- 一级标题必须来自招标文件"投标文件组成"，不得自创、删改顺序。
- 仅允许 `level` 1/2/3，不得出现四级标题。
- 技术模式二级顺序固定：`技术评分标准 -> 采购需求`。
- 已生成节点不得被后续步骤无故删除或重排。
- 同义重复标题需合并，禁止"…1/…2/…3"机械命名。
- 若一级标题为"技术偏差表/技术偏离表/商务偏差表"等表类节点，可保持 `children: []`。

## 模式差异

### 技术模式

- 一级：技术相关章节（含"技术部分"等技术条目）。
- 二级：先技术评分标准，再采购需求。
- 三级：评分点/采购点展开。

### 商务模式

- 一级：商务相关章节。
- 二级与三级：来自商务评分标准及其评分点。

### 全套模式

- 覆盖商务+技术；按先评分后采购的方式补全技术侧。

## 质量门禁（进入流程 3 前必须通过）

- `outline_score_procurement.json` 存在、合法 JSON、层级正确。
- 一级标题顺序与来源可追溯至"投标文件组成"。
- 技术模式顺序校验通过（评分在前，采购在后）。
- 未通过门禁时 fail-fast，返回：`failed_step=outline`、`reason`、`missing_or_error_file`、`suggested_action`。

## 常见错误（禁止）

- 未打开对应 `.py` 提示词文件即用泛泛指令代替该步生成。
- 单次回复内连续完成步骤 1+2+3，或跳过 `outline_level_1.json` / `outline_score.json`。
- 绕过一级骨架，直接生成二级三级。
- 技术模式先补采购需求再补评分标准。
- 把"专业技术人员情况/企业实力材料/主要产品规格一览表"等非技术项错误纳入技术模式一级。