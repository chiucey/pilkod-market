# 验证记录

## OMP 来源接入（0.6.0）

- 新增独立 `omp_source.py` 与 `--source omp`，复用现有清单、目标写入、批次、去重和恢复流程。依据 OMP 官方 commit `b4e288210c052e1c62042515e739919c9304f14e` 的 V3 类型、标题槽、上下文重建、消息和目录规则；保留原五来源适配器实现。
- 聚焦执行 27 项检查：OMP 9 项、共用迁移任务 10 项、Pi 回归 8 项。OMP 场景覆盖 UTF-8 标题槽、旧 V3 header、来源只读、fork/子代理、分支、两次压缩与 reset、跨压缩工具结果、失败/重试/悬空调用、中断连续性、原轮次身份、Python/bash、内联文本与附件降级、敏感元数据过滤、profile/XDG 隔离、链接与损坏/未知格式拒绝。公共矩阵增加 OMP，覆盖单个/多个/全部、失败隔离、重试、提交前后进程硬退出恢复、workspace 绑定和重复迁移。市场 CI 通过 `tests/test_omp_session_migration.py` 纳入 OMP 专项。
- 使用普通、两次明文压缩、`/clear` 后新输入三条合成会话，在 Archon `8ee84dddfb99fdd83c76c25a692c393d59b06da8` 的真实 schema 和 production canonical history provider 上执行现有 `verify_codex_native.mts`（`SOURCE_TYPE=omp`、`SOURCE_ALL=1`）。展示/有效消息数分别为 2/2、3/2、3/1；初始化、追加重读、续聊追加后重复导入保留、既有种子会话不变检查通过。合成源 JSONL 字节未变。
- 完整 marketplace 校验通过（main 基线，80 个插件）；改动 Python 的 Ruff 格式与 `E9,F,I` 检查、`git diff --check` 通过。未运行全仓测试。
- 边界：样本按已核对源码构造，未安装/调用 OMP writer，未验证用户真实 OMP 会话、真实模型续聊、Windows 真机和超大会话容量。当前有效的 remote/snapcompact、非空 preserveData/provider replay、实验性 context rollover/notes 明确拒绝；图片/blob 字节需显式接受仅保留说明。仅处理末尾持久化分支，不恢复 OMP 内存状态。没有修改正式 profile、覆盖已安装插件缓存或发布市场。


## 2026-09-27 OpenCode 旧版 SQLite 兼容（0.5.1）

- 新增 schema 路由与独立旧版解析器，复用 opencode 身份、转换、预览、批次及恢复。依据 OpenCode v1.18.32 commit 545f51d26cc39a907d2867492d498d9607ea5fa4 的 sql.ts / message-v2.ts，不修改来源数据库。
- 插件聚焦 147 项通过，包含 8 项旧结构专项；公共矩阵增加旧结构的单个、多个、全部、失败隔离/重试、提交前后硬退出恢复和重复导入。专项覆盖 1.14/1.18 版本字段、WAL、生命周期表、多次压缩及保留片段顺序、失败/未完成压缩、工具输出裁剪、附件 opt-in、回退和混合结构拒绝。
- 分别使用旧结构与 V2 的三会话模拟库执行 --all，接入桌面端真实 schema 和生产 canonical history provider。均通过初始化、追加重读、重复迁移保持续聊、原有种子会话不变。旧版双压缩样本为 3 条展示 / 2 条接续，V2 压缩样本为 2 / 1，其余普通样本为 2 / 2。此处未调用真实模型，不作为 LLM 语义验收。
- 未访问反馈用户的 Windows 数据库或 F: 诊断文件，不声称其 313 条会话全部兼容。Windows 路径仅为合成测试；Windows 真机、大库容量和完整来源样本尚未验收。JSON 文件布局与混合正文投影尚不支持，未知内容明确失败，原库无需升级。

日期：2026-09-20。当前产品：Agent 会话迁移 0.5.0，当前来源适配：ZCode、Codex、Claude Code、OpenCode、Pi Agent。以下先记录语义修复与真实续聊验收，再保留先前版本记录；旧记录中的未验证项和格式假设不代表当前结论。

## 0.2.1 ZCode 主会话筛选与旧版归档（2026-09-20）

依据本机 ZCode 3.12.3 的 `glm/zcode.cjs`：`Jfe/isTaskListSessionType` 仅允许 interactive、fork、workflow_parent；子 agent 创建时显式设置 subagent_child；用户 fork 同时设置 parentID 和 fork 类型。该源文件 SHA-256 为 `da61b0663336a65f7cce3dec223678794ccaa58158e304fc0d97b695434a8f01`。

