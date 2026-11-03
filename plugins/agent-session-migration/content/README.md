# Agent 会话迁移插件

将其他 Agent 的本机会话迁入 MiniMax Code，保留历史并继续任务。**当前支持 ZCode、Codex、Claude Code、OpenCode、Pi Agent 和 OMP**，其他 Agent 暂未实现。

MiniMax Plugin V1，本地运行，Python 3.9+ 标准库，无网络请求。安装后在 MiniMax Code 使用 `/migrate-agent-session`，或说“一键迁移我的 ZCode 会话”“迁移我的 Codex 会话”。插件自动预览并导入，目标始终取当前 profile 的数据目录。

新迁入会话的标题自动加上来源前缀，例如 `[From ZCode] 原标题`、`[From Codex] 原标题`、`[From Claude Code] 原标题`、`[From OpenCode] 原标题`、`[From Pi] 原标题`、`[From OMP] 原标题`；已有相同前缀时不重复添加。来源数据不改名，重复迁移保留目标端现有标题（包括用户改名），不会追溯修改此前已迁入的会话。

历史展示与续聊上下文分别生成：ZCode / Codex / Claude Code / OpenCode / Pi Agent / OMP 共用工具记录转换，固定使用“历史工具记录”通用组件，展开后查看来源、原工具名、原状态及分段输入输出。历史未完成调用也不会进入运行态；不复用原工具的执行、审批或文件编辑操作。详情沿用桌面端的长度截断与复制完整内容能力。

Codex 已识别的附件包装会将真实请求放在前面，后面单独列出“历史附件引用，未复制文件”；未知包装原样保留。附件引用不是已上传附件，不保证原路径在新电脑可访问。原始文本仍完整进入续聊历史。展示改善只作用于新导入；重复迁移继续去重，不覆盖已迁入会话或其中新增的续聊。

市场清单最多展示 3 条示例问句，不代表来源支持数量。六个来源都可直接请求：

- 将我的全部 ZCode 会话迁入 MiniMax Code
- 将我的全部 Codex 会话迁入 MiniMax Code
- 将我的全部 Claude Code 会话迁入 MiniMax Code
- 将我的全部 OpenCode 会话迁入 MiniMax Code
- 将我的全部 Pi Agent 会话迁入 MiniMax Code
- 将我的全部 OMP 会话迁入 MiniMax Code

## 安装

作者：Insider。版本：0.6.0。图标来源见 [ASSETS.md](ASSETS.md)。

将整个 `agent-session-migration` 文件夹放入 **MiniMax Code 当前 profile 的 `plugins/`**，保持 `.minimax-plugin/plugin.json` 在插件根目录下。压缩包先解压，再复制这个文件夹。不要多套一层同名目录。依赖 Python 可用；脚本不安装任何依赖。

## 当前支持：ZCode、Codex、Claude Code、OpenCode、Pi Agent、OMP

下表的迁移内容和格式约束对六个来源都适用；来源特有差异见本节末尾。

## 迁移内容

| 内容 | 处理 |
| --- | --- |
| 会话标题、工作目录、创建/更新时间、归档状态 | 写入原生会话列表并关联项目 |
| 用户/助手消息 | 按 ZCode 回退、压缩和可见性语义分别生成界面历史与模型接续历史；压缩前可见历史保留展示，但不重新进入上下文 |
| 工具调用输入/结果/错误 | 界面使用通用只读折叠记录；模型上下文仍保留带来源标签的完整历史文本，不重放 |
| 思考内容 | 保留为界面历史，不重放进模型上下文 |
| 项目文件夹 | 按现有工作目录关联项目；不复制、移动工程文件，也不恢复 ZCode 的收藏分组 |
| 来源历史与迁移元数据 | 每会话保存 `<来源>-source.json`，按适配器规则过滤敏感配置后供核对 |
| 文件附件（包括工具结果内的附件） | OpenCode / OMP 已存内联文本保留；其他附件不迁移字节，引用降级需 `--allow-reference-only`，来源具体限制见下文 |
| 登录、密钥、系统提示、权限、自动化/运行中任务 | 不导入 |
| 已删除会话 | 按 Desktop index 跳过 |

