---
name: company-brief
description: 借助 MiniMax Finance Data MCP或其他数据获取方式，为 A 股、港股或美股上市公司产出带来源支撑的速览，并默认通过 visual-page skill 生成 GUI/HTML 页面。涵盖公司档案、财务、行情、估值、股本、行业与关键事件。默认中文叙述、兼顾中国大陆用户习惯；不用于私营公司、基金尽调或完整投资备忘录。
---

# 多市场上市公司速览

## 启动顺序

1. 先读 `references/finance-mcp.md` 与 `references/market-rules.md`，确定数据通道规范与市场规则。
2. 判断证券所属市场，再选择 `a_stock` / `hk_stock` / `us_stock` 调用 `resolve_entity`；不要绕过候选直接猜内部 `code`。
3. 按任务所需最小化调用 `call_api`，逐项落实公司档案、财务、行情、估值、股本、股东、分红融资与事件数据。
4. 涉及板块对比时：A 股优先 `industry` / `sw_industry` / `concept`，港股优先 `hk_industry`，美股通过公司或行业接口拿到对应分类。
5. 数据登记表中必须保留：市场、交易所、当地时区、截至日期、报告期、单位、币种、会计准则与复权口径。

## 数据来源原则

- 正式公告与定期报告优先用于财务与事件事实。
- MiniMax Finance Data MCP 用于结构化的财务、行情、估值、股本、行业与宏观数据。
- 用户提供的模型、跟踪器、研究材料用于补充投资者视角。
- 出现冲突时如实记录冲突，并以正式披露为最终基准。

## 交付物意图收集

按 `references/output-guidelines.md` 排序的载体优先级执行。本工作流的自然产物是一份经过优化的 GUI/HTML 发行人速览；除非用户主动要求轻量回复，否则不要默认走纯对话输出。GUI/HTML 产物必须通过 `visual-page` skill 完成，本技能只负责研究内容、证据、页面结构 brief 与业务优先级。

在为新的独立、面向读者的核心交付物开始收集来源或动笔分析之前，加载 `references/output-guidelines.md`，并只就"真正会改变结果"的格式 / 深度 / 受众 / 重点问题进行确认。

## 目的

为上市发行人产出有来源支撑的基线档案，让下游公开股票投资工作流从一致的事实视角起步。默认产物按设计是"发行人基线"，而不是 memo、模型、推介或建议。

当需要快速搭建上市公司画像时，本技能用在如下工作流之前或其中：comps、DCF、三表模型、业绩分析、模型更新、多空推介、备忘录、会议准备、论点跟踪、风险 / 仓位规模、对冲、事件、催化剂、股票风险信用信号，以及演示文稿 / 报告制作。

除非其他格式优先级更高，否则把完整内容包交给 `visual-page` skill 生成一份精炼、经过优化的 GUI/HTML 速览；层级由发行人的商业模式与所要求的审阅视角共同决定。仅当用户主动要求轻量回复时使用对话输出。如果工作扩张到详尽论点构建、情景分析、承销分析或完整投资观点，应当把基线移交给 `initiating-coverage`、`memo-builder` 或对应主导工作流。仅当用户明确要求标准化仪表板、可复用仪表板模板，或要求由结构化 payload 驱动渲染时，才准备结构化展示 payload；HTML 文件本身仍由 `visual-page` skill 负责完成与交付。

## 不适用情形

- 私营公司、由财务投资人持有的资产、私募基金、LP / GP 尽调对象、供应商、客户或商业交易对手。
- 基金 / 资产管理机构尽调档案。
- 市场图谱、买方名单、私营公司项目筛选或尽调工作计划。
- 完整备忘录、估值模型、交易推介或投资建议。
- 不要把更广义的投资 / 业绩 / 可比 / 信用 / 推介请求压缩成速览；应当路由到主导完整分析的对应技能。

## 不可妥协的纪律

