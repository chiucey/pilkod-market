# 按文件分工与保存

本页仅供用户明确要求手动文档分工时使用，不是后台不可用时的自动回退。普通聊天分析统一按 [后台分析交接](dispatch.md) 处理；原生后台会话沿执行器上下文直接执行，不读取本页主协调规则。

本节供主 Agent 准备输入、协调分析和核对结果。文档子任务负责分析与保存，依据本轮公开工具核对能力；确认缺少所需工具时，调整该文件为子任务只读分析、主 Agent 原样保存。子 Agent 执行的完整规则在[文档分析规则](document-analysis.md)。仅适用于已获委托的普通审阅；讨论封套仍遵守[只读讨论](context.md)。

## 主 Agent 准备本次范围

主 Agent 保留真实 `workRef`、`reviewId` 及每份文档的 `documentId`、`assetVersionId`、获授权列或工作项范围和宿主任务引用。本地 MCP 调用在顶层携带原 `workRef`，`list_review_templates` 除外；不通过插件目录、端口或 SQL 读写业务数据。

新建审阅时，主 Agent 从 `open_tabular_review`、`enqueue_review_work` 和 `get_tabular_review` 的紧凑回执取得文档、列与工作项范围并按 documentId 分组（open/get 的文档、列、版本与工作项统一位于 `workspace`）；续审时保留交接请求给出的 workItemIds。不将未获委托的新目标加入本轮。直接保存模式由子任务用 `list_review_cells` 的 documentId 及本次 workItemIds / dimensionId 筛选查询其未完成目标；只读模式由主 Agent 查询后交接。沿 nextCursor 翻页并保持原筛选，分页大小不决定分析批量。

直接保存模式由子 Agent 按交接的不可变 assetVersionId 调用 `prepare_legal_document_text`，保留返回的 textFilePath、metadataFilePath、正文 SHA-256、UTF-16 长度、truncated 和有效期，再用 Host 当前文件工具读取；只读模式由主 Agent 查询目标并准备这些文件引用后交接。同一文档跨列复用，主 Agent 不搬运全文；读至 EOF 只表示保存正文已读完，truncated 为 true 仍不完整。跨文件判断分别交接获授权的相关材料，明确目标文档与参考文档，证据仍绑定目标文档。

用户明确要求手动任务包分工时，先用 `prepare_review_dispatch` 传固定 reviewId/workItemIds，沿 nextCursor 保持原筛选。每份包交给对应文档任务，以 `open_review_document` 准备最新上下文。`get_review_dispatch` 只用于核对原范围状态，不授权扩展；所有相关文档任务退出后才用 `release_review_dispatch` 核对与清理。普通聊天仍用 `start_review_analysis`，不进入这条手动路径。

## 派发与复用

- 每份文档交给一个子 Agent 处理本次获授权列。交接须包含可核对的 documentId、assetVersionId、列或 workItemIds 范围、材料边界、明确的保存分工及已确认可读的完整[文档分析规则](document-analysis.md)绝对路径。每个任务提示明确写出 `analysisRulesPath`，要求子任务首轮完整读取后执行，不重新加载整个 Skill。不得用自己的摘要替代完整规则；子任务无法读取规则文件时，才内联完整正文。直接保存时另交接真实 `workRef`、`reviewId` 及下方保存/恢复要求；只读时提供规范文件路径、版本回执、列要求与反馈，并原样交接当前 `set_cell_analysis` 的分析字段说明，不另写格式规则。不能仅给 Skill 注册名或让子任务自行找规则，也不要把全文或摘录塞进任务提示。
- Pilkod 的文档任务明确选择内置 Pilkod：调用 `task` 时设置 `agent_name: "pilkod"`，不要因为任务范围明确就选 Worker，也不选 Explore 或 Verifier。核对创建回执中的实际角色；仅在提示正文写“Pilkod”不等于选中了它。其他 Host 或当前公开契约不提供 Pilkod 时，按公开目录选择具有文件读取能力的任务并核对 Legal MCP，缺失时采用下方只读分工，不猜角色或修改宿主配置。不要靠显示名、提示中的 `@Pilkod For Legal` 或文本称呼推定插件注入，也不把目录未列 MCP 当成工具不存在。各子任务用当前公开工具目录及可用的发现入口核对能力，有工具即继续本文件的分析与保存，不要求先完成一份能力试跑。缺少能力时仅回报具体缺口，主 Agent 调整该文件分工，不反复猜角色、改宿主配置或查找私有工具通道。
- 直接保存模式下，交接时明确“核验完成一格就立即单格保存，不等待其他列或引文批处理”；子 Agent 按完整文档分析规则并行查询本文件未完成目标与准备固定版本正文，再并行读取 metadata 与规范 TXT；分页读至 EOF，汇合核对 documentId、assetVersionId、正文哈希、列要求、反馈和 expectedCellRevision 后开始分析。按完整规则生成结果后，用 Legal MCP 保存已就绪的 Cell，检查逐项 accepted / rejected，并只处理本文件的拒绝或未知结果。两种模式均不得重新导入、建表、开页、修改规范文件、寻找插件目录/端口、使用 SQL、扩大范围或再派生子任务。
- 委派方式、参数、并发、等待和续派遵循 Host 当前公开契约。采用宿主支持的非阻塞方式；独立文件在当前容量内全部先派出，主任务继续派发或核对已完成文件，不逐个等待，也不设首文件完成门槛。维护已创建、运行中、已完成和待派发的文件清单。公开契约或本会话容量回执已给出上限时，只填充剩余名额；未知容量遇到首次拒绝后记录容量并等待已创建任务完成，不在没有名额释放时重试。一次等待获取完成事件并补位，不能把未创建任务当成已派发。实际创建回执才证明已委派，实际重叠运行才证明并行。
- 新增文件只处理新增行及其获授权列；新增列只处理本次请求范围内的新列目标，保留已有 Cells。反馈或重新分析只处理获授权的受影响列。能续派时优先复用原文档子 Agent、同一版本的已读正文与上下文，只补充变化和本次目标；原任务不可恢复或宿主不支持续派时，重新交付文件引用及完整规则。需要重新读取而路径失效时，沿用原 workRef、assetVersionId 重新准备，不猜路径；以当前文档版本和目标关联回报，过期或重复回报不能重复保存。

