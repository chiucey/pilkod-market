---
name: humanize-ai-text
description: >
  学术写作风格工具箱（中英双语，academic writing style toolkit）：论文降AI率、去AI味的风格自查与自然化改写工具（style naturalization & style-pattern scan）。
  写作风格特征自查报告、确定性文本清理（各家模型残留、标点、填充短语）、完整性
  守卫（数字/DOI/PMID/术语必须原样保留）、以及由 agent 执行的风格自然化深改
  （去模板化、去翻译腔、节奏、具体性），让正式文体更清晰自然——特别适合行文
  生硬、模板腔重的作者与非母语（ESL）学者。内置 AIGC
  使用披露合规检查（中国 2025-09 标识办法）与学术诚信护栏：本工具只做写作质量
  自查与改进，不用于误代署名、隐瞒应披露的 AI 使用或对抗学术诚信审查。100% 本地
  运行，零上传，仅 Python 标准库。相关工具：paper-polisher-pro（综合润色）、pubmed-verifier、
  cite-holmes、academic-figures、cn-med-oa、doc-holmes。
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
metadata:
  displayName: 降AI率·去AI味改写｜论文改写·学术表达优化
---

# 论文降AI率 · 去AI味 · 风格自然化（paper-rewriter）

**TL;DR**：`python scripts/pipeline.py draft.txt -o out.txt` → 读报告 →（要排优先级
就 `plan.py --handoff`）→ 按 style_guide 深改 → `verify.py` → 完成。
Word（.docx）直读、英文 PDF 实验性直读；完整性护栏保住每一个数字与引用。

中英双语的学术写作风格工具箱：找出书面语里生硬、模板化、机器腔的表达模式，清掉
机械垃圾，按写作质量原则深改——每一步都带完整性护栏。

> **一句话路由**：改语法、改通顺、按期刊格式润色 → 用润色工具（paper-polisher-pro）；
> 去模板腔、清模型残留、降AI率/去AI味的风格自查与改写 → 用本工具。两者都要时先润色再跑本管线。

## 学术诚信护栏——先读这一节

- **正当用途**：润色自己的稿件；在学校/期刊**允许或要求披露**的前提下，把 AI 辅助
  的文本对齐到自己的行文习惯；清理合规草稿里粘贴带进的模型残留（oaicite/[cite:]
  等垃圾 token）；提升正式文体的清晰度、节奏与具体性。
- **不做的事**：不用于误代署名、隐瞒按规定应披露的 AI 使用、对抗学术诚信审查。
  如果请求的表述是「改到没人看得出来」「帮我瞒过审查」，agent 应拒绝这一目的、
  说明披露义务，并转而提供正当的质量改写路径。运行本技能的 agent 有责任守住这条线。
- **本工具从不动数据**：数字、p 值、置信区间、DOI、PMID、年份、术语全部由
  `verify.py` 守卫（见下）。文字可以改好，事实一个不能少。
- 合规：中国 AIGC 标识办法（2025-09-01 施行）、期刊披露政策与 arXiv 政策要点
  见 `references/compliance.md`——披露义务的主体是作者，不是工具。

## 分工设计

| 层 | 谁做 | 做什么 |
|---|---|---|
| 风格自查 | `scripts/detect.py` | 启发式风格特征报告（模板腔、节奏均匀、公文 boilerplate），供作者自查 |
| 机械清理 | `scripts/transform.py` | 模型残留、聊天客套句、标点归一、语法安全的填充短语替换——只做语法安全层。**何时直接用它**：只需要残留/填充清理、不需要风格诊断时（快、确定性） |
| **质量深改** | **你（agent 本人）** | 按 `references/style_guide_zh.md`（英文用 `_en.md`）：去模板化、节奏、具体性、立场 |
| 完整性守卫 | `scripts/verify.py` | 数字/DOI/PMID/年份/缩写/术语必须原样保留 |
| 前后对比 | `scripts/compare.py` | 特征分变化 + 完整性判定 |

**能改什么（改前 → 改后实例）**——承诺到例子的粒度，不用读完 style_guide 才知道边界：