- 保留用户提供的来源材料与工作成果。
- 来源使用顺序：用户上下文 / 文件 > 实际可调用的运行时应用 / 连接器 > 一手来源 > 用户提供的数据商导出 > 可信二手来源 > 已标记的假设。
- 使用 `financial-source-of-truth` 处理来源层级、陈旧检查、引用、冲突，以及事实 / 假设的纪律。
- 当源财务数据杂乱时，先走 `financials-normalizer` 或 `excel-data-cleaner`。
- 永远不要伪造缺失的事实、指标、评级、债务、估值、持仓、客户或 KPI。
- 区分并标记：事实、计算、预测、管理层陈述、用户调整、假设、缺失字段、置信度。
- 在面向读者的产物中，把内部证据标签翻译成普通投资者用语，例如 `Reported`、`Company-defined`、`Derived`、`Not yet sourced`；只在支持材料中、或在用户明确要求时保留精确的证据标签。

## 工作流

1. **分类画像。** 在 `public_company` / `equity_issuer_profile` / `public_sector_peer` 中选择正确档案类型；确定下游用途。
2. **建立来源清单。** 维护 `source_id`、来源名称 / 类型、所有者 / 提供商、截至日期、检索日期、期间、位置、时效性与备注。
3. **提取档案关键事实。** 只填入与用途相关、且有来源支撑的业务、分部、地区、管理层、指标、估值、资本结构、KPI、近期事件、风险与证据缺口字段。
4. **打证据与置信度标签。** 使用 `references/source-and-evidence.md` 中的标签以及 `high` / `medium` / `low` 置信度。
5. **铺排速览。** HTML 速览路径下，先构建 `visual-page brief`：investor read、四到五项有助于决策的指标、核心业务与盈利驱动、估值背景、紧凑的催化剂 / 风险、重要证据缺口、来源说明，以及下一分析路径建议；再交给 `visual-page` 生成页面。
6. **守住基线深度。** 不要让实时事件、冗长的缺失数据登记、海量尽调问题或情景工作把发行人基线挤掉；这些工作变成核心时，升级到主导完整分析的工作流。
7. **执行 QA。** 确认主体身份、期间、单位、币种、来源、置信度、陈旧 / 冲突数据、衍生计算依据，以及面向读者的可读性。

## 确定性辅助脚本

```bash
python scripts/validate_brief_json.py path/to/brief.json
python scripts/build_brief_markdown.py path/to/brief.json output.md
```

这两个脚本只负责对结构化输入做校验与渲染。它们不会去抓取数据，也替代不了来源审阅。除非用户明确要求 JSON 或 Markdown，否则它们的产物都是支持性的、或用作渲染器输入。

## HTML / 仪表板交付

需要 HTML 速览、展示页或标准化仪表板时，必须无损调用 `visual-page` skill。调用前先把公司研究整理成一个页面 brief；调用后由 `visual-page` 负责创建自包含本地 HTML、选择输出路径、验证可直接打开，并用 `<media type="file" src="/absolute/path/to/index.html" caption="..."/>` 交付。不要在本技能内自行实现 HTML 外壳、CSS、JS 或旧仪表板渲染器。

交给 `visual-page` 的 brief 必须包含：

