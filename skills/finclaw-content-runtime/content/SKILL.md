---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: ec43646b60bd9fa72929cb1973e148a9
    PropagateID: ec43646b60bd9fa72929cb1973e148a9
    ReservedCode1: 3044022033628196dbc6b68c177c9c046d2ffcf1ffaa3e0934bf66b360b8e3e3c10fe1c30220116191bc9b32d8bfe26efdc46c1e420fc894dd52b072293998e2ad496d8ce2c4
    ReservedCode2: 3044022058fa33604096327c5c5375e49b1e4fa8246063d481c340b0894039c9759bdb6e02206eea33f232641aee9d4f0aea11efafe746af0596c73afa28fc231344352327ab
description: |
    FinClaw Content Runtime v2：面向金融、国央企、政务等高安全合规行业的 B2B 技术文章发布 Skill。 支持选题后先确认大纲，再确认正文，再确认配图，最后输出 Markdown 文件。 内置低 AI 感写作规则、硬禁词、企业观点层、SEO、视觉、引用、内容治理与发布平台适配配置。
files:
    - README.md
    - skill.yaml
    - configs/banlist.txt
    - configs/core_thesis.yaml
    - configs/glossary.yaml
    - configs/seo_rules.yaml
    - configs/source_policy.yaml
    - configs/topic_rules.yaml
    - configs/visual_style.yaml
    - configs/writing_constraints.yaml
    - configs/risk_policy.yaml
    - configs/china_media_search.yaml
    - prompts/stage1_outline.txt
    - prompts/stage2_draft.txt
    - prompts/stage2_5_wechat_optimize.txt
    - prompts/stage3_images.txt
    - prompts/stage4_finalize.txt
    - prompts/rewrite_humanize.txt
    - prompts/seo_optimize.txt
    - prompts/governance_style.txt
    - prompts/fact_check.txt
    - runtime/quality_gate.md
    - runtime/post_checker.md
    - runtime/humanize_rules.md
    - runtime/structure_checker.md
name: finclaw-content-runtime
---

# FinClaw Content Runtime v2

## 使用场景

当用户提出以下任务时，使用本 Skill：

- 生成面向金融、国央企、政务、大型集团的 B2B 技术文章
- 围绕企业级 AI、Agent 中台、云原生 Claw、AI 安全治理、私有化部署、MCP-UI、Skill Hub 等主题写作
- 需要先确认大纲与方向，再写正文，再出配图 Prompt，最后再生成最终 Markdown 文件
- 需要降低文章 AI 感，避免口号化、教导式、绝对化、模板化表达
- 需要引用资料、网络检索、事实核查、SEO 与平台发布适配

## 固定输出规格

- 标题：30-50字
- 梗概：100-200字
- 正文：Markdown
- 微信公众号版：用户要求时在 Stage 2.5 输出 `article_wechat.md`
- 图片：阶段 3 才输出 1 张 16:9 封面图 Prompt + 3 张内文示意图 Prompt
- 文件：阶段 4 才输出最终 Markdown 文件
- 禁止：阶段 1 直接写全文；阶段 2 直接配图；阶段 3 直接输出最终文件

## 项目补充约定

- 后续生成的文档默认减少反引号使用；如无必要，不要给普通中文叙述、常规产品名、普通概念、标题和小标题添加反引号
- 反引号只保留给代码、命令、文件路径，以及少量确实需要区分的协议名或接口名
- 后续文章正文，包括微信公众号排版版本，默认不插入图片占位、HTML 图片占位注释或 Markdown 图片引用
- 微信公众号版本默认面向手机端阅读优化：短段落、清晰小标题、适度加粗、少表格、少代码块、少装饰符号，不使用图片占位
- 图片 Prompt 和实际图片独立保存在单篇文章文件夹内，不嵌入正文
- 搜索相关知识库或做行业背景调研时，需要额外检索中国科技媒体、微信公众号、掘金社区和云技术社区
- 国内媒体与社区检索参考 `configs/china_media_search.yaml`，包括钛媒体、虎嗅、36氪、微信公众号、掘金、CSDN、腾讯云开发者社区、阿里云开发者社区、华为云开发者联盟、火山引擎开发者社区等
- 国内媒体与社区内容优先用于行业语境、传播角度和用户关切参考；涉及法规、数据、公告、标准时仍以官方或一级来源为准
- 每次生成一篇文章时，在 `/Users/ryanz/Local Projece/2026 FinClaw Article/Output` 下新建一个独立文件夹
- 文件夹命名默认使用 `YYYYMMDD_主题英文短名`
- 该文件夹内至少包含：
  - 文章 Markdown
  - 图片 Prompt 文档
  - 后续生成的封面图与内文图

## 四阶段确认流

### Stage 1：确认大纲与方向

只输出：

1. 受众定位与文章目的
2. 3-5 个备选标题方向
3. 章节大纲
4. 关键证据点清单
5. 风险与敏感表达检查

等待用户口令：

- `确认大纲`：进入 Stage 2
- `大纲修改：...`：继续修改 Stage 1

### Stage 2：输出正文，不配图

输出：

1. 标题
2. 梗概
3. Markdown 正文
4. 引用来源

等待用户口令：

- `确认文章`：进入 Stage 3
- `文章修改：...`：继续修改 Stage 2
- `生成微信公众号版本`：进入 Stage 2.5

### Stage 2.5：微信公众号发布优化

在用户明确要求生成微信公众号版本、适合公众号发布、公众号排版优化时执行，输出并保存 `article_wechat.md`。

优化重点：

1. 标题保留传播性，但不夸张、不标题党
2. 正文适配手机阅读，单段通常控制在 2-5 行
3. 小标题要能承接用户滑动阅读，不堆砌口号
4. 重点句可适度加粗，但不要整段加粗
5. 复杂表格改为短表格或拆成解释段落
6. 代码块、密集参数、长引用尽量压缩
7. 结尾自然收束到观点或产品，不强行 CTA
8. 不插入图片占位、Markdown 图片引用或 HTML 图片注释

等待用户口令：

- `确认文章`：如正文与公众号版本均确认，进入 Stage 3
- `公众号修改：...`：继续修改 Stage 2.5

### Stage 3：输出配图 Prompt

输出：

1. 16:9 封面图 Prompt
2. 3 张内文示意图 Prompt
3. 每张图的风格、构图、元素、禁止项

等待用户口令：

- `确认配图`：进入 Stage 4
- `配图修改：...`：继续修改 Stage 3

### Stage 4：输出最终 Markdown 文件

输出：

1. 最终 Markdown
2. 已确认的图片 Prompt
3. 自检报告：标题长度、梗概长度、硬禁词、引用、风险表达、结构完整性
4. 在 Output 目录下为该文章创建独立文件夹，并保存文章与图片相关文件

## 默认风格

默认采用：

- 腾讯云技术社区的方案型结构
- 掘金式项目场景切入
- 少 AI 腔、少模板化连接词、少口号
- 强调企业组织、治理、安全、审计、私有化部署

## 使用优先级

1. 先遵守用户当轮明确要求
2. 再遵守四阶段确认流
3. 再遵守硬禁词和风险政策
4. 再遵守平台风格与 SEO 配置
5. 再使用模板和示例

## 关键原则

- 不编造数据、政策、客户案例
- 对当前信息、法规、行业动态使用网络检索
- 检索行业动态时，同时覆盖中文科技媒体、微信公众号、开发者社区和云技术社区
- 对文章中的关键事实保留来源
- 对安全合规场景避免绝对承诺
- 对产品能力使用边界表达，不夸大
- 每次输出前执行 runtime/quality_gate.md