| 能改 | 例 | 谁做 |
|---|---|---|
| 删八股开场/收尾 | 「众所周知，…」→ 直接进入论点；「综上所述」类仪式感收束降密 | transform `--deep` 自动 + agent 深改 |
| 拆投票式句式 | 「不仅X，而且Y」→「X，且Y」 | transform `--deep` 自动 |
| 清模型残留 | oaicite / turn0search / [cite: 1] / grok_card 等 token 整体清除 | transform 自动 |
| 标点与全角数字归一 | 中文半角标点→全角（小数保护）；２０２５→2025 | transform 自动 |
| 替换黑话/翻译腔 | 「进行…的研究」→「研究」；「在某种程度上」→「部分」 | agent 深改（style_guide 对照表） |
| 调节奏 | 长句连排→长短交错；同款句首连发→换开场 | agent 深改 + stylecheck 验收 |
| 提具体性 | 空泛评价→落到数据/对象（**只重组织表达，绝不编造数据**） | agent 深改（守卫对凭空新增数字告警 W_NUM_ADDED，需人工核对删除） |
| 术语一致性 | HF/心力衰竭/心衰 混用 → 按高频形态统一 | `check_terms.py` 变体组报告 |
| 数字自洽 | 百分比清单合计≠100（划分用语句）/ 同分组前后 n 不同 / p 与 P 风格混用 | `check_stats.py` 报告 |
| 不能改 | 数字、p 值、置信区间、DOI、PMID、年份、术语、引文内容——守卫硬拦 | verify.py 拒绝放行 |

**功能状态（v3.3.0）**——⚠️ 行 = 实验性（可能拒收合法文件或需人工复核）；完整史见 references/errors.md 与各专题文档：

| 能力 | 状态 | 版本 |
|---|---|---|
| ⚠️ **PDF 直读+置信度自评**（嵌字体/ToUnicode 先试抽取封顶「中」；`--pdf-min-confidence 高/中/低` 硬门闸可设；200 篇校准表见 references/pdf_confidence.md） | ⚠️ 实验性 | v1.6–3.3 |
| 五件套+章节感知+句级计划（--handoff）+用户守卫自学习 | 稳定 | v1.0–3.0 |
| 机器退出码（--exit-verdict/--ci）·超时·批量重试·集中异常层·--deep·全角归一 | 稳定 | v2.3–2.9 |
| 风格画像（stylecheck --html/--compare+stats 统计面板）·最佳实践手册·--terms auto | 稳定 | v2.6–3.1 |
| 术语守卫变体组（8 域 27 组 55 变体，--pack 选域）·深改交接块 | 稳定 | v3.0–3.1 |
| 统计一致性守卫（check_stats --batch 跨文件分组 n 聚合+pipeline --check-stats 阶段） | 稳定 | v3.2–3.3 |
| 批量 .pdf 混批 · HTML 报告 · --track 审计 | 稳定 | v1.5–2.8 |

**规模上限**：单块 800,000 字符（块间 2000 重叠）· 文件 50MB · 单步 120 秒。
**PDF 置信度分档怎么用**：高=正常进流程 · 中=抽查 3-5 处关键数字再全量 ·
低=导出 UTF-8 文本重来（`references/pdf_confidence.md` 有真实语料校准表）。

## 自动化与 CI 集成（v2.3.0）

所有判定双口径机器可读：

- **缺省口径（人读流程）**：`verify.py` 独占退出码 0/1/2（1=完整性 FAIL）；
  detect/transform/compare/pipeline 跑完恒 0，判定写在报告里。不要按它们的
  缺省退出码写分支。
- **机器口径**——detect / compare / pipeline 加 `--exit-verdict`（或等价短别名
  `--ci`，v3.1.0 起，方便 CI 里少打字）：
  `0` 干净（低档、无残留）· `3` 风格特征中及以上（需深改）· `4` 命中模型残留
  （先跑 transform）· `1` 完整性 FAIL（仅 pipeline 产出，与 verify 契约同义）·
  `2` 用法错误（不受影响）。**pipeline 是唯一 1/3/4 全档门禁**，CI 推荐：
  `pipeline.py 原稿.txt --rewrite 改稿.txt --terms terms.txt --exit-verdict`。
