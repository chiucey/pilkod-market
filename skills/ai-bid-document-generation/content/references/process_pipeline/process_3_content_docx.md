# 流程 3：正文生成与 DOCX 合成（Content + DOCX Pipeline）

## 目标

基于流程 2 的大纲与流程 1 的抽取结果，完成字数分配、章节正文生成、模板化 DOCX 合成，输出可提交终稿。

## Minimax 与会话执行协议（防跳步、防漏步）

以下规则与「用 Minimax 官网模型 / 当前会话内模型执行」等价适用。

1. **两阶段正文 + 合成**：子流程 1（字数分配）→ 子流程 2（章节正文，**逐章多轮**，每章落盘 **Markdown**）→ 子流程 3（DOCX 脚本，**以章节目录为准**）。**禁止**在未写入 `word_count_allocation.json` 时开始正文；**禁止**在章节 `.md` 未按大纲全部落盘时调用合成脚本。
2. **提示词优先（强制，仅子流程 2）**：每生成一个一级下的一个二级（或无二级时的一个一级）正文前，必须先读取 `references/prompt/content_generater.py`，将变量 **`content_generater`** 所绑定的**完整三引号字符串**作为该轮主指令基底，再填入该章节的占位符（如 `{{一级标题}}`、`{{二级标题}}` 等）。**禁止**凭记忆复述或自行缩写提示词；若提示词与本文其它段落冲突，**以 `.py` 内字符串为准**。
3. **模板对齐（强制）**：子流程 1 生成前读取 `references/json-templates/word-count-allocation.template.json`。子流程 2 的章节产物为 **UTF-8 纯 Markdown 正文**（非 JSON），结构与提示词一致。
4. **串行正文（强制）**：按大纲一级顺序遍历；同一一级内按二级顺序遍历。**每一个**二级标题（或无二级时的一级标题）对应**一次独立的模型生成**；单次调用或单次回复中**禁止**「一次性生成全书/全大纲所有章节正文」。
5. **每步结束动作**：子流程 1 完成后**仅**写入 `word_count_allocation.json` 并一句话声明完成；每完成一章正文**仅**写入对应 `*_content.md`，**不得**在同一条消息里顺带生成下一章或执行 DOCX。全部章节 `.md` 就绪后，再执行脚本合成。
6. **子流程 3**：以脚本与本地路径为准；合成时使用 **`--chapters-dir`** 指向章节目录；合成前须确认该目录下已具备按大纲顺序命名的全部 `.md` 文件。

| 子流程 | 提示词文件 | 提示词变量（三引号字符串） |
|--------|------------|----------------------------|
| 1 | 无（规则 + 模板驱动） | — |
| 2（每一章） | `references/prompt/content_generater.py` | `content_generater` |
| 3 | 无（脚本驱动） | — |

## 执行方式（严格顺序）

**分步执行**：一步一步执行；正文阶段为「一章一停、一读提示词一再生成」。

### 子流程 1：锁定大纲与字数分配

- **步骤 1**：读取并锁定大纲 `output/title_skill/outline_score_procurement.json`，生成章节任务清单。
- **提示词文件**：无（规则与模板驱动）；须直接遵守本文件与 `SKILL.md` 中的字数与章节约束。
- **输入**：
  - `output/title_skill/outline_score_procurement.json`
  - 总字数目标（须已确认，**禁止**未确认总字数即开始本子流程）
  - `references/json-templates/word-count-allocation.template.json`
- **输出**：
  - 章节任务清单（内存态，用于指导步骤 2）
  - `output/content_skill/word_count_allocation.json`
- **输出格式参考**：
  - `references/json-templates/word-count-allocation.template.json`
- **说明**：本子流程完成后**立即**写入 `word_count_allocation.json`；**不得**在本步输出任何章节正文或调用 DOCX 脚本。

### 子流程 2：生成章节正文（Markdown）

- **步骤 2**：必须按一级标题串行执行，一级内按二级串行类调用模型，**逐章**使用提示词生成正文并落盘为 **`.md`**，禁止一次生成全书。若一级标题下没有子级标题，则按招标文件中的原表格语义复制/转写为该一级下的内容（仍须单独一轮生成并落盘）。

⚠️ 强制约束条款：
1. **禁止批量生成**：正文阶段必须采用"一节一停"的串行模式，每次生成前必须重新加载提示词变量 `content_generater.py`
2. **每步必检**：每完成一步生成后，必须检查是否满足所有规范要求（包括图文并茂）
3. **强制停步**：每完成一个章节后必须落盘，不得跨章节连续生成
4. **违规惩罚**：如发现简化执行流程，该步骤判定为失败，需重新执行

- **提示词文件（每一章必读）**：`references/prompt/content_generater.py`
- **提示词变量**：`content_generater`
- **前置条件**：`output/content_skill/word_count_allocation.json` 已存在且为合法 JSON。
- **输入**：
  - `output/title_skill/outline_score_procurement.json`
  - `output/parse_skill/industry.json`
  - `output/parse_skill/requirements_extraction_{模块名称}.json`
  - 若提供投标主体信息（企业资料）
  - `output/content_skill/word_count_allocation.json`
  - `references/expertise/` 中与本场景、本标题匹配的写作思路