- 迁移 inventory、load_inventory 和 scan 使用来源会话类型；不靠标题或 parent_id 推测。跳过内部类型并报告 excludedSessions；显式选择或旧预览继续 apply 都不能绕过筛选。缺字段旧格式保持兼容，未知非空类型报错。
- 加入 8 项回归（含多类型子案例）：主/子/孤立子任务、用户 fork、旧格式、未知类型、单独选择、全量/旧预览、旧导入归档预览/幂等/保留性、运行中/追加输入/存档篡改拒绝和归档写入失败回滚。Marketplace 197/197 通过；包含插件 102 项测试。
- 原生 verify_native.mts 使用真实 Runtime schema 和合成 fork/子 agent：只创建 fork 的目标会话，子 agent 不进入列表；原有搜索、项目恢复、历史 checkpoint、追加及幂等检查通过。
- archive_subagents.py 默认仅预览，--apply 先备份后归档；不删除消息文件，不修改已有主会话。使用来源存档/指纹和历史重建校验，无法证明未变化的记录进入 blocked。
- 本机正式 profile 仅执行归档预览，结果 0 个候选、0 个 blocked，未归档正式数据。用户截图为 Windows，未访问截图对应数据库，也未做 Windows 真机或真实模型接续验证。

## 2026-09-20 Pi Agent 来源接入

- 新增 `pi-agent` 路由及独立只读 `pi_source.py`，对照本机 pi-coding-agent 0.86.0 的 V3 JSONL 格式和 session-manager 上下文选择实现。五个来源共用指定单个、多个、全部的预览、分批导入、失败隔离、重试、中断恢复及目标写入。
- 聚焦 Python **131/131** 通过；Pi 8 项专项与五来源公共矩阵覆盖只读、身份/标题、重复导入、分支与分支摘要、两次压缩、摘要先于保留片段、工具调用已压缩但结果被保留、系统/签名/扩展状态过滤、bash 上下文排除、图片 opt-in、断链/循环/未知格式/延迟响应拒绝。市场 CI 已登记 Pi 测试入口。
- 本机一条真实 Pi 会话通过 `--all` 临时目标原生验证，产生 11 条展示 / 11 条 canonical 历史；生产 provider 初始化、追加重读、重复导入保留新增消息、原有种子会话保持均通过。
- 经授权向 Internal Code 新增 `[From Pi] hello`，目标 `mvs_cd3920a305cba418ec8e0c599af5eb29`。重启后可见、可打开，原生输入自动化曾超时，改用可访问性 setValue 后成功发送不提供答案的验收问题。真实模型 45 秒完成，正确复述最初的问题、历史工作目录和后来提供的 lark-base 技能；没有调用工具。canonical 从 11 条增至 13 条，重复 apply 后全部保留。
- Pi 源 JSONL 的 SHA-256 未变。目标既有 **1,196 个会话、21,593 条展示消息、255 条初始化记录、265 份历史文件** 指纹未变；新增一个会话及 13 条展示消息（含验收）。29 个已有项目中，仅关联项目的 session_count 从 2 到 3，以及续聊触发的 latest_activity_at_ms 更新。导入前有在线数据库备份。
- 边界：当前只支持 V3，不自动升级源 V1/V2。按最后持久化节点选择分支，无法恢复仅存在内存中的分支切换；真实样本未压缩，压缩/分支使用合成测试，未声称真实模型验收覆盖全部分支。扩展自定义 UI 不迁移，扩展消息仅作标记背景；图片字节不迁移并要求显式降级许可。未支持 deferred response，未验证 Windows 真机或超大上下文容量。未替换已安装插件，发布依赖 MR 合入和市场更新。

## 2026-09-20 OpenCode V2 来源接入

- 新增 `opencode_source.py`，对照官方 v2.0.10 的 session schema、history 选取和 fork projector，以及本机 2.0.10 数据库实现。读取 session_v2 / session_message，不读取凭据、权限、事件总线或工作树快照。四个来源共享范围选择、预览、批次、失败重试、恢复和目标写入。
- 聚焦 Python **123/123** 通过；OpenCode 10 个专项测试及四来源共同矩阵覆盖单个/多个/全部、失败隔离和硬退出恢复。专项验证只读/WAL、标题回退和归档、两次明文压缩、失败压缩保留历史、未知/原生 checkpoint 拒绝、文本附件解码、二进制降级 opt-in、工具流式/错误状态、fork 独立投影、宿主元数据过滤、暂存回退、未完成助手和重复序列拒绝、前台/后台 shell 差异。市场 CI 已登记独立测试入口。
- 本机真实会话 `ses_f42d7ab95ffeKN0pGFnkjljVlw` 在临时目标通过 `--all` 原生验证：5 条源记录中 idle 不作为对话，得到 4 条展示 / 4 条 canonical 历史。包含内联文本文件、5 个工具调用及最终回复；生产 provider 初始化、追加重读、重复导入保留新消息和种子会话检查均通过。
- 经授权向 Internal Code 新增 `[From OpenCode] Custom Header Stories 文件和图片内容`，目标 `mvs_86826b01bf4efc36a1f9ab66f375e9b7`，按来源关联 mx-h5 项目。正常退出并重启应用后可见、可打开；发送不含答案的验收问题，真实模型 46 秒内正确复述文件路径、顶部导航栏布局、iphone6 视口和示例标题“自定义头部”。未调用工具，canonical 从 4 条变为 6 条；重复 apply 保留新增用户/助手回复。
- OpenCode 两张来源表指纹与 DB/WAL 文件 SHA-256 均未变。目标既有 **1,195 个会话、21,587 条展示消息、28 个项目、254 条初始化记录、264 份历史文件** 均未变；仅新增 1 个会话、6 条展示消息（含验收）、1 个项目及对应历史初始化。导入前有在线数据库备份。
- Ruff、市场校验、reference vectors 和独立 CI 测试入口通过。当前真实样本仅为一个未压缩会话；压缩和 fork 验证采用合成样本，未冒充真实 LLM 压缩验收。OpenCode 旧版存储、暂存回退、模型专属 checkpoint 不支持；Windows 真机及大上下文容量尚未验证。图片/非文本附件不迁入，工具原始输出已截断时只保留现有文本并告警。不替换已安装插件，发布依赖 MR 合入与市场更新。