- **JSON**：`detect -j`（完整扫描结果）、`pipeline --json`（前后分/verify 判定/
  `exit_verdict` 字段/处置提示/深改简报）、`compare --json`（变化量+verify）、
  `plan.py --json`（句级队列+预算投影）。一行门禁示例：
  `python scripts/pipeline.py 原稿.txt --rewrite 改稿.txt --json --exit-verdict || echo "拦截: $?"`
- 两套口径的退出码全表：`references/errors.md` 第一节。

## 快速上手

**普通作者怎么开口**（不用记命令，把这些话原样说给 agent 即可）：

| 你可以这样说 | agent 会做的 |
|---|---|
| 「帮我把这篇论文的 AI 味去掉 / 降一下 AI 率」 | detect 自查 → transform 清残留 → 按指南深改 → verify 守卫 |
| 「这段读起来太模板腔了 / 太像 AI 写的」 | 同上，重点走深改（style_guide 去八股） |
| 「文里有 oaicite、[cite: 1] 这种乱码残留」 | transform 一步清掉（确定性，不碰你的句子） |
| 「先告诉我哪几句最该改」 | `plan.py` 出句级优先级清单（要交接给另一个 agent 就加 `--handoff`） |
| 「改完了，帮我确认没改坏数字和引用」 | `verify.py` 守卫 + `compare.py` 前后对比 |
| 「给我一份风格体检报告 / 量化看看改没变好」 | `stylecheck.py` 画像（单稿体检或 `--compare` 看差值） |
| 「查查数字有没有前后打架 / 百分比加起来对不对」 | `check_stats.py` 统计一致性报告（退出码同 check_terms） |
| 「扫到的 XX 是正常术语，别再报它」 | `learn_guards.py` 固化守卫，类似上下文下不再误报（守卫按上下文窗口豁免，全新语境仍会报） |

**阅读地图**（本文件是枢纽，细节都在一键之外）：初次接触 → 快速上手+工作流 ·
排错 → `references/pitfalls.md`+`references/errors.md` · CI/agent 集成 → 自动化节 ·
能力边界 → 诚实边界节 · 场景打法 → `references/best_practices.md` ·
深改流程操作 → `references/deep_rewrite_guide.md` · PDF 置信度分档 →
`references/pdf_confidence.md` · 程序化调用 → `references/api.md`。

无需 agent——以下全部命令可直接在终端运行。
所有脚本内建 `--help`（完整参数说明）与 `--version`。常用参数语义：

| 参数 | 含义 |
|---|---|
| `--profile general` | 非学术文本：降权八股/公文信号 |
| `--deep` | 确定性句式转换（句首八股删除/不仅合并） |
| `--exit-verdict` | CI/agent 门禁机器退出码（见自动化节） |
| `--structure` | 章节感知评分（IMRaD） |
| `--step-timeout 秒` | 单步墙钟预算（缺省 120） |
| `--terms 文件` | 完整性守卫术语表（extract_terms.py 生成草稿） |

一条命令（自查→清理→深改简报→完整性守卫）：

```bash
python scripts/pipeline.py draft.txt -o out.txt --terms terms.txt
```

- **可视化/批量**：detect/pipeline/compare 加 `--html report.html` 出单文件报告
  （compare 含逐句对照）；`--batch 目录` 整目录汇总（pipeline 出 CSV）。
- **章节感知**：`detect --structure` 按摘要/引言/方法/结果/讨论分章评分，
  方法/结果固定句式按领域惯例降权（只归一综合分，各章原始分逐项展示）。
- **输入格式**：`.txt`/`.md` 直读 · `.docx`（Word）直读 · PDF 实验性直读
  （英文文本型；置信度自评，低=乱码形态——导出 UTF-8 文本重来）。
- **术语表**：`python scripts/extract_terms.py draft.txt -o terms.txt` 自动抽候选，
  人工删改后给 `--terms`；任何运行加 `--suggestions 路径.md` 同时出修订建议工作单。

非学术文本（博客、公众号、公文）加 `--profile general`，学术八股/公文过渡信号
降权 60% 减少误报；默认 `academic` 按学术论文口径标定。

或分步执行（请在技能所在目录内运行，或把 `scripts/…` 换成绝对路径）：