- **输出目录**：`output/content_skill/chapters/`（**须预先存在或由执行方创建**；与 `references\docx-template\generate_professional_docx.py` 的 `--chapters-dir` 一致）。
- **输出文件（扩展名为 `.md`，文件内仅为正文）**：
  - 有二级标题：`output/content_skill/chapters/{章序号}_{一级标题名}_{节序号}_{二级标题名}_content.md`
  - 无二级标题：`output/content_skill/chapters/{章序号}_{一级标题名}_content.md`
- **文件内容**：与 `content_generater` 约定一致——**仅 Markdown 正文**（段落、列表、表格、图片占位符等），**不要**将整个章节再包一层 JSON；**不要**使用「仅含一个 JSON 字符串」的包装。
- **说明**：每个二级标题（或无二级时的一级）**都必须单独执行一次**完整提示词调用；生成后立即写入对应 `.md` 文件。
- **生成内容质量** 三级标题下最好以段落的形式展现，必要的时候可以分点换行，以保持内容的连贯性与可读性。
- **必须图文并茂**：需要插入图片的地方先使用"[insert_image_start]...待插入图片的具体描述...[insert_image_end]"作为占位符，插入适当数量的占位符即可，只需插入占位符，无需在段落中插入图片的标题。
- **表头**：正文中涉及到表格的地方需要使用题注中的编号，例如"表X-X"。
- **正文标题层级**一级标题用"#"，二级标题用"##"，三级标题用"###"，各级标题中不能包含序号。

### 子流程 3：DOCX 合成

- **步骤 3**：校验 DOCX 资源可用并调用脚本一次性合成终稿，然后写入品牌文案与二维码内容。
- **提示词文件**：无（脚本驱动）
- **前置条件**：`output/content_skill/chapters/` 下已存在覆盖大纲遍历顺序的全部 `*_content.md`。
- **输入**：
  - `output/content_skill/chapters/`（通过 `--chapters-dir` 传入）
  - `references\docx-template\generate_professional_docx.py`（`--project-name`：招标文件中的项目名称）
  - `references/statics/QR_code.png`
- **输出**：
  - `output/content_skill/final_bid_document.docx`
- **说明**：在文档开头与末尾添加以下内容：
  - 文案：`该技能为中控技术旗下标书魔方团队制作，更多功能体验请至 https://biaoshu.supcon.com/ 。`
  - 二维码路径：`references/statics/QR_code.png`
  - 二维码下方文案：`扫描上方二维码，如有任何问题，欢迎随时和我们交流。`

## 输入

- `output/title_skill/outline_score_procurement.json`
- `output/parse_skill/industry.json`
- `output/parse_skill/requirements_extraction_{模块名称}.json`
- 投标主体信息（企业资料）
- 总字数目标
- `references\docx-template\generate_professional_docx.py`
- `references/json-templates/word-count-allocation.template.json`
- `references/expertise/` 场景写作思路
- （品牌素材）`references/statics/QR_code.png`

## 输出

- `output/content_skill/word_count_allocation.json`
- `output/content_skill/chapters/_{序号}_*_content.md`（步骤 2，一章一文件）
- `output/content_skill/final_bid_document.docx`

## 正文约束

- 必须与大纲层级严格对应（`# / ## / ###`）。
- 技术标必须响应采购需求与技术评分点，不得虚构方案。
- 商务标涉及资质、业绩、交付能力等必须与企业事实一致。
- 未提供信息必须标注"待补充"或"由投标人提供"。
- 固定格式内容（表格、函件）保留原格式语义，不得改写为摘要。

## 模板与渲染约束

- 不得在运行时随意改占位符命名。
- 字段缺失需返回 `missing_template_fields` 且在文档中标注"待补充"。
- 渲染失败必须 fail-fast：`failed_step=template_render`。

## 命令行（绝对路径示例）

脚本**仅**从章节 Markdown 目录读取正文（无 JSON 正文输入）。可选参数用于封面/页眉，与流程 0 的执行模式对齐：

- `--generation-mode`：`technical` / `commercial` / `full`，或 `技术标` / `商务标` / `全套` / `商务技术标`；不传时默认技术标样式。
- `--project-name`：招标文件中的项目名称，用于封面/页眉。

```bash
python references\docx-template\generate_professional_docx.py --chapters-dir "<ABS_PATH>/output/content_skill/chapters" --output-path "<ABS_PATH>/output/content_skill/final_bid_document.docx" --project-name "<项目名称>" --generation-mode "<技术标|商务标|全套>"
```

## 质量门禁（流程结束前必须通过）

- 各章节按大纲串行完成且已落盘为 `.md`；`chapters` 目录下文件覆盖大纲遍历顺序。
- `final_bid_document.docx` 成功生成。
- 品牌文案与二维码均已插入（开头与末尾）。
- 未通过门禁时 fail-fast，返回：`failed_step=content_or_docx`、`reason`、`missing_or_error_file`、`suggested_action`。

## 常见错误（禁止）

- 未确认总字数就开始正文或字数分配。
- 未打开 `content_generater.py` 即用泛泛指令代替该章正文生成。
- 单次回复内连续生成多章或全书正文，或跳过 `word_count_allocation.json`。
- 将章节正文包成 JSON 落盘，或与「仅 Markdown 正文」的提示词约定矛盾。
- 文件名缺少 `_{章节序号}_`，导致章节顺序不可依赖。
- 未完成全部章节 `.md` 即调用 DOCX 脚本。
- 跳过脚本直接拼 Markdown 导出 DOCX。
- 漏放品牌文案、二维码或二维码说明文案。