## 2026-09-20 Claude Code 来源接入

- 新增只读 `claude-code` 适配器，复用单个、指定多个、全部的预览、分批导入、失败重试、中断恢复和去重流程；标题统一标记 `[From Claude Code]`。解析主会话 parent chain、同一 provider message 的并行工具块、按 ID 配对的工具结果，以及明文压缩摘要和显式保留片段。历史工具使用已有只读卡片，不重放调用。
- 经用户授权，将跨电脑 ZIP 中 70 个文件（17 个主会话及关联子代理/工具输出）安全解压至本机 Claude projects 目录。仅转换 ZIP 路径分隔符，未改写 JSONL 中的 Windows 路径；未覆盖已有文件。导入时显式将所选会话的工作目录映射到本机项目。
- 聚焦 Python **113/113** 通过；三个来源共享选择范围、失败隔离和硬退出恢复矩阵。Claude 专项覆盖分支选择、并行工具、两次压缩、保留段校验、断链/循环/未知格式拒绝、宿主块与正文 XML 区分、二进制/签名过滤、会话内完整工具输出与符号链接拒绝。Ruff、市场 66 插件校验和 reference vectors 通过。
- 17/17 真实主会话以指定批量方式导入临时目标，生产 history provider 初始化、续聊追加与重读、重复迁移保留新回复及既有种子会话均通过。原生测试脚本新增通用 `SOURCE_TYPE` / `SOURCE_PATH` / `SOURCE_IDS` / `SOURCE_WORKSPACE` 参数，旧 Codex 参数仍兼容；Codex 原生 fixture 回归通过。这里不是将 17 条全部写入正式 profile，也不是对 17 条逐一调用真实模型。
- 实际向 Internal Code 新增 2 条验收会话并重启：`mvs_dc8f2177f0d1154d9d72353aca6a1fc6`（两次压缩，108 条展示 / 71 条接续）和 `mvs_97445c5db256bc9e1042a07e5afc7aee`（普通工具会话，17 / 17）。分别提问未提供答案的历史问题；真实 `gpt-6-astra` 在 20 秒和 24 秒内回答。前者正确优先采用压缩之后对保存失败状态的最终修正，后者复述文件打开报错的历史定位、处理及验证局限。两次均未调用工具，持久化接续历史分别增加用户、助手两条消息；重复 apply 后仍保留。
- 导入和验收后，源 70 个文件 SHA-256 全部未变。目标既有 **1,193 个会话、21,458 条展示消息、252 条初始化记录、262 份 messages.jsonl** 指纹未变；新增 2 个会话、125 条迁入展示消息及 4 条验收消息。已有项目仅 `session_count: 412 → 414` 和续聊触发的 `latest_activity_at_ms` 更新。迁移前已在线备份目标数据库。
- 限制：真实来源版本为 2.1.177 / 2.1.198，未知结构明确拒绝。未在 Windows 真机执行迁移；跨系统路径测试不等于 Windows 锁及进程行为验收。图片/文档二进制不迁入，子代理独立轨迹不作为主会话导入，仅保留主会话收到的结果。未对每个大上下文会话进行真实模型容量验收；原生存储检查通过不保证目标模型窗口足够。未替换已安装插件，发布仍需市场更新。

## 2026-09-20 Codex 加密压缩的明文重建