- **页面模式**：通常选择 `Long-read / Report`；若用户要求可筛选表格、密集对比或同业面板，选择 `Data UI`。
- **视觉主题**：要求 `visual-page` 使用冰白纸背景、液态玻璃风格；不要使用 `visual-page` skill 里的默认配色方案。上涨、改善、确认、利好、估值/盈利上修等好事，以及所有强调色，统一用中国红 `#c0322f`；下跌、恶化、削弱、利空、估值/盈利下修等坏事，统一用稳绿 `#15803d`。
- **输出路径意图**：若用户给了路径，要求 `visual-page` 使用该路径；若没有，要求它按 `/tmp/visual-page/<issuer-brief>/index.html` 形态创建独立目录，不覆盖旧页面。
- **首屏结构**：H1 为发行人 / 证券名；首屏一屏内展示 investor read、as-of、来源状态、四到五个高信号指标，不用营销式 hero。
- **组件映射（深度耦合 visual-page 组件，每个都带交互）**：
  - 高信号指标 → **可展开 KV cards**：默认显示指标名 + 当期值；hover 触发液态玻璃浮层 / 点击在卡内就地展开期间、单位、来源、证据标签与置信度。卡片用 visual-page 的 `rounded-2xl` + diffusion shadow + `hover:-translate-y-0.5`，正向值（同比改善、估值上修）数字着中国红 `#c0322f`，负向着稳绿 `#15803d`。
  - 分部 / 盈利驱动 → **带切换的 bench bars**：在 visual-page bench-bar 基础上加一个「绝对值 / 同比 %」分段切换（segmented control，激活态中国红），切换时 `bar-fill` 宽度做 200ms 过渡；超过 8 个分部时折叠为「展开全部」。
  - 业务 / 收入链条 → **arch-row**，每个 arch-block hover 时升起液态玻璃 mini 说明卡（描述 + 来源），不再用静态 `desc-mini` 死贴。
  - 催化剂 / 风险 → **可筛选 2×2 matrix**：四象限上方放筛选 chips（全部 / 催化剂 / 风险 / 近端 / 远端，激活态中国红），点击高亮对应象限条目；条目过多时单元格内滚动而非撑高页面。
  - 估值背景 → **KV card 组**，倍数旁可 hover 看口径（trailing / 衍生 / 同业）与 as-of。
  - 下一分析路径 → **step timeline**，每个节点 hover 升起说明卡，渐变主轴用中国红→稳绿但仅作装饰、不承载涨跌语义。
  - 来源台账 / 证据缺口 → **可排序 + 行内展开表**：表头点击按 as-of / 置信度排序（升降箭头指示）；每行点击就地展开来源全名、检索日期、原始证据标签；证据状态用 chips（Reported / Derived / Company-defined / Not yet sourced）。
- **交互规格（全部用内联 vanilla JS + CSS，禁止额外重依赖；继承 visual-page 的 BANNED 清单：无 AI 渐变 / 霓虹 / Inter）**：
  - 顶部 **sticky 锚点导航**：Investor read / 盈利驱动 / 估值 / 催化剂风险 / 证据缺口，当前区块高亮中国红，点击平滑滚动。
  - 所有可点击元素必须有 hover 态、`:focus-visible` 键盘可达、`cursor:pointer`；展开 / 折叠 / 排序 / 筛选 / tab 切换一律 ≤200ms 过渡。
  - 移动端（<768px）：sticky nav 收成横向滚动条或汉堡；所有表格转为单列卡片，禁止横向滚动；segmented control 与 chips 自动换行。
  - 交互只增强信息密度与可读性，不得制造数据噱头；首屏一屏内仍要给出 investor read 与四到五项高信号指标。
- **可视化规则**：同业或分部 2-8 项对比用带切换的 CSS bench bars；只有超过 8 个时间点的财务 / 股价序列才引入 Chart.js（`font.family='Outfit'`、正向序列中国红、负向稳绿、`borderRadius:6`）；业务 / 收入链条 2-3 节点用 hover 增强的 flow-node，4 节点以上才用 Mermaid 并允许点击节点跳转对应章节。不要为少量数据点引入重库。**用到 `<div class="mermaid">` 时，务必提醒 `visual-page` 在 `<head>` 加载 `mermaid.min.js`（CDN）并调用 `mermaid.initialize`，否则图不渲染。**
- **必须保留的业务语义**：事实 / 计算 / 预测 / 假设要可见地区分（用 chips 或角标，不要靠颜色单独承载，避免与涨跌红绿混淆）；缺失持仓、因子、一致预期等字段整合进可展开的 evidence gaps 区块，不要散落成噪声表。
- **交付要求**：要求 `visual-page` 产出完整 GUI/HTML、做响应式与本地打开检查、确认每个交互元素都有 hover / focus 态且无断链，并以 `<media />` 返回文件。

## 何时调用支持技能

遇到来源冲突、陈旧数据或杂乱表格时，直接做来源分层、事实 / 假设标注与结构化清理。若环境另装了财务标准化或电子表格清理类技能，可顺势调用；不存在时不要阻塞速览交付，但要把未解决的数据问题显式披露。

## 输出契约