```bash
python scripts/detect.py draft.txt            # 风格自查（-j JSON / -s 只看分）
python scripts/transform.py draft.txt -o step1.txt
# ……按指南对 step1.txt 做质量深改……
python scripts/verify.py draft.txt step2.txt --terms terms.txt
python scripts/compare.py draft.txt step2.txt
```

端到端完整输入输出样例：`references/examples.md`。统一错误码与处置速查：
`references/errors.md`。**集中式常见错误用法清单（24 条）：`references/pitfalls.md`**
——首次实战前先读。Python API 参考：`references/api.md`。常见问题：
`references/faq.md`。

修订追踪：transform/pipeline 加 `--track base` 把机械清理的**每一处修改**记录为
base.md+base.json 可审计清单。

### Agent 调用协议

被触发时先选路径，再执行：

- **触发词**：论文降AI率 / 去AI味 / 去AI味改写 / 降AI改写 / 风格自然化 /
  写作风格自查 / 论文改写 / 学术改写 / 段落改写 / 表达优化 / 去模板腔 /
  翻译腔清理 / 论文润色（限风格自然化语义，见下方消歧） → 跑上面的管线。
  （参数速查表见「快速上手」节；两套退出码表见 references/errors.md——
  均从本节链接直达，避免跨节翻找。）
- **语义消歧（本工具 ≠ 润色工具）**：这里「论文改写」「论文润色」两词用户都可能用——指风格自然化/去模板腔
  （降AI味）。判断标准示例——只关乎语言正确性/通顺的请求路由给润色工具
  （如 paper-polisher-pro）：「帮我改下语法」「这句读不顺，润色一下」「按期刊
  风格改写摘要」；关乎模板腔或模型残留的请求路由给本工具：「这篇读起来像
  AI 写的」「把套话删一删」「文里有 [cite: 1] 这种残留」；两者都要时先润色
  再跑本管线——两个工具互不替代。
- **用户想知道先改哪里** → `plan.py draft.txt -o plan.md`（P0 句级队列 +
  预算投影），再进深改；要把深改交给另一个 agent 执行时加 `--handoff`
  产出逐句指令单（v3.0.0，含守卫铁律与验收命令）。
- **术语称谓混用**（缩写与中文全称、同义术语不一致）→ `check_terms.py 文稿
  --pack <域>`；`--list-packs` 列出八个域包（v3.0.0）。
- **数字前后打架**（百分比清单不凑整、同一分组 n 不同、p/P 风格混用）→
  `check_stats.py 文稿`（v3.2.0，退出码同 check_terms：0 一致 / 1 有问题）。
- **用户想量化验收改稿** → `stylecheck.py 原稿 改稿 --compare`（v2.6.0 风格
  画像差值；触发词：风格画像 / 量化验收 / 深改验收 / style profile）。
- **扫描误报了正当术语** → 不要手改词表文件；用 `learn_guards.py from-text
  术语 样本.txt`（或 `add`）固化守卫——升级不丢，之后每次扫描自动生效。
- **用户只想复核已有改稿** → `pipeline.py draft.txt --rewrite 改稿.txt --terms terms.txt`。
- **用户要求隐瞒 AI 使用、误代署名或对抗诚信审查** → 拒绝该目的，指向
  `references/compliance.md`，改提供正当质量改写路径；不得把本工具用于该目的。
- 退出码：`verify.py` 是严格契约方——`0` 完整性 PASS、`1` 完整性 FAIL
  （修改稿，不修守卫）、`2` 用法/文件错误；`detect/transform/compare/pipeline`
  把判定写在输出报告里，跑完恒返回 `0`（用法/文件错误为 `2`）；
  `check_terms.py` 独立口径：`0` 术语一致、`1` 发现不一致、`2` 用法错误。
  agent/CI 按退出码分支时加 `--exit-verdict`（v2.3.0）：detect/compare 出
  0/3/4，pipeline 出全档 0/1/3/4——见「自动化与 CI 集成」节。
  所有脚本支持 `--version`。

## 工作流（按序执行）

1. **自查**：`detect.py draft.txt`——启发式风格特征报告（套话、句长均匀、
   公文过渡语、模型残留）。报告供作者本人复查；分数是本地启发式，不代表
   任何官方测量，也不说明署名归属。
   （注：`--deep` 的句首套话删除/合并会改变句边界，`verify` 的「新增句子」
   告警对这些改写句属预期——以 `--track` 修订记录为准；管线内路径已自动豁免。）