- 对明确识别的 `compaction.encrypted_content`，新增 `prepare-context` 导出固定来源前缀、分块明文证据、完整工具证据与摘要模板。Skill 使用当前宿主生成摘要，`--context-summary-dir` 接入已有单个/多个/全部清单流程。脚本不调用模型、不解密；未知压缩、回退及缺少压缩前助手正文仍失败。
- Python 聚焦 **104/104** 通过。覆盖两次压缩、摘要缺失/超限/未读全/错误绑定、证据篡改、预览后摘要变化、源前缀修改/截断/未写完、允许快照后追加、超长轮次不截半、直接与重建会话混合全量，以及既有选择范围、失败隔离和硬退出恢复回归。Ruff 格式与 `E9,F,I`、市场 66 插件校验、reference vectors 通过。
- 原生 `verify_codex_native.mts` 使用真实来源的固定快照，在临时目标验证 **103 条展示 / 1 条 canonical 摘要**、生产 history provider 初始化、追加重读、重复迁移保持续聊和种子会话。通过 `CONTEXT_SUMMARY_DIR` 指定证据目录。ZCode 原生 schema、repair、WAL、搜索、隐藏项目恢复及续聊回归通过。
- 真实宿主摘要验收：Internal Code 中独立任务读取仓库 Skill 和 8 块证据，必要时补查完整记录，生成 8,159 字符摘要；预览通过。该流程实际使用宿主模型，未用固定 fixture 摘要冒充 LLM 结果。块校验只能证明绑定与阅读声明一致，不能自动证明摘要事实完整。
- 经用户授权，将曾失败的真实会话 `01a0b7da-c685-7941-86a7-08a19de0775f` 新增到 Internal Code，目标 `mvs_7a0f3f4dcc67daf2727e35a3f7fdb886`。源快照 13,321,504 字节，包含 2 个加密检查点；最后完整轮次超出预算，所以本例 canonical 仅保留重建摘要。原始历史继续用于展示与来源存档。固定前缀 SHA 校验通过，迁移脚本未写源历史；Codex 本身在快照之后的追加不纳入此次导入。
- 通过原生菜单重启应用后，列表和历史可读；向新导入会话发送未给出答案的三个问题，实际模型 `gpt-6-astra` 在 22 秒内正确回答最初三项问题、统一适配器的原因和批次/中断恢复规则。运行时返回 200、单步完成；canonical 为迁入摘要、验收问题、助手文本回复，未调用工具或重放历史任务。续聊后再次 apply 完成，未覆盖新回复。
- 紧邻导入前后的不变性核验：既有 **1,192 个会话、21,353 条展示消息、251 条初始化记录、261 份 messages.jsonl** 哈希均保持不变；新增 1 个迁入会话、103 条展示记录和验收的 2 条新消息。项目唯一变化为 `session_count` 从 411 到 412。导入已生成在线数据库备份，没有整库恢复或覆盖既有会话。
- 限制：以上仅验证这一个真实加密会话；不等于逐字无损恢复，也不保证任意模型生成的摘要完整。图片/二进制内容仍未迁入；Windows 真机、数千会话容量与真实批量 LLM 摘要耗时尚未验收。新版本代码在仓库中验证，未直接替换已安装插件副本；实际发布以 MR 合入及市场更新为准。

## 2026-09-19 统一来源路由和迁移任务执行

- `migrate.py` 统一入口通过 `SOURCE_ADAPTERS` 路由；新增 `zcode_source.py` 隔离 SQLite/index 读取及压缩、回退语义，与 `codex_source.py` 提供一致接口。`migration_job.py` 统一接收候选会话集合，执行预览、分批、失败隔离、重试与恢复。
- ZCode、Codex 的单个、指定多个、全部迁移均使用同一清单流程。CLI 两个来源都要求显式 `--session` 或 `--all` 以及 `--report`，不再提供省略范围的隐式全部或绕过清单的指定迁移入口。Skill 与 README 已同步。存储核心的原子事务函数保留，供统一执行器调用和已有集成验证。
- 聚焦 Python **92/92**（ZCode 42、Codex 42、统一任务 8，任务测试包含多个参数化子场景）。矩阵覆盖两来源 × 单个/多个/全部、指定批量的失败隔离与重试、两来源提交前后硬退出恢复、明确工作目录映射、未知选中 ID、旧导入去重及旧 Codex 清单升级。Marketplace CI 已登记新的任务测试入口。
- 额外用重构前 `d56db67` 的脚本分别导入 ZCode/Codex fixture，再由新流程预览和执行：均为 already-imported，数据库会话行和 messages.jsonl 字节不变，证明旧来源指纹、目标 ID 与历史路径兼容。
- 原生 Archon schema / production history provider：ZCode 指定和全部均通过初始化、repair、WAL、搜索、动作投影、隐藏项目恢复及续聊追加重读；Codex 指定批量和全部分别对三个真实副本通过，展示/接续消息数仍为 78/43、5/5、6/6，重跑保留已追加历史和既有会话。
- 本轮仅使用临时目标与来源副本，未修改原始 Codex 或正式 Internal Code 会话，未新增真实 LLM 请求。Windows 真机锁和数千会话容量压测仍未执行。后续段落按时间保留历史验证记录，旧命令/能力边界以当前 README 和 Skill 为准。

## 2026-09-19 Codex 显式全量与中断恢复（历史阶段）

- 新增 `plan --all --report`：固定候选范围，逐会话解析和目标契约预检，分别记录 ready / already-imported / incompatible 与发现阶段错误；预览不写来源和目标会话，仅写清单。
- 新增 `apply --all --report`：默认每批 20 个会话，批次独立备份与提交；批次失败自动逐条隔离。进度原子保存，重跑核对已完成目标并继续未完成项；`--retry-failed` 重试失败项。来源变化要求新预览。
- Python 聚焦测试 **84/84**（ZCode 42、Codex 42）。新增覆盖混合兼容性、非法记录结构、批次失败隔离、失败重试、预览后来源变化、新增会话不扩范围、缺失成功目标、参数互斥、来源目录保护、配置一致性与跨进程写锁。
- 子进程通过 `os._exit(91)` 分别在历史写入后/数据库提交前、数据库提交后/进度更新前直接退出；重跑分别隔离未提交目录并重试、识别已提交会话，未重复写入。另测第一批完成后中断，恢复余下批次。未提交目录保存在 `recovered-*`，不删除历史或恢复整库。
- `verify_native.mts` 的 ZCode 初始化、repair、WAL、搜索与原有会话保留通过。`CODEX_BULK=1` 下 `verify_codex_native.mts` 对合成样本与此前三个真实 Codex 副本分别通过：每批 1 个，展示/接续消息数 78/43、5/5、6/6，原生 provider 读取、追加、重读、重复执行和既有会话保留正常。
- 全量流程仅对隔离 fixture 和三个真实来源副本执行，目标均为临时目录。本轮未修改 Codex 原始数据或正式 Internal Code 会话，未新增真实 LLM 请求；前次真实续聊验收见后文。
- 尚未对数千会话/数十 GB 全量做容量压测，Windows OS 文件锁未真机执行。每批整库备份会增加磁盘占用；预览给出按当前数据库大小估算的备份量，不含数据库增长、历史文件和失败重试。

