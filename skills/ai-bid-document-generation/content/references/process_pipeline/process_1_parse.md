# 流程 1：解析招标要求（Parse Pipeline）

## 目标

将 `bid_doc` 解析为可复用的结构化招标要求，产出行业标签与分模块抽取结果，作为流程 2、流程 3 的唯一事实输入。

## Minimax 与会话执行协议（防跳步、防漏步）

以下规则与「用 Minimax 官网模型 / 当前会话内模型执行」等价适用：**语义与格式以本文件 + 各步提示词字符串为准**。

1. **二步二停**：子流程 1 → 2 必须拆成**两次独立的生成动作**。单次模型调用或单次助手回复中，**禁止**在未落盘子流程 1 产物的情况下直接输出子流程 2 的全部模块 JSON，也**禁止**将多个模块的抽取合并为一次不落盘的「口述草稿」替代分步落盘。
2. **提示词优先（强制）**：在生成该步 JSON **之前**，必须先读取对应 `references/prompt/*.py` 文件，将下表中的**提示词变量**所绑定的**完整三引号字符串**作为该轮系统/主指令（或等价地合并进用户消息首部）。**禁止**凭记忆复述或自行缩写提示词；若提示词与本文其它段落冲突，**以该步 `.py` 内字符串为准**，本文仅约束路径、文件名与步骤边界。
3. **模板对齐（强制）**：生成前须读取对应 `references/json-templates/*.template.json`（见各子流程「输出格式参考」），保证字段层级与约定一致；最终输出须为合法 JSON（步骤内提示词若要求「仅 JSON、无 Markdown 代码块」，须严格遵守）。
4. **依赖链**：子流程 2 的输入中若使用行业元数据，其 JSON 必须来自磁盘上已存在的 `output/parse_skill/industry.json`；**禁止**用「本对话中刚才口述的草稿」代替已写入文件的版本。
5. **每步结束动作**：该步 JSON 校验可读后，**立即**写入该步规定的输出路径；写入完成后，在对话中用**一句话**声明：`步骤 {n} 已完成，产物路径：…`，**不得**在同一条消息里继续执行下一步的正文生成。
6. **再开下一步**：仅当用户或流程明确进入下一步时，才加载**下一步**的提示词文件并重复上述协议。

| 子流程 | 必须先读的提示词文件 | 必须使用的提示词变量（三引号字符串） |
|--------|----------------------|--------------------------------------|
| 1 | `references/prompt/industry.py` | `industry_class` |
| 2 | `references/prompt/extraction.py` | `extractor` |

## 执行方式（严格顺序）

**分步执行**：一步一步执行；每步须完成「读提示词 → 读模板与输入 → 仅生成该步 JSON → 落盘 → 声明完成」后，再开始下一步。

### 子流程 1：行业/场景识别

- **步骤 1**：读取 `references/industry-classification.md`，执行行业/场景识别。
- **提示词文件（必读）**：`references/prompt/industry.py`
- **提示词变量**：`industry_class`（将该变量赋值右侧的完整字符串作为该步主指令）
- **输入**：
  - `bid_doc`（PDF 路径、URL 或上传映射）
  - `references/industry-classification.md`（行业分类依据）
- **输出**：
  - `output/parse_skill/industry.json`
- **输出格式参考**：
  - `references/json-templates/industry.template.json`
- **说明**：仅输出行业分类结果，用于流程元数据，不用于正文抽取；本步完成后**仅**写入 `industry.json`，**不得**在本步写入各模块 `requirements_extraction_*.json`。

### 子流程 2：模块化抽取招标要求

- **步骤 2**：读取 `references/unified-extraction-resource.md`，按模块语义执行分块多次抽取。
- **提示词文件（必读）**：`references/prompt/extraction.py`
- **提示词变量**：`extractor`
- **前置条件**：`output/parse_skill/industry.json` 已存在且为合法 JSON。
- **输入**：
  - `bid_doc`（PDF 路径、URL 或上传映射）
  - `references/unified-extraction-resource.md`（按模块切分后写入 `{{extraction_content}}`）
  - `references/json-templates/requirements-extraction.template.json`（结构校验依据）
  - `output/parse_skill/industry.json`（行业上下文元数据，与抽取提示词约定一致时使用）
- **必须分别输出输出结果，不能合并为一个 JSON 文件**：
  - `output/parse_skill/requirements_extraction_项目信息.json`
  - `output/parse_skill/requirements_extraction_投标文件组成.json`
  - `output/parse_skill/requirements_extraction_评分标准.json`
  - `output/parse_skill/requirements_extraction_采购需求.json`
- **输出格式参考**：
  - `references/json-templates/requirements-extraction.template.json`
- **说明**：结合 `{{extraction_content}}` 分块抽取，输出结构化 JSON；抽取时严格按原文保真，禁止改写、概括、缩写；评分标准和采购需求中的表格必须保留表格语义；每模块完成后立即写入对应文件。

## 输入

- `bid_doc`（PDF 路径、URL 或上传映射）
- `references/industry-classification.md`
- `references/unified-extraction-resource.md`
- `references/json-templates/industry.template.json`
- `references/json-templates/requirements-extraction.template.json`
- `references/prompt/industry.py`（子流程 1，`industry_class`）
- `references/prompt/extraction.py`（子流程 2，`extractor`）

## 输出

- `output/parse_skill/industry.json`（子流程 1）
- `output/parse_skill/requirements_extraction_{模块名称}.json`（子流程 2；流程 2 消费 `requirements_extraction_*`）

## 核心约束

- 抽取须严格按原文保真，禁止改写、概括、缩写；禁止用模型总结替代原文抽取。
- 评分标准与采购需求中的表格须保留表格语义，不得转为无结构段落。
- 子流程 2 须基于 `references/unified-extraction-resource.md` 的模块语义分块执行，不得跳过该资源直接泛泛抽取。
- 须产出结构化要求 JSON；仅产出行业标签、不产出各模块 `requirements_extraction_*.json` 视为流程失败。

## 交叉引用处理规范（必须执行）

### 原则

- 追踪：遇到交叉引用必须定位到被引用位置。
- 完整：被引用片段必须完整抽取，不得截断关键语义。
- 闭环：不得保留悬空引用（「详见…」但未提取实际内容）。

### 常见模式

| 引用模式 | 示例 | 处理动作 |
|---|---|---|
| 章节引用 | 详见第 X 章 | 跳转章节并完整抽取 |
| 表格引用 | 见下表 | 抽取完整表格结构与单元格语义 |
| 附件引用 | 见附件 X | 在附件或正文定位并抽取 |
| 部分引用 | 技术要求见 3.1 节 | 提取 3.1 节完整条目 |
| 文档引用 | 见技术规格书 | 定位规格书对应部分并抽取 |

## 质量门禁（进入流程 2 前必须通过）

- 输出文件存在且为合法 JSON。
- `requirements_extraction_{模块名称}.json` 的层级可被后续流程读取（至少含可识别模块节点）。
- 未通过门禁时 fail-fast，返回：`failed_step=parse`、`reason`、`missing_or_error_file`、`suggested_action`。

## 常见错误（禁止）

- 未打开对应 `.py` 提示词文件即用泛泛指令代替该步生成。
- 未读取 `references/unified-extraction-resource.md` 就直接抽取。
- 单次回复内跳过 `industry.json` 落盘即输出全部模块抽取结果。
- 将表格转成无结构段落。
- 用模型总结替代原文抽取。
- 只产出行业标签，不产出结构化要求 JSON。