当前适配 ZCode `cli/db/db.sqlite` 的 session/message/part 表和可选 `v2/tasks-index.sqlite`。目标适配 MiniMax Runtime columnar version 3、session data version 4 的存储布局。不是官方导入 API；此版本使用经过源码和隔离实测核验的本地存储适配器。目标中的合法 `columnar_version=0` 历史行原样保留，不要求删除；其他未知版本或损坏记录拒绝写入。Windows 编码与路径代码已检查，并覆盖非 UTF-8 终端和 reparse point 回归测试，尚未真机验证。

Codex 适配 `sessions/`、`archived_sessions/` 下的 rollout，以及可选 `state_*.sqlite` 和 `session_index.jsonl` 元数据。正文读取 `response_item`，明文压缩记录重建有效接续历史；普通 `event_msg` 不重复导入，回退事件会阻止不安全迁移。来源读取完成后，Codex 记录按与 ZCode 相同的 `projection` 策略分类，不另行维护一套转写逻辑：

| Codex 记录 | 分类 | 结果 |
| --- | --- | --- |
| 真实用户输入 | `user` | 界面历史 + 接续上下文 |
| 助手回复 | `assistant` | 界面历史 + 接续上下文 |
| 已识别宿主块（Codex 中为 user 角色） | `hidden` 或正文分离 | 纯宿主记录隐藏；混合消息保留真实请求 |
| 子代理消息 `agent_message` | `context` | 带标签进入接续上下文，不显示在界面 |
| `base_instructions` 系统提示、`developer`/`system` 注入 | — | 读取阶段即丢弃 |

工具参数中的 Fernet 加密载荷替换为占位符；图片等非文本内容当前不迁移，只在告警中计数。兼容双 UUID 文件名，但通过元数据确认身份；指定空会话和损坏记录拒绝迁移；不可读取的压缩摘要按下方重建规则处理。保留归档状态。`repair` 只适用于 ZCode 旧导入。**六个来源的 `plan`/`apply` 都必须显式选择 `--session` 或 `--all`，并使用同一份 `--report`；不默认迁移全部。**

## Claude Code 来源

`--source claude-code` 扫描 `projects/<工程标识>/<会话 UUID>.jsonl`，使用记录内 sessionId 校验身份；custom-title 优先于 ai-title，再回退真实用户首条正文。保留 Windows 来源路径，不把编码目录名反向猜成当前工程。跨电脑迁移通过 `--workspace` 显式映射已选会话；不修改原 JSONL，也不批量覆盖不同项目的工作目录。

父消息链选择当前分支，排除已放弃分支；同一助手消息的流式片段以及并行工具结果按原消息/调用 ID 合并到只读历史记录。识别的 `<ide_opened_file>`、`<ide_selection>`、`<system-reminder>` 宿主块不当作用户正文，普通 XML 保留。hook、skill 列表、权限、配置不导入；思考只展示，signature、图片及文档二进制不进入新模型上下文。

明文 `compact_boundary` + `isCompactSummary` 恢复有效摘要，校验并恢复明确的 `preservedMessages` / `preservedSegment`；压缩前的当前分支历史用于展示。损坏父链、冲突身份、未知压缩或缺少可读摘要会报不兼容，不用全量历史假冒有效上下文。这里不需要 Codex 的摘要重建目录。