复现分批原生验证：使用下方已有 `verify_codex_native.mts` 命令，增加 `CODEX_BULK=1`；若提供来源副本，`CODEX_SESSION_IDS` 仅供测试断言预期总数，导入实际走 `--all` 固定清单。

## 2026-09-19 来源入口与标题标记

在最新 `main`（`9eda027`）上重放本 MR 的三个提交，再补充来源展示：市场示例分别提供 ZCode、Codex 入口；新迁入标题分别使用 `[From ZCode]`、`[From Codex]`。同一前缀不重复添加，重复导入保留目标现有标题，源数据不修改。

- 聚焦 Python **72/72**（ZCode 42、Codex 30），覆盖标题持久化、来源前缀搜索、归档标题、避免重复标记、用户改名后幂等导入和原库只读。
- `verify_native.mts`、`verify_codex_native.mts` 在临时目录通过，验证原生 schema、历史加载、追加与重读，以及既有会话保留。
- 72 个插件的市场目录校验、Ruff 格式与 `E9,F,I` 检查、`git diff --check` 通过。
- 本次未向正式 profile 新增或修改会话，未重复执行真实 LLM 续聊；前次真实验收记录保留在下节。

## 2026-09-19 Codex 语义修复与真实 Desktop 验收

源码基线：Archon `b95c95599f036d59e9561c7e5ced71088fa5604e`；已安装 MiniMax Internal Code `3.0.73-preview.4152`，macOS。通过应用进程、runtime 子进程及打开的数据库确认当前 profile；用户明确授权新增迁入测试会话及重启，未修改 Codex 原始 rollout。

- 修复附件说明开头导致真实请求被隐藏的问题，只剥离已识别宿主块，保留普通 XML 和混合消息中的正文。
- 明文 `compacted.replacement_history` 作为有效接续历史，再追加后续记录；历史展示单独保留。无法跨模型读取的加密 checkpoint、缺少 replacement history 的旧格式和回退记录，当前明确拒绝，不静默丢弃语义。
- 会话 ID 以 `session_meta` 和 SQLite 元数据为准；双 UUID 文件名不再被当成稳定身份。恢复归档发现和状态；歧义、元数据冲突及损坏 JSON 在写入前拒绝。
- 插件聚焦 Python 测试 **70/70**；包含 ZCode 原有 41 项与 Codex 29 项。新覆盖附件请求、用户 XML、混合宿主块、工具记录不归属到下一条用户消息、压缩后的双历史、多个 checkpoint、加密/回退拒绝、元数据身份、归档、重复身份和原库只读。
- `verify_native.mts` 通过，保留原有 ZCode 首次初始化、repair、WAL、搜索、操作投影和幂等证据。
- 新增 `verify_codex_native.mts`：当前 Archon 原生 schema、production legacyHistory provider、revision、历史追加、重建 provider 读取、重复导入后新消息保留、既有会话不变均通过。合成 fixture 与 3 个真实来源副本分别执行。
- 3 个真实样本隔离验证后，新增到已授权的 Internal Code profile，标题均加验收前缀。展示/接续消息数分别为 **78/43、5/5、6/6**。原始文件与来源副本 SHA-256 核对一致。
- 通过原生 Computer Use 正常退出并启动应用，三个新会话可搜索、可打开。各发送一次依赖历史的验收问题；真实模型 `gpt-5.6-sol` 正确复述压缩会话的 MR 与修复决策、搜索会话的具体参数、附件请求的原始任务和环境结论。三次均完成，新增工具调用均为 0。
- 对照持久化的实际 LLM request：**43/43、5/5、6/6** 条接续消息的文本全部出现在实际请求中，非仅校验文件或 mock。第二次退出并启动后，新回复和旧历史仍可打开；重复导入返回 `unchanged`，新回复保留。
- 既有 **1,179 个会话、21,084 条消息、238 条历史初始化记录、247 份 messages.jsonl** 在导入及重启后逐项指纹未变。已有项目变化仅为新增会话触发的 `session_count: 406 → 407`，以及验收续聊更新的 `latest_activity_at_ms`；另外新增两个来源工作目录的项目。
- 市场目录校验（66 个插件）与 Publisher dry-run 通过。Python 初始环境缺 PyYAML，使用临时 uv 依赖环境执行校验，未更改全局环境。Ruff 使用 `--isolated --select E9,F,I` 检查通过；`git diff --check` 通过。