2. **机械清理**：`transform.py draft.txt -o step1.txt`——清除粘贴带进的各家
   模型残留（`oaicite`/`turn0search`/`[cite: 1]`/`grok_card`/`attached_file`）、
   聊天客套句、Markdown 残留与语法安全的填充短语；中文半角标点自动全角化
   （小数保护）。`-a` 激进档追加破折号降噪、空泛开场删除。`--deep`（v2.4.0）
   追加句式级确定性转换——句首八股删除、「不仅X，而且Y」→「X，且Y」合并——
   只做零信息损失操作，每笔进 `--track` 可审计。人写的干净文本逐字节原样通过（全角字母数字归一除外，见功能状态 v2.9.0）。
3. **质量深改**（真正的活）：可先用 `python scripts/plan.py draft.txt -o plan.md`
   生成句级改写优先级计划（P0 队列：每句带章节归属、命中类别、处理原则与
   预算投影），把深改力气花在贡献最大的句子上；加 `--handoff` 直接产出
   **深改交接块**——逐句「原句+操作指令+守卫铁律+验收命令」的指令单，
   交给执行改写的 agent 可照做（v3.0.0）。然后按文本语言读对应指南——
   - 中文：`references/style_guide_zh.md`（去骨架模板→黑话→节奏→具体化→
     立场→完整性红线）
   - 英文：`references/style_guide_en.md`（小词→拆意义框架→散句化→节奏→
     真归因→亮立场）
   - 逐段改写；事实、数字、引用、术语全部保留。
3b. **量化验收**（`stylecheck.py`，v2.6.0）：段落级风格画像——黑话命中定位
    到段、句长节奏 CV、开场词多样性，逐项标「自然/观察/偏机器」并给指南
    锚点；`stylecheck.py 原稿 改稿 --compare` 看差值，深改验收从凭感觉变
    看指标。档位只是校准提示，不改变任何评分。`--json` 下另有 `stats` 统计面板
    （TTR/虚词比例/句长分位，v3.1.0，信息性口径——看改稿前后的趋势，不判档）。
4. **守卫**：`verify.py draft.txt step2.txt --terms terms.txt`——退出码 1 表示
   有数字/引用/术语被动过：改的是改稿，不是守卫。医学文本建议先做术语表
   （药名/基因名/量表名，每行一个；鼠源基因首字母大写形态如 Myc 也要列入）；
   同义称谓混用（如「肝功能/肾脏功能」「SLE/系统性红斑狼疮」）另跑
   `check_terms.py 文稿 --pack 心血管`（v3.0.0 八个学科域包，`--list-packs` 看全表）；
   数字内部自洽（百分比清单求和/分组 n 前后一致/p 与 P 风格）在**定稿/送审前**
   对原稿跑 `check_stats.py 文稿`（审稿人对数字打架的容忍度远低于文风问题；
   先核对原始数据是笔误还是口径差异，再改表述）；分章分稿写长文用
   `check_stats.py --batch 目录`（v3.3.0 跨文件分组 n 聚合——摘要 vs 方法/结果
   的数字打架单文件检查看不见；只核 n= 记法，散文形态的数字打架需人工）。一条命令全带：`pipeline.py 原稿 --check-stats`。
   守卫还会对「凭空新增的数字」告警（编造防线）与「数字上下文互换」提示
   （两臂/方向核对）。
5. **复核**：`compare.py draft.txt step2.txt`——特征下降 + 完整性判定。
   建议保留前后稿；如学校/期刊要求 AI 使用披露，请如实声明——本报告只是
   质量自查记录，不能替代披露。

## 诚实边界（承诺任何事之前先读）

- 风格分是对写作模式的本地启发式度量，不代表任何外部服务的测量结果，
  更不说明文字由谁写成。永远不要把它当成那种东西来展示。
- 正式学术文体与非母语写作经常被自动化评审误判；如果你是作者本人，请保留
  草稿、版本历史与写作笔记——署名问题靠过程证据解决，不靠风格分数。