`subagents/` 不作为独立用户会话导入，父会话中的子代理调用/结果保留。`tool-results/` 内与当前 session ID 绑定的落盘文本可只读补回长工具结果；禁止跨会话或任意路径读取，缺失文件明确提示只保留预览。该目录布局参考 [Claude Code 官方文档](https://code.claude.com/docs/en/claude-directory)，父链规则参考 [官方 SDK 会话读取器](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_internal/sessions.py)。当前实际样本覆盖 Claude Code 2.1.177 / 2.1.198；这不是对所有历史/未来格式的兼容保证。

## Pi Agent 来源

`--source pi-agent` 读取 `~/.pi/agent/sessions/<工作目录编码>/*.jsonl`；遵循 `PI_CODING_AGENT_DIR`，`--source-db` 接受 agent 数据目录或 sessions 目录。通过 header.id 确认身份，支持自定义 ID，不从文件名猜 ID；标题优先 session_info.name，再取当前分支首条用户正文。

当前核验已安装 `@earendil-works/pi-coding-agent` **0.86.0** 的 version 3 格式，依据官方 [session format](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/session-format.md) 和 session-manager 的 buildContextEntries。末尾 entry 对应持久化 leaf，沿 parentId 还原当前分支；内存中尚未写入的分支切换不在范围内。最新 compaction 摘要、firstKeptEntryId 开始的保留区间及其后消息用于续聊；压缩前当前分支保留展示。branch_summary 保留为带标签背景，不拼接被放弃分支的原始消息。

工具调用和结果按当前分支 call ID 配对；只保留结果的压缩边界也不会丢掉结果。bashExecution 的 excludeFromContext 生效，不执行命令或读取 fullOutputPath。system、工具声明、配置切换、custom 扩展状态、签名不迁入；custom_message 作为带标签的历史上下文，不加载扩展渲染器。图片仅保留占位说明，需接受 --allow-reference-only。v1/v2、未知角色/entry、断链、无效压缩引用、pending/deferred 助手拒绝导入，不自动升级源文件。

## OMP / Oh My Pi 来源

`--source omp` 读取 OMP V3 JSONL，默认 `~/.omp/agent/sessions/<工作目录编码>/*.jsonl`。`OMP_PROFILE` 优先于 `PI_PROFILE`；空值或 `default` 选择默认 profile。named profile 使用 `~/.omp/profiles/<profile>/agent/sessions`，忽略普通 agent-dir override；默认 profile 使用非 profile 派生的 `PI_CODING_AGENT_DIR`。遵循 `PI_CONFIG_DIR`，并在 macOS/Linux 对已存在的 `$XDG_DATA_HOME/omp[/profiles/<profile>]` 采用 XDG 布局。不存在的 profile 明确失败，不回退其他数据。`--source-db` 可显式指定 agent 数据目录或 sessions 目录，适用于 OMP CLI `--profile` / 自定义 session-dir 与宿主环境不一致的情况。

支持 256 字节首行 `title` 槽以及直接以 `session` header 开始的旧 V3，header.id 定义稳定身份；标题优先当前槽/header，再回退当前分支首条用户正文。末尾持久化 entry 的 parentId 链定义分支；用户 fork 保留，session_init 子代理日志列入 excludedSessions。只扫描会话层级，不读取 `history.db`、blobs、artifact 子树或凭据配置。

展示保留当前分支的历史正文；有效续聊使用最新明文 compaction 摘要、firstKeptEntryId 保留区间与后续消息，空 firstKeptEntryId 表示仅摘要。支持无 method 的普通压缩及不携带专属载荷的 handoff / soft / shake。更晚的 reset_boundary（`/clear`）使此前摘要及消息不再进入模型。工具按 call ID 配对，跨压缩边界的已有结果保留；失败/重试助手和悬空工具不重放，interrupted-thinking 连续性记录保留为背景。

bashExecution / pythonExecution 只读展示并遵循 excludeFromContext；fileMention 已保存的内联文本保留，路径不自动打开。思考只展示，签名、system、credential_pin、模式/模型配置及 custom 扩展状态不迁入。custom_message / hookMessage 仅作带标签背景，临时 prewalk-plan / vibe-mode-context 按来源规则排除。图片和 blob 字节不迁入，明确接受降级后才能使用 `--allow-reference-only`。仅关联主 cwd，额外 workspace 目录告警，不复制工程。

当前有效的 remote / snapcompact、非空 preserveData、providerReplayThroughEntryId、实验性 context rollover / notes 明确报不兼容；v1/v2、未知 entry/角色、损坏父链、无效保留引用、pending/deferred 回复和空有效历史同样拒绝。特殊压缩已被后续普通压缩或 `/clear` 取代时，按当前有效上下文判断。源码基线为 [OMP b4e2882](https://github.com/can1357/oh-my-pi/tree/b4e288210c052e1c62042515e739919c9304f14e)，依据 session-entries、session-title-slot、session-context、messages 及 utils/dirs；验证范围与未执行项见 [VALIDATION.md](VALIDATION.md)。

## OpenCode 来源

`--source opencode` 默认读取 `$XDG_DATA_HOME/opencode/opencode.db`，未设 XDG 时使用 `~/.local/share/opencode/opencode.db`；Windows 默认 `%USERPROFILE%/.local/share/opencode/opencode.db`。可用 `--source-db <数据库文件或数据目录>` 显式指定；未指定时尊重 `OPENCODE_DB`，其相对路径以数据目录为基准。SQLite 以只读事务打开，包含已提交 WAL，不读取账号、凭据或权限表。

支持 1.x 的 `session/message/part` SQLite JSON 正文（依据 1.18.32 源码）和 **2.0.10** 核验的 `session_v2/session_message` 投影。自动按完整 schema 分派，不要求升级原库。1.x 同名 `session_message` 只允许生命周期记录，不作为正文；混合正文投影或两套非空会话表拒绝迁移。JSON 文件存储尚未支持。按 `seq` 排序，idle 与切换模型等状态不算对话；用户正文、助手文本、历史工具使用共同转换。内联 base64 文本附件保留可读内容，不打开任意路径或下载 URL；二进制/外链附件只保留说明并要求 `--allow-reference-only`。工具输出原已截断时告警，不把摘录宣称为完整结果。

旧版按 message.time_created/id 和 part.id 排序；完成的 summary 与 compaction 请求配对，有 tail_start_id 时按“摘要、保留片段、后续消息”重建，失败压缩不清空历史。系统配置和 provider 签名不迁入；已裁剪工具输出使用占位并告警。data URL 文本附件可解码，外部路径不读取。断链、未知块、无结果压缩、暂存回退拒绝。各会话只读自己的历史，不按 parent_id 猜测排除 fork。

V2 最新完成的本地明文 compaction 的 `summary` + `recent` 和后续消息进入续聊；压缩前历史仍展示。失败压缩不清空旧上下文。fork 的历史已复制到自身会话，仅读其投影，不拼接父会话的后续内容。暂存 revert、进行中的助手/压缩、未知类型和 provider-native checkpoint 明确拒绝；目前不对 OpenCode 模型专属检查点调用 Codex 的重建路径。大上下文的模型容量仍需实际验收。

格式依据固定版本官方 [消息 schema](https://github.com/anomalyco/opencode/blob/v2.0.10/packages/schema/src/session-message.ts)、[上下文选取](https://github.com/anomalyco/opencode/blob/v2.0.10/packages/core/src/session/history.ts) 和 [fork 投影](https://github.com/anomalyco/opencode/blob/v2.0.10/packages/core/src/session/projector.ts)。

## Codex 加密压缩上下文重建

明文 `replacement_history` 仍直接恢复；包含加密 `compaction.encrypted_content` 时，可先运行 `prepare-context --source codex <范围> --context-summary-dir <目录>`。脚本只读生成固定前缀快照的证据块、完整可读证据和摘要模板，由 Skill 使用当前宿主模型整理交接摘要，再带同一 `--context-summary-dir` 走普通 plan/apply。不会解密密文，不要求新增模型 API Key，也没有脚本网络请求。

预览 `contextReconstruction` 标记 reconstructed、快照时间/hash、摘要长度与最近消息数。模型上下文使用摘要（最多 18,000 字符）＋预算内最多 3 个完整最近轮次（最多 24,000 序列化字符），完整历史用于展示和来源存档。工具长输出在摘要阅读块中提供明确标记的摘录，需核对时读取 full-evidence.jsonl；不是完整上下文的无损还原。详细的摘要字段与证据核对流程见 Skill。

来源可以继续追加，但本次只迁入已明确准备的快照前缀；前缀变更或截断会拒绝。摘要缺失、未声明全部证据块已读、摘要绑定错误或预览后摘要变化也会阻止导入。未知压缩类型、回退、缺少 replacement_history、缺少压缩前助手明文仍失败，不通过忽略记录来迁移。此机制覆盖指定单个、多个和全部范围，批量中每会话独立准备摘要，直接可迁移的会话继续复用原流程。

## 统一架构

```text
migrate-agent-session Skill / migrate.py CLI
  → --source 选择来源适配器
    → zcode_source.py：SQLite、Desktop index、压缩与回退
    → codex_source.py：rollout、catalog、可读 checkpoint / 重建摘要
    → claude_source.py：JSONL、父消息链、流式工具、明文压缩及保留区间
    → opencode_source.py：V2 SQLite 投影、工具及文本附件、本地明文压缩
    → pi_source.py：V3 JSONL、当前父链、压缩保留区间及分支摘要
    → omp_source.py：OMP V3 标题槽、profile、父链、reset 与明文压缩
  → 内部会话模型：身份/标题/工作目录、消息 parts、展示历史与有效续聊历史
  → migration_job.py：选择范围 → 兼容性预览 → 分批提交 → 失败记录 → 恢复/重试
  → migrate.py 存储核心：转换、在线备份、事务、原生索引、历史初始化与读回
```

适配器提供相同接口：`inventory` 返回候选 `ids`、发现 `errors`、来源大小 `bytes` 及适配器私有索引；`load_inventory` 返回会话元数据、规范化 messages/parts 和 fingerprint；`select_histories` 解释原生语义并给出展示/接续消息序列；`overview` 提供元数据列表（Claude Code 需读取 JSONL 提取标题）。执行器不按来源复制流程；新来源应实现适配器并登记到 `SOURCE_ADAPTERS`。旧 ZCode `repair` 仅处理历史初始化兼容，不属于迁移范围选择。

| 能力 | ZCode | Codex | Claude Code | OpenCode | Pi Agent | OMP |
| --- | --- | --- | --- | --- | --- | --- |
| 指定单个 / 多个 / 全部 | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 |
| 逐会话兼容性预览、来源标题标记 | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 |
| 分批导入、失败隔离、单独重试 | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 |
| 中断恢复、成功项保留、重复导入去重 | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 |
| 按时间范围筛选 | 暂不支持 | 暂不支持 | 暂不支持 | 暂不支持 | 暂不支持 | 暂不支持 |

每种范围只改变候选 ID 集合；单个是只有一条记录的批次，指定多个与全部使用相同事务和恢复逻辑。来源格式、压缩和回退兼容性仍由各适配器决定，不代表六个工具的全部历史格式均可无损转换。

## 统一命令与使用流程

`scan` 只列来源元数据，不代表正文兼容。`plan` 解析选中会话并检查目标契约，不修改来源或目标会话，仅写入显式清单。`apply` 消费同一清单；所有来源、所有范围都必须先 plan。

```sh
# 查看来源，其他来源将 codex 换成 zcode、claude-code、opencode、pi-agent 或 omp
python3 scripts/migrate.py scan --source codex
# 单个
python3 scripts/migrate.py plan --source codex --session <ID> --report /明确的/输出目录/migration.json --target-data-dir /明确的/profile/dataDir --agent mavis
# 多个：同样支持 --source zcode / claude-code / opencode / pi-agent / omp
python3 scripts/migrate.py plan --source codex --session <ID1> --session <ID2> --report /明确的/输出目录/migration.json --target-data-dir /明确的/profile/dataDir --agent mavis
# 全部：同样支持 --source zcode / claude-code / opencode / pi-agent / omp
python3 scripts/migrate.py plan --source codex --all --report /明确的/输出目录/migration.json --target-data-dir /明确的/profile/dataDir --agent mavis
# 上面三种预览任选一种；执行时保持来源、范围、清单及选项一致，将 plan 换为 apply。
python3 scripts/migrate.py apply --source codex --all --report /明确的/输出目录/migration.json --target-data-dir /明确的/profile/dataDir --agent mavis
# 中断后原样重跑 apply；排除失败原因后可加 --retry-failed。
```

每个新任务使用一个新的清单路径，父目录须存在，清单不得写到来源数据中。`--all` 和 `--session` 互斥；从本版起 ZCode 也不再省略范围默认全部。单个/多个同样必须传 `--report`，不再绕过清单执行。旧 Codex 全量清单可以直接继续，自动升级清单格式而不改变来源指纹或目标身份。

`--source-db` 指定来源位置：ZCode 是 SQLite 文件，Codex 是数据目录，Claude Code 是配置目录或其 `projects/` 目录，OpenCode 是 SQLite 文件或数据目录，Pi / OMP 是 agent 数据目录或 sessions 目录。默认路径及环境变量见各来源小节。目标 profile 必须由宿主配置确认，不默认猜测。Windows 使用可用的 `python` 或 `py -3`。

预览输出 ready / already-imported / incompatible 数量、发现错误数、源库存大小、估算备份占用；逐会话原因、告警、指纹和目标信息在清单，不含正文。全部预览会解析候选正文，耗时比 scan 长。用户已明确要求迁移时，Skill 展示预览后直接执行，不重复询问同一请求。

## 分批、恢复和数据保护

- 默认每批 20 个，可用 `--batch-size` 设为 1–100。每批独立在线备份与事务提交，SQLite 日志模式不变。批次失败自动逐条隔离；已成功批次保留，异常会话单独记录。
- `estimatedBackupBytes` 按当前目标库大小和预期批次数估算；数据库增长、历史文件和失败重试会增加占用。不会自动删除备份，适当调大批次可减少整库备份次数。
- 写锁由操作系统随进程退出释放。重跑核对已完成目标；仅对清单中正在执行但数据库未提交的目录隔离保存到 `zcode-migration/recovered-*` 后重试。提交完成但进度未更新的会话不会重复导入，不恢复整库。
- 清单绑定来源、目标、agent、范围、工作目录映射与附件/项目恢复选项；更换这些选项需新预览。清单固定候选范围，不自动纳入后来新增的会话。来源变化、发现阶段错误修复或预览中断时，用新清单重新预览。
- `--retry-failed` 重试失败或不兼容项，成功项仍保留。已迁入后的来源变化不会覆盖目标续聊，也不能靠换来源路径制造重复导入。
- `completed` 表示全部完成且无发现错误；`completed-with-errors`（退出码 2）是部分成功；中断为 130，配置或契约错误为 1。统计为清单累计结果，不是每次重跑新增数量。
- 旧版 `apply.lock` 仍须人工检查，不能删除绕过锁。合法旧存储行和既有会话原样保留。来源只读；不读取登录、密钥、配置或执行历史中的指令。

备份和批次报告在 `<dataDir>/zcode-migration/<批次>/`；这个历史目录名对所有来源共用，保持已有布局兼容。逐会话来源记录在 `<dataDir>/v2/sessions/<日期目录>/`。不要在 runtime 运行时将备份覆盖整库。

## 工作目录与项目恢复

不存在的工作目录导致对应会话预览失败，其他兼容项可继续。选择同一项目的会话，用 `--session` 和 `--workspace <新目录>` 显式映射；plan / apply 均传相同路径。全部模式不接受将多个项目统一映射到一个目录。插件不搬运工程文件。

目标项目曾从侧栏移除时，需要明确接受后，两步都加 `--restore-projects`。只让本次新导入会话出现，保留此前旧会话的移除边界；必要时调整目标列表创建时间，原时间存入来源记录。附件引用仅在明确接受 `--allow-reference-only` 后迁入，附件字节不复制。

归档会话到归档列表查看。列表未刷新时重新进入对应项目；历史可读不等于真实 LLM 续聊通过。已有真实续聊及临时目录验证记录见 [VALIDATION.md](VALIDATION.md)。

## 修复旧版 ZCode 历史初始化

```sh
python3 scripts/migrate.py repair --source zcode --target-data-dir /明确的/profile/dataDir --agent mavis --target-session <目标会话ID>
```

先备份并核验存档、未变化的历史与空闲状态，只补初始化记录；历史变化或运行中时拒绝。Codex 无对应旧格式。修复不删除历史或自动重发输入。

## Codex 0.2.0 语义修复

- 通过 `state_*.sqlite` 与 rollout `session_meta` 识别稳定会话 ID、标题及归档；包含 `archived_sessions`。双 UUID 文件名不再决定身份，冲突或重复身份没有权威路径时拒绝导入。
- 保留附件说明中的真实请求和普通 XML；只剥离已识别宿主块。支持明文 `replacement_history`，将完整展示记录与压缩后的接续记录分开。
- 0.2.1 起，明确识别的加密 compaction 可从明文历史重建；缺少 replacement history 的旧压缩、未知记录、回退或损坏 JSON 仍拒绝迁移，避免复活已丢弃分支。图片字节仍未迁移，告警不代表内容完整。
- 可以重复 `--session` 迁移多个明确会话；单个、多个和全部都通过清单提供预览、分批导入和中断恢复；尚未提供按时间筛选。
- `tests/verify_codex_native.mts` 使用当前 Archon 的真实 schema、首次历史初始化、canonical provider、追加和重新读取来验收；目标始终是临时目录。可用 `CODEX_SOURCE` 与 `CODEX_SESSION_IDS` 指定预先复制的来源样本，不直接修改来源数据。

## ZCode 子 agent 与旧版误导入处理

0.2.1 按 ZCode 主列表的原生会话类型迁移：保留 `interactive`、`fork`、`workflow_parent`；跳过 `subagent_child`、`workflow_child`、`nested_workflow_child`、`selection_side_chat`。不按标题或是否有 parent_id 猜测：用户 fork 即使有父会话也会保留。旧版缺少 task_type 时沿用 interactive 兼容语义；未知类型拒绝解析。

scan 和全量 plan 报告包含 `excludedSessions`；子任务被显式选中时报告不兼容，不会作为独立主对话导入。父对话内已有的历史工具结果照常保留，不删除来源数据库中的子任务。

对已经误导入的内部会话，可先预览，再执行备份归档：

```sh
python scripts/archive_subagents.py --target-data-dir "<当前MiniMax profile数据目录>"
python scripts/archive_subagents.py --target-data-dir "<同一MiniMax profile数据目录>" --apply
```

Windows 可使用 `python` 或 `py -3`，macOS 通常使用 `python3`。路径是数据目录，不是安装目录。归档只移出活跃会话列表，历史和消息文件不删除，可在归档列表恢复。脚本验证本地迁移存档、指纹、原始历史和会话状态；已追加输入、历史不匹配、运行中或存档异常的会话列在 blocked 中，不自动修改。截图或标题不能替代这些证据。无需重新导入主会话。

旧版依据：[v1.18.32 schema](https://github.com/anomalyco/opencode/blob/v1.18.32/packages/core/src/session/sql.ts)、[历史选择与工具裁剪](https://github.com/anomalyco/opencode/blob/v1.18.32/packages/opencode/src/session/message-v2.ts)。