边界：压缩样本中的 2 张历史图片字节未迁移，文本续聊验收不代表附件完整性。压缩样本首次续聊显示上下文使用 84%，未验证继续增长到窗口上限后的自动压缩。加密摘要、旧式压缩、回退、Windows 真机、时间范围筛选、全量和批次恢复仍未支持或未验证。没有发布生产市场，没有自动合并 MR。

复现原生 Codex 验证（仅创建临时目标）：

```sh
ARCHON_ROOT=/path/to/agent-archon \
  /path/to/agent-archon/node_modules/.bin/tsx \
  --tsconfig /path/to/archon-source-paths.json tests/verify_codex_native.mts
# 可选：CODEX_SOURCE=/path/to/source-copy CODEX_SESSION_IDS=id1,id2
```

## 2026-09-18 历史记录：0.2.0 Codex 来源验证

改动范围：新增 `scripts/codex_source.py`（仅读取与规范化）。`migrate.py` 增加来源注册表与命名 dialect；迁移锁、SQLite 在线备份、单事务提交、失败回滚、提交后读回、项目恢复、历史初始化与 `repair` 逻辑均未改动。冻结的 `convert_legacy_v1` 保持 ZCode 硬编码不变。

- Codex 记录规范化为与 ZCode 相同的 item 形状，转写复用同一个 `convert` 与 `projection` 策略，不存在第二套转写实现。分类结果：真实用户输入 `user`、助手回复 `assistant`、宿主脚手架 `hidden`（仅存档）、子代理消息 `context`（带标签进接续、不进界面）。
- ZCode 路径行为、目标 ID 算法与 `zcode-*` 产物文件名保持不变。
- Codex 行为测试 18 项：廉价 scan 只读、plan 只读、系统提示与加密载荷不泄漏、`event_msg` 不重复导入、宿主脚手架仅存档且不作标题、子代理消息为带标签上下文且不进界面、Codex dialect（工具标签/turn/msg 前缀/provider）、真实用户消息保留 `msg-user-v1-` 身份、思考内容不进接续上下文、迁入会话进入 FTS、首次对话历史初始化写入且 revision 与 canonical 一致、`repair` 拒绝非 ZCode 来源、provenance 为 `codex-*` 且带 `sourceType`/`adapterVersion`、幂等重导、源变更拒绝覆盖、未知会话 ID 拒绝、fork 文件名可发现、空与损坏 rollout 降级、符号链接来源拒绝。
- 市场测试合计 154/154 通过；`validate_marketplace` 66 插件与 four-types fixture 通过；publisher dry-run 与 fixture dry-run 通过；`reference_vectors verify` 通过。
- 本机真实 Codex 数据 3413 个 rollout（约 19 GB）：`scan` 约 3.7 秒；缺少 `--session` 时 `plan`/`apply` 被闸门拒绝。
- 选定 2 个真实会话导入隔离目标副本，复跑返回 `unchanged`；导入结果中 `You are Codex`、`base_instructions`、`gAAAAAB`、`<app-context>`、`<environment_context>` 命中均为 0。
- 隔离目标为按正式库 DDL 重建并植入种子会话的副本，未写入正式 MiniMax Code 数据库。

## 0.2.0 未验证及 Codex 限制

- 未在 Desktop GUI 验收 Codex 迁入会话的列表与展开；未发起真实模型请求，仅验证到存储与 canonical history 接口层。
- 多代理会话的子代理消息按 `context` 全部进入接续历史。实测单个会话 502 条，接续上下文会显著变大；当前不做裁剪或摘要。
- 同一 turn 内的多条助手消息各自成行，不还原 Codex 原生 item 级 UI。
- 只能用 `--session` 逐个点名，不提供时间窗口或批量筛选。
- 未命名会话取首条真实用户输入作标题，可能取到 slash 命令文本。
- Codex 无归档/删除状态，无样本可验证，一律按非归档迁入。
- 不迁移 `~/.codex/attachments` 附件字节；Codex 消息中的图片等非文本内容不迁移，只在告警中计数。
- 批次目录仍沿用 `zcode-migration` 历史名称；`apply` 每次全量备份目标数据库；`<来源>-source.json` 使落盘体积约翻倍。三项为两来源共有的既有行为，本次未改。

## 0.1.4 首次对话初始化修复

根因：导入已经写入 `messages.jsonl`，但没有写 `local_runtime_pi_history_file_migrations`。生产 turn 启动时启用 `legacyHistory`，将已有文件与空的旧存储比较，报 `Canonical history materialization is ambiguous`。先前 provider 测试未配置 `legacyHistory`，遗漏了这条初始化路径；现已使用生产同款 legacy source reader/checkpoint repository。