## 直接保存与只读分工

负责保存的一方核对文档版本、授权列和结果对应本次输入，检查依据、条件与不确定性未丢失；引文定位由插件在写入时校验。
保存时仅映射权威文档、列标识并补齐 Cell 版本和幂等元数据。
输入不足、越界或分析有误时只重做受影响列，不将工具错误写成法律结论。
完整阅读并核对材料后，已有核验完成的结果即可提交；每核验完成一个 Cell，立即按当前提交通道保存，默认用平铺单格参数调用 set_cell_analysis，再继续下一格；不要攒成整行或整批提交。
不要仅为等待其他未就绪列而延迟已有结果，也不得为提前首格跳过全文或该格所需交叉核对。
不重复提交在途或已接受项。

负责保存的一方默认用 `set_cell_analysis` 的平铺参数 `{reviewId, expectedCellRevision, idempotencyKey, analysis}` 保存当前格，不传 items。
analysis 必须显式填写 conclusion：有依据的有效值使用符合列格式的字符串，没有结论时使用 JSON null，并在 explanation 的非空 text 中解释原因；结果表达遵循[文档分析规则](document-analysis.md)，判断依据与必要限制写入 explanation，通过引用 ID 关联 citations 中的原文，不将解释填入结构化值。
有相关原文时提供 citations，没有相关原文时允许空数组；不编造或引用无关条款。
每格必须显式填写布尔字段 isLowConfidence，依据充分且结论明确时填 false，存在实质不确定性时填 true。
新分析省略 explanation 会清除先前说明和证据，不将旧说明沿用到新结论；仅缺少影响理解的必要说明时补齐，不为填充可选字段重复分析。
没有已知输入变更或版本冲突时，直接使用查询返回的 expectedCellRevision，避免在写入前逐格重新查询；插件会拒绝旧版本，冲突后才回读受影响格。
每项使用独立幂等键，不传 workItemId、analysisRunId 或租约。
普通文档分析每次只提交当前已就绪的一格；批量接口能力不是等待其他格的理由。
逐项检查 accepted / rejected：completed 格保留；provisional 格尚未完成；有 repairFile 时核对 changes 仅修引文，优先原样按 repairFile.arguments 调用 submit_cell_analysis_file，不重生成法律字段，再检查保存回执。
无 repairFile 时按 pendingEvidence 中的 citationId 修复，用 accepted.cellRevision 和新幂等键提交 citationPatches。
未知结果重试沿用完整原参数和原键，明确拒绝后修改参数使用新键。
直接保存的子任务成功后只回报文档、已完成列、暂存待完善列、被拒列、是否仍有本次未完成目标和必要错误，不重复返回已保存业务正文。

首次明确参数结构拒绝（缺必填字段、字段层级或类型错误）后，负责保存的一方按[结果文件提交](result-files.md) 修正并写入请求文件提交，当前格及本次文档任务后续格改为文件通道，不受 8 KiB 限制。
明确拒绝修正后使用新键；未知结果保留完整原请求，文件提交原样重交同一文件，不切通道，普通业务拒绝和版本冲突仍按原规则处理。
文件通道不可用时报告具体阻碍，保留已保存格及其他就绪结果，不自行转派绕过分工；只读模式始终不写入。