- 本工具不与任何外部评审系统交互，不移除官方内容标识或水印，不协助隐瞒
  应做的披露。详见 `references/compliance.md`。
- **检测能力边界（2026-10 真实语料实测）**：对流畅的模型生成文本，本工具的
  风格特征通道几乎不触发——128 篇真实 ChatGPT 文本 98% 低于 28 分，60 篇
  2026 年代模型文本检出率 0%；而能全检出的竞品检测器在人写论坛体上误报约
  50%。**低分不代表「没有 AI 参与」**——本工具定位是风格自查+完整性护栏，
  不是 AI 检测器，也不要反过来用它给「人写」背书。
- **统计通道实验结论（2026-10，373 文件实测）**：句长带集中度是分离度最强的
  单一统计信号（AI 语料 0.68/0.72 vs 人写 0.48/0.47）。已按保守阈值集成
  「节奏规整旗」（≥8 句才判；band≥0.65 或 cv≤0.30）：2023 代 AI 语料 41%
  被标注 @ 人写标注率 3%（低于现行误报基线）。旗标只做提示不改评分——
  规整文体（文献摘要等）也会触发，不能当检测结论用。
- 规模边界：回归测试覆盖至 ~1MB 级文本；扫描为线性复杂度（有界量词，无灾难性
  回溯）。内存约为文件 3 倍；超长稿件建议按章节切分处理，报告更可读。

## 权限与环境声明

供审核者、安全扫描与谨慎的用户查阅：

- 只**读取**你作为参数传入的文件路径（以及 stdin 管道输入，含 `--batch` 目录
  下的 .txt/.md/.docx/.pdf 文件）和技能自带的词表文件（`scripts/patterns_*.json`；
  若你用 `learn_guards.py` 建过用户守卫，还会读自己的 `scripts/user_guards.json`）。
  可自行验证：

  ```bash
  grep -rnE "urllib|requests|socket|subprocess|os\.environ" scripts/ || echo "clean"
  ```

  （本版实测输出 clean——承诺可复现，不是修辞。）
- 只**写入**你显式传入的输出路径：transform/compare/pipeline/plan/extract_terms
  的 `-o`/`--output`、`--suggestions`、`--html`、`--review`（detect.py 的审稿
  报告）、`--report`（check_terms.py / check_stats.py 的一致性报告）、`--track`（写 base.md +
  base.json 双文件）。一个派生例外：`pipeline --terms auto` 会额外写自动术语
  草稿 `<输出基名>.terms.auto.txt`（工具生成、未经人工确认，见工作流说明）。外加一个工具自有数据文件：`learn_guards.py
  add/from-text/remove` 写 `scripts/user_guards.json`（你自学的术语守卫，
  经瞬时 `.tmp` 原子替换落盘）。除此之外无任何写入。
- **零网络访问**——无 HTTP 请求、无下载、无任何 API 密钥。
- **零第三方依赖**——仅 Python 标准库。
- **不读任何环境变量**；不创建子进程；不创建定时任务；唯一会写的临时文件
  是上述 `user_guards.json` 原子替换用的瞬时 `.tmp`。
- 测试语料与开发笔记仅存在于开发仓库，不随发布包分发。

## 自定义

- `scripts/patterns_zh.json` / `patterns_en.json`：词表（含改写建议）、正则信号、
  术语保护（正当学术用法不误报，如 mutational landscape、pivotal trial、
  序列对齐、沉淀反应）、自动修复清单。
- **用户自学守卫**存放在 `scripts/user_guards.json`（由 `learn_guards.py`
  管理，不要手改；`list` 查看、`remove` 删除）。误报词固化请写这里而不是改
  `patterns_*.json`——词表文件升级会被覆盖，守卫文件不会。
- 评分标定系数在 `scripts/hxt_core.py`（`_LANG_K`）；开发仓库 `tests/` 四语料
  （发布包不含）记录了预期分离度。

## 相关工具

- pubmed-verifier —— 批量核验 PMID/DOI 引用真实性
- cite-holmes —— 课题深度调研，引用逐条自证
- paper-polisher-pro —— 综合润色与降重
- academic-figures —— 出版级论文配图
- doc-holmes —— 保持排版的 PDF 精准翻译
- 医学知识库：docsor.cn