- 在报错原会话的隔离副本上复现相同错误；报错 materializer 模块与已安装 Desktop 模块 SHA-256 一致。补齐 checkpoint 后原生 provider 成功读取 28 条历史。
- 新导入在同一事务写入 checkpoint、消息数和原生语义 revision；回滚包含 checkpoint。重复 apply 遇到旧导入缺少 checkpoint 时明确提示 repair，不再误报可用。
- `repair` 先生成独立数据库备份，核对来源身份、存档指纹、idle/error 状态和原始历史，仅补写缺失 checkpoint。按 adapter v1/v2 分别重建校验值，不转换或覆盖旧历史。运行中、存档损坏或历史变化时拒绝处理。
- 已按用户请求修复指定正式会话，独立回读确认历史文件字节及 30 条界面消息（含 2 条失败输入）均未变化；再取副本用原生 provider 读取成功。没有代用户发送模型请求。
- Python 插件测试 41 项通过，包含原有 33 项及初始化、回滚、repair 防护/保留性、旧版格式等 8 项回归。
- 增强 `tests/verify_native.mts`：配置真实 legacyHistory，校验 Python revision 与 Runtime revision 一致，新导入读取成功；删 checkpoint 后重现原错误；repair 后读取、追加、重建 provider 后读取成功，旧历史前缀不变；原有 WAL、搜索、fork/rewind 操作投影、项目恢复与旧会话隐藏验证继续通过。
- 原生集成使用本机 Archon 源码及指向源码的 tsconfig paths，在临时目标中执行；Marketplace CI 无 Archon 依赖，运行 Python 回归。

未覆盖：修复后真实 LLM 回复、Desktop GUI 自动化验收和 Windows 真机。用户反馈 fork 后可对话，与 fork 会创建初始化记录一致；不将该反馈当作修复后原会话验收。

## 0.1.3 修复验证

源码基线：

- agent-archon `preview_train`：`39f002383d78e77bd96e9f626fe8f3f767d536c1`；相关数据库、搜索、消息操作与项目移除代码也与当时 `main`（`b7ba255844d4a4fb64772801c9f5aca199c2c79c`）逐文件比对。
- zcode-reverse `main`：`21613a053e3fe781bda93c5ae82b60271d56cba5`，恢复代码位于 `readable/resources/glm/zcode.cjs`。回退选择来自 `d0`，压缩/保留片段来自 `Dp`、`klt`、`zzo`，显示策略来自 `H2`；不是根据界面猜测。

自动化与隔离集成结果：

- 插件测试 **33/33**，分别在 Python 3.9.6 和 3.12.5 通过。覆盖 WAL 目标备份独立读取、未 checkpoint 的 WAL 源数据、合法 v0 行逐列不变、非法旧身份拒绝、回退/压缩组合、隐藏/ignored 消息、嵌套附件、即时全文搜索、事务回滚、已移除项目恢复及回滚、旧导入不重写、GBK 输出与 Unicode 路径、Windows reparse point 识别。
- Marketplace 全套 **128/128**（含上述 33 项）；reference vectors、主目录/fixture validator、两种 publisher dry-run 通过。
- `tests/verify_native.mts` 在上述 Archon 源码初始化的真实数据库结构上通过：保持在线 WAL 连接，保留原生 v0 记录，导入后中文/emoji 标题立即可搜索；原生 action projection 识别 rewind/fork；已移除项目仅显示新导入会话，原有会话仍被移除边界挡住。
- 原生 canonical provider 成功读取并追加用户轮次，原有历史前缀不变；重复导入返回 `unchanged`，继续对话后的文件逐字节不变。没有调用真实模型。
- 额外 6 个隔离来源案例通过原生读取/操作投影检查；覆盖回退、压缩、模型专用消息、嵌套附件等；7 组回退/压缩组合的显示链与接续链和从上述 ZCode 文件提取的原始函数结果一致。
- Ruff lint/format 与 Python 编译检查通过。

边界：

- Windows 反馈仅用于定位线索。没有 Windows 真机/Runner，不能把 macOS 上的非 UTF-8 子进程或 reparse 模拟称为 Windows 验收。
- SQLite 只读打开缺少 WAL 辅助文件的库，在本机环境可能失败。脚本明确报告路径和宿主初始化建议，不忽略 WAL。备份副本则在关闭前转为 DELETE 模式并校验，独立可读。
- 不修改正式 profile、不执行旧工具、不自动修复旧适配器导入过且可能已接续的会话。0.1.3 的历史转换与索引修复只作用于新导入记录。
- 文件夹迁移指会话关联到现有工作目录；`--workspace` 支持按项目分批映射到新路径。不会搬运工程文件、附件字节或收藏分组。

原生集成测试需要准备好 Archon 依赖，并让 tsx 的 paths 指向源码（避免误用旧 dist）：

```sh
ARCHON_ROOT=/path/to/agent-archon PYTHON=/path/to/python3 \
  /path/to/agent-archon/node_modules/.bin/tsx \
  --tsconfig /path/to/archon-source-paths.json tests/verify_native.mts
```

该脚本只创建临时来源和目标，退出时清理。普通 Marketplace CI 不依赖 Archon checkout，执行 33 项 Python 回归；原生集成是上述独立运行结果。

## 0.1.0 历史验证记录