主 Agent 对明确故障只跟进受影响列；全部子任务结算后，按稳定文档/列范围查询未完成 Cell，再读取整体完成与关注数量，一次收尾。完成态不依赖只适用于活动任务的工作项筛选，不逐个回执反复重读整表。查询和任务上下文使用分析专用字段，读取方式见[文档分析规则](document-analysis.md)；写入回执不包含界面同步快照，回执中省略的字段不表示业务数据已被清空。

只读分工：主 Agent 用同一 documentId 与本次范围筛选 `list_review_cells`，保留列要求、反馈和 expectedCellRevision；沿固定 assetVersionId 准备规范 TXT 与 metadata，把真实路径、版本回执、完整分析规则及当前 `set_cell_analysis` 的分析字段说明原样交给具备文件读取能力的子 Agent。子任务自行读至 EOF，返回已就绪列的业务字段；主 Agent 只映射目标并补齐版本、幂等元数据，原样调用 `set_cell_analysis`，不改写结论、说明或引文，收到即保存。拒绝项按下方规则局部处理，需要补充依据或判断时续派原文档任务。没有可用的文件读取子任务时才由主 Agent 直接处理。只对受影响文件调整分工，保留已接受结果。

每条 citations 默认只传稳定 `id` 与逐字 `quote`，说明通过 citationIds 关联；省略 locator，插件绑定文档并生成证据页码与坐标。列要求关联 PDF 页码也采用此流程。仅实际歧义需要消除时，依据候选上下文填写 occurrenceIndex 或经核实的 UTF-16 坐标；确定性辅助或 repairFile 已提供的定位原样保留。pageMap 用于确保每条引文在同一 PDF 页内，跨页内容拆成多条，省略页码不绕过跨页校验。

## 人工核验与结果变化

Agent 校验或 MCP 接受结果不等于用户已人工核对。用户在界面核对或保存手动编辑后，核验标记只对应当前结果版本；Agent 调用 `correct_cell` 不自动标记人工核验。重新分析、提交反馈或修改列要求会使核验失效。核验保留原低置信度标记，不表示风险或依据缺口已经消除，不为清除提醒而改写分析事实。

## 只恢复被拒或未完成范围

- 证据待完善或拒绝：`accepted.status=provisional` 表示结论已保存但未完成。有 `repairFile` 时，核对 changes 中的目标和转换摘要，仅修证据且保留原法律字段后，优先用原 `repairFile.arguments` 调用 `submit_cell_analysis_file`；准备好的修复请求不是完成回执，不重新写整格。文件提交未知时原样重交同一文件与内含键；有冲突回读重评，不换版本覆盖。无 repairFile 时按 pendingEvidence 的 proposedEvidence、issueCode、message 识别并修复对应引文，不把校验后索引盲用于原输入顺序。补交使用该回执 cellRevision 和新幂等键，不创建 retry_cell。硬拒绝仍读取 rejected.details，版本不变。坐标或页码拒绝若携带 `recovery.strategy: "quote_only"`，表示插件已确认引文在同一固定正文中可唯一定位；只用 `recovery.evidence` 替换 evidenceIndex 指定的那一条，保留其他证据与业务字段，仅以新幂等键重试被拒的 Cell item，再检查 accepted / rejected。没有该恢复回执时，不自行删定位字段绕过歧义：`issueCode: "quote_ambiguous"` 根据回执候选上下文消歧；`issueCode: "quote_mismatch"` 由文档子任务从规范 TXT 回读对应段落、原样修正；页码问题核对 pageMap。只处理受影响列，不凭记忆改空白、拼接引文或重析整表。仅 rejected 不修改 Cell 版本；provisional 已推进版本，不重复 completed 格。子 Agent 无法恢复时，把拒绝回执和受影响列交回主 Agent 续派。
- 版本冲突：回读最新 Cell、列要求与反馈，交给对应文档子 Agent 重新评估；不能只换版本重交旧结论。保留人工修正，不写回已移除目标；已完成格仅在用户明确重析或提供反馈时建立待办。
- 目标不存在或不匹配：核对原查询与目标映射，不新建目标代替。retryable 为 false 时不以相同参数盲重试；未知保存结果先核对原操作，不反复换键，不用 correct_cell 或删除成果绕过验证。
- 正文文件失效或需有界排错：沿原绑定与资产版本重新准备；必要时用 `read_legal_document_text` 读取受影响片段，不以片段代替应读完的全文。
- 变更结构或输入前协调在途分析及保存；需要审阅级 expectedRevision 时，相关保存结算后读取最新版本提交，再按回执分发新增范围。旧任务回报仍须按当前输入和 Cell 版本校验。
- 从第一页复查本次筛选内的剩余目标，将遗漏交给对应文档任务。派发、回报或查询为空都不等于整表完成；仅核对和汇报本轮范围，保留已保存结果和正式结构。