**面向用户的回复需要包含：**

1. 已创建速览：主体、档案类型、范围、来源、截至日期。
2. 关键结论：3–5 个要点，并标记预测 / 假设。
3. 指标表：有助于决策的指标，含期间、单位、来源、置信度。
4. 风险 / 缺口：陈旧、冲突、缺失事实、证据标记。
5. 建议的下一步或下游交接。

**独立 HTML 速览的首读结构应当保持精炼：**

1. Investor read 与四到五项高信号指标。
2. 盈利驱动表，或精炼的驱动卡片。
3. 仅有历史或衍生估值倍数时，可见标题使用 `Valuation Context` 或 `Trailing Valuation Snapshot`；除非有远期预测、同业、目标价或显式市场预期支撑，否则标题中不要出现 `Debate`。
4. 紧凑的催化剂与风险矩阵。
5. 重要证据缺口、来源台账、下一分析路径。

不要仅仅因为 HTML 有空间，就把速览撑成完整首次覆盖报告、冗长尽调问题集、情景包或投资建议。

## HTML 内容交接要点

当用户要求或意图收集后选定 HTML 时，将以下内容作为完整设计 brief 交给 `visual-page` skill，不要在本技能内直接写 HTML：

- 先呈现基于事实的 investor read 与核心盈利驱动问题；发行人基线与盈利驱动是首要对象。
- 优先使用四到五张差异化的指标卡、一组盈利驱动对比对象、一个精炼的估值背景对象与一个催化剂 / 风险对象，避免重复仪表板面板。
- 当当前成交、传闻、监管事项或其他实时事件重要但不属于当下重点时，把它放进 investor read 与 catalyst / risk，并在证据缺口区块中标记缺失的一手证据；除非它直接改变某一章节，否则不要重复贯穿盈利驱动、估值与倍数摘要。
- 通过精炼的证据缺口块，明确显示缺失的持仓、头寸、因子或一致预期字段；除非这些字段属于审阅重点，否则不要做冗长无来源的字段表。
- 用自然语言表达可见的证据状况，不要把 `fact_source_reported` 或 `missing_required_source` 这类内部标签裸露给读者。
- 引用要可追溯且可读：不要把代码、年份、日期、数字区间、指标名、产品标签拆成多个独立带链接的词元。
- 明确要求 `visual-page` 按其工作流完成本地 HTML 验证与 `<media />` 交付。

## 参考资料索引

- `references/source-and-evidence.md`：来源层级、引用、陈旧检查、标签、冲突。
- `references/profile-templates.md`：通用单页与档案专用模板。
- `references/metric-library.md`：指标类别、行业叠加、KPI 指引。
- `references/quality-checks.md`：质量自检清单。
- `references/integration-guide.md`：公开股票投资上下游交接。

## 公开股票 PM 判断层

对重要的速览，在定稿前加载 `references/pm-judgment-heuristics.md`。

- **受众模式**：`long_only_pm`、`long_short_hf`、`sell_side_research`、`etf_index_diligence`、`public_equity_diligence`。
- **场景模式**：`long_only_baseline`、`hf_baseline`、`sell_side_coverage_starter`、`etf_index_constituent_profile`、`public_diligence_baseline`。

**必须具备的 PM 判断：**

- 保持速览以事实为基底，但要把下一分析路径显式呈现。
- 可用时纳入对投资者有用的字段：市值、企业价值、自由流通、ADV / 流动性、指数成分身份、ETF / 被动持股及资金流相关性、主要持有人、卖空、可借券 / 拥挤度、因子敞口、持股集中度、公司治理、资本配置、卖方覆盖、一致预期格局、资产负债风险，以及关键经营 KPI。
- 持仓、头寸、可借券、流动性、因子、一致预期字段不可用或陈旧时，明确标注 as-of / 来源要求，不要静默省略。在面向读者的 HTML 里，把非核心缺口整合进一个精炼的证据缺口区块，不要展示冗长低信息量的登记表。
- 不要把速览变成投资建议；投资决策路由到首次覆盖、备忘录构建器、多空推介或论点跟踪器。