- Python 标准库自动化测试 14/14：只读预览、原生消息与接续历史、重复导入、源变更拒绝覆盖、损坏源拒绝、选定会话、目标必填、迁移锁、符号链接拒绝、未来版本拒绝、附件缺省阻止、Desktop 归档/标题/删除、事务失败回滚、提交成功后报告失败不误删历史。
- 本机 ZCode 3.12.3 真实数据库，以 `mode=ro`、`query_only` 和读事务读取：16 会话、224 消息、821 parts。
- 目标为隔离的 MiniMax Runtime 数据库副本，未修改正式源/目标会话。源端 Desktop 覆盖标题和 1 个归档状态已保留。
- MiniMax Code Desktop 数据目录与隔离测试来源数据库的 31 个相关表、索引、触发器 DDL 完全一致。
- 当前 Runtime 原生 `readMiniMaxPlugin` 接受插件格式；Skill frontmatter 检查通过。
- 当前 Runtime `createSessionRepository` 读取全部 16 个迁入会话；`createMessageRepository` 读取全部 224 条界面消息。
- `decodeCanonicalHistoryEnvelope`、`assertCanonicalHistorySequence`、`validateCanonicalHistoryMessages`、`copyCanonicalHistoryForPiCompatibility` 接受全部迁入历史。
- 实际 `createSessionSystemCanonicalHistoryProvider.read` 读取 16 个会话；对 1 个隔离会话通过原生 `commitUserMessage` 和 canonical `append` 追加新用户轮次，旧历史前缀完整保持。
- 在追加新轮次之后再次运行迁移，返回 `unchanged`，无重复会话，也未覆盖新历史。

## 0.1.1 市场接入验证

- Marketplace 主目录 66 个插件和 four-types fixture 4 个插件通过 validator。
- reference vectors 校验通过；市场测试 109/109，其中包含本插件迁移行为测试 14 项。
- 新图标由 imagegen 生成，作者为 Insider，catalog 仅分发到 desktop；不向无法访问本机 ZCode 数据的 cloud 分发。

## 0.1.2 产品定位与来源边界

- 产品更名为 Agent 会话迁移，插件标识 `agent-session-migration`，入口 `/migrate-agent-session`；作者为 Insider，保留通用会话迁移图标。
- 当前仅支持 ZCode，CLI 通过 `--source zcode` 显式选择来源；未实现的来源在读取/写入前拒绝。
- 原有 ZCode 目标 ID、备份路径和来源存档保持兼容，避免更名后重复导入。
- 迁移器 15 项行为测试接入市场测试入口。

## 未验证及明确限制

- 未向正式 MiniMax Code 数据库执行迁移，未在 Desktop GUI 中验收列表刷新。
- 未发起真实模型请求。已验证的是原生持久化与接续历史接口，不是 LLM 端到端结果。
- Windows 未真机验证。运行需 Python 3.9+；当前本机验证环境为 macOS。
- 0.1.0 的真实来源无附件 file parts；0.1.3 以隔离 fixture 验证了直接及工具嵌套附件。插件默认拒绝带附件的迁移；只有显式 `--allow-reference-only` 才保留引用而不复制字节。
- 工具记录转为完整历史文本，原始数据存档；不恢复其他产品的原生工具 UI、权限、工作流或正在运行的任务。
- 插件使用有版本检查的本地存储适配器。不是公开稳定导入 API；MiniMax/ZCode/Codex 未来格式变动需要重新验证。

## 复现自动化测试

```sh
python3 -B -m unittest discover -s tests -v
```

## 通用历史展示补充（2026-09-19）

- ZCode / Codex 共用只读工具展示转换，原工具名、状态及输入输出放入详情，固定工具名不触发原生执行/编辑组件；模型续聊依然使用原有带标签文本。Codex 附件包装只在识别完整结构时将真实请求前置；未知内容不删除。
- 聚焦 Python 94/94。新增两来源的工具名/未完成状态/多行输出及附件包装边界测试；原生 ZCode 验证增加 800 行输出通过实际 display sanitizer 的检查。真实界面曾发现长 JSON 字符串被替换为 `omitted:non-json`，改为结构化 `content: [{type: text, text: ...}]` 后复验通过。
- 三个真实 Codex 副本的续聊消息（43、5、6 条）、消息 ID 和告警与修改前完全一致；当前原生 provider 的追加、重读和重复迁移测试通过。没有新增真实 LLM 请求，延续前次续聊证据。
- 经既有授权，在 MiniMax Internal Code 新增 3 个独立验收副本（2 个 Codex，其中 1 个用于排查长输出；1 个 ZCode），重启并实际打开两来源，验证正文与附件引用分开显示、工具分组折叠/展开、输入输出详情及复制按钮。最终 Codex 副本的长输出正常显示；旧调试副本保留以供比对。未覆盖旧导入，不自动追溯刷新已有会话。
- 原有 1,182 个会话、21,179 条消息、241 条历史初始化记录、250 份历史文件指纹不变；既有项目仅新增验收会话计数。来源使用临时副本，没有写入 Codex / ZCode 原始会话数据。
- 详情沿用桌面端 2,000 字符展示截断及完整复制能力；图片/附件仍只保留历史引用，不复制文件，不增加任何执行、审批或重试操作。Windows GUI 未验证。
