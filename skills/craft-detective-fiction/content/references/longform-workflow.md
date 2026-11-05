# 中长篇项目工作流

## 目录

1. 解释器与项目入口
2. 最小创作契约
3. 建立案件真相
4. 设计读者体验与登记簿
5. 校准原创风格
6. 恢复项目与交接
7. 章节循环与 canonical 门槛
8. 阶段复盘与结构变更
9. 完稿审计与清洁导出
10. 权威关系与版本规则

## 适用档位与缩放

本工作流的机制按交付规模分档启用，不一刀切；`SKILL.md` 的公平性与因果硬门槛在所有档位都不降低：

- **短篇（约 3 万字以内）**：通常按 `SKILL.md` 任务路由直接交付，不建档。选择建档时保留案件闭合（§3）、合并节点的公平性审计（§8）与 §9 导出。章节仍写 `status` 与六项 checks——这只是章节模板默认的六行 frontmatter，`ledger_actions` 四键与 `continuity_dependencies` 留空列表即合规，不构成额外簿记。真正不启用的是：登记簿交叉核销（`mystery-ledger.md` 可为空）、版本递增与审计快照；`--strict` 因快照前置而可选，不用时以普通审计加导出前人工确认替代。
- **中篇**：在短篇基础上启用 `mystery-ledger.md` 登记簿与章节 `ledger_actions` 核销；版本号、审计快照状态与交接检查点按需启用。注意 `--strict` 以审计快照为前置：启用严格检查时必须同步维护 `audit-report.md` 的 `current`／`stale` 状态。
- **长篇与系列**：启用完整机制——章节 `draft`／`canonical`／`superseded` 状态机、权威档案版本递增、审计快照 `current`／`stale`、`notes.md` 交接检查点，并以 `--strict` 作为导出前置。

## 1. 解释器与项目入口

先解析本 Skill 的实际目录，随后探测当前环境可调用的 Python 3。依次考虑系统 `python3`、系统 `python`、Windows Python Launcher 的 `py -3` 和 Codex 提供的 bundled Python；不要假定任何固定命令名。把当前 shell 中已验证可运行的调用方式记作 `<python>`。

先运行单行验证命令：

```text
<python> --version
```

确认输出为 Python 3 后再运行脚本；若命令不存在或版本不是 Python 3，继续探测下一候选。路径中有空格时使用当前 shell 的安全引用方式。本文中的 `<python>`、`<skill-dir>`、`<project-dir>`、`<title>` 和 `<count>` 都是占位符，不应原样复制到执行命令。

仅在目标目录不存在或为空时初始化：

```text
<python> "<skill-dir>/scripts/init_project.py" "<project-dir>" --title "<title>" --target-words <count>
```

生成结构：

```text
<project-dir>/
├── project-charter.md
├── case-bible.md
├── outline.md
├── mystery-ledger.md
├── style-guide.md
├── notes.md
├── audit-report.md
├── chapters/
└── exports/
```

目标目录已有内容时不要重新初始化。先只读映射现有设定、大纲、正文、研究笔记和历史版本，再补齐缺失的权威关系与章节元数据；不得用模板覆盖用户文件。

## 2. 最小创作契约

先从用户原话吸收已确定信息，再按 `intake-and-structures.md` 补真正阻塞的选择。完整项目默认最多覆盖以下八类信息，但一次只问最关键的 1–3 项：

- 交付规模与形式
- 核心谜题和读者体验
- 时代、地点与现实度
- 调查者及 POV
- 类型坐标与基调
- 内容与安全边界
- 系列定位
- 用户保留决定与 Agent 可代决事项

把结果写入 `project-charter.md`。明确哪些结构变更必须再次确认，以及章节进入 `canonical` 前是否要求逐章用户确认。未阻塞当前产出的未知项先进入 `notes.md`，不要伪装成已确认契约。

## 3. 建立案件真相

读取 `mystery-engineering.md`，在 `case-bible.md` 中至少完成：

1. 用一句话写清谁、为什么、何时何地、如何实施与掩饰、在哪里失败。
2. 建立诱因、决定、准备、接近、实施、掩饰、善后、调查应对和失败点组成的因果链。
3. 验证真凶的动机、手段、机会、风险承受与“为什么是现在”。
4. 建立嫌疑人矩阵，使每名主要嫌疑人都有可疑事实、非凶案秘密和可验证的排除依据。
5. 以故事所需粒度建立真实时间线、空间状态和关键物件持有链。
6. 在案件圣经中创建稳定的 `Q-###` 终局结论，并为每项结论写明推理步骤、替代解释与排除方法。

`case-bible.md` 是 `Q-###` 定义的唯一所有者。真相尚未闭合时，不写依赖该真相的正式长篇章节；可以交付明确标为可变草稿的概念样章。

## 4. 设计读者体验与登记簿

根据已版本化的案件圣经编写 `outline.md`，不要为了迁就偶然写出的场景反向篡改真相。每章规划至少说明：

- POV、故事时间、章节功能与前后依赖
- 进入本章前读者掌握的模型
- 本章新增、修正或误导的信息
- 计划执行的登记簿动作
- 人物关系或风险的不可逆变化
- 章末推进力

在 `mystery-ledger.md` 建立稳定 ID：`C-###` 为推理线索，`F-###` 为人物、主题或未来事件伏笔，`R-###` 为观察真实但解释错误的红鲱鱼。`C-###` 必须引用案件圣经中现存的 `Q-###`；每个 `R-###` 必须有真实观察、表面解释和真实意义。

同一登记项始终只保留一行，通过实际位置、回收位置和状态推进生命周期。废弃项保留原因，禁止删除、复制或复用 ID。

## 5. 校准原创风格

读取 `style-and-scene.md`，把用户喜欢的作品或作者转译为视角距离、句长变化、意象密度、对话压力、心理深度、幽默、暴力显隐和节奏等高层特征。不得复制原句或仿写在世作者的独特风格。

先写约 200–400 字原创样章；用户确认后，将其作为锚点写入 `style-guide.md` 并递增风格版本。允许后续经确认更新基线，不把早期选择永久锁死。

## 6. 恢复项目与交接

新上下文或中断恢复时先读 `notes.md` 的“交接检查点”，确认：

- 当前阶段
- 最后一个 `canonical` 章节
- 当前在写章节
- 下一步动作
- 等待用户决定
- 连续性快照
- 最新审计版本与 `current`／`stale` 状态

再核对检查点引用的章程、真相、大纲、登记簿和风格版本。只读取当前章节 `continuity_dependencies` 中列出的 `chapter-XX.md` 及确实受当前任务影响的其他章节；不要机械读取全部前文，也不要仅凭笔记覆盖权威档案。

完成一章、暂停工作、改变结构或交给新上下文前，更新交接检查点。开放问题与研究结果先留在笔记中；确认后按笔记模板的晋升规则写入唯一权威所有者并记录新版本。

## 7. 章节循环与 canonical 门槛

章节状态只使用 `draft`、`canonical`、`superseded`：

- `draft`：正在写作或尚未通过完成门槛。
- `canonical`：当前叙事采用、允许进入清洁导出的章节。
- `superseded`：已被结构决定淘汰，保留用于追踪但不得导出。

### 章前

1. 从 `case-bible.md` 读取本章相关真相、时间段与 `Q-###`，核对真相版本。
2. 从 `outline.md` 读取本章目标、进入前认知和前后依赖，核对大纲版本。
3. 从 `mystery-ledger.md` 读取计划动作及当前状态，核对登记簿版本。
4. 从 `style-guide.md` 读取关键约束和已确认锚点。
5. 根据人物位置、信息得知、未完场景和关键物件，填写最小 `continuity_dependencies`；列表项必须是现存的 `chapter-XX.md` 文件名。

### 章后

1. 检查 POV 是否有能力知道、看到、听到或推断正文信息。
2. 检查人物位置、时间、称谓、伤势、物件持有和信息得知顺序。
3. 按章节 `ledger_actions` 核销登记簿：`seed` 的实际出现位置包含本章且状态为 `已埋设`、`已强化` 或 `已回收`；`reinforce` 的实际出现位置包含本章且状态为 `已强化` 或 `已回收`；`pay_off` 的实际回收位置包含本章且状态为 `已回收`；`retire` 的状态为 `已废弃`。
4. 对大纲偏差选择 `none`、`accepted` 或 `change_required`。前两者可继续；`change_required` 立即进入结构变更流程。
5. 将连续性变化、开放问题、研究项和已接受偏差写入 `notes.md`，并更新交接检查点。
6. 若项目章程要求逐章确认，取得用户确认；否则明确记为 `not_required`。

把可判定结果写入章节 frontmatter：`pov`、`continuity`、`ledger_synced`、`notes_synced` 只用 `pending`／`pass`／`fail`；`outline_deviation` 只用 `none`／`accepted`／`change_required`；`user_approval` 只用 `not_required`／`pending`／`approved`。frontmatter 中的列表写行内形式（`pay_off: [C-001]`）或块式序列（`pay_off:` 后跟缩进的 `- C-001` 行）均可通过结构检查。

注意这六项 checks 是 agent 的**声明**——脚本只验证枚举值合法，无法判断检查是否真实执行；真正被机器交叉**验证**的是登记簿核销、依赖章节存在性和 `Q-###` 引用完整性。填入 `pass` 前必须实际完成对应检查。

在目标章仍为 `draft` 时执行 canonical 候选检查：

```text
<python> "<skill-dir>/scripts/audit_mystery_project.py" "<project-dir>" --chapter "chapter-XX.md"
```

只有以下条件同时成立时才把状态改为 `canonical`：四项检查均为 `pass`；大纲偏差为 `none` 或 `accepted`；用户确认为 `not_required` 或 `approved`；登记动作已按上述规则核销；依赖章节存在；单章候选检查为 0 error。状态改变后再运行同一命令确认。

## 8. 阶段复盘与结构变更

在案件设计完成、大纲批准前、约 10%–20% 进度节点、重大结构变更后、揭晓前和完稿时，按 `audit-rubric.md` 执行相应深度的人工审计。短篇可合并节点，不机械固定每五章或固定比例。

修改真凶、手法、核心动机、死亡时间、世界规则、关键线索或主要反转时：

1. 立即将 `audit-report.md` 标记为 `stale`，暂停受影响章节扩写与导出。
2. 先更新 `case-bible.md` 的一句话真相、因果链、时间线和相关 `Q-###`，递增真相版本。
3. 更新 `mystery-ledger.md` 的受影响 ID 和版本，再更新 `outline.md` 的信息顺序和版本。
4. 搜索并检查所有受影响章节的人名、物件、时间、证词、内心陈述与 `continuity_dependencies`；不再采用的章节标为 `superseded`。
5. 把决定、影响范围和下一动作写回 `notes.md`，并按项目章程取得必要的用户确认。
6. 对受影响范围运行结构检查和人工公平性回归审计；记录所覆盖的各权威版本与章节后，才把审计快照恢复为 `current`。

局部措辞或非关键场景调度可直接修订并复查本章；位置、物件、伤势或信息得知变化需要检查依赖章节与登记簿。不得只改正文而让权威档案保持旧版本。

## 9. 完稿审计与清洁导出

先完成 `audit-report.md`，记录报告版本、`current` 状态、覆盖章节，以及章程、真相、大纲、登记簿和风格的确切版本。先修硬失败，再处理重大警告；结构脚本不能替代人工重建推理。

对完整项目运行严格检查：

```text
<python> "<skill-dir>/scripts/audit_mystery_project.py" "<project-dir>" --strict
```

严格检查 exit 0（无 error、无 warning，且审计快照为 `current`）后，输出到项目的 `exports/`。权威档案中残留的 `待定` 会产生 warning 并阻断严格检查；`notes.md` 是允许保留未决项的工作区，其中的 `待定` 不参与严格检查：

```text
<python> "<skill-dir>/scripts/build_clean_export.py" "<project-dir>" "<project-dir>/exports/<title>-clean.md"
```

已有同名导出且确需替换时才追加 `--replace`。输出不得位于 `chapters/`、不得等于任何输入章节，也不得指向项目根、文件系统根或其他源档案。导出器只合并编号连续且状态为 `canonical` 的章节，并在原子替换前拒绝 draft、superseded、缺章、模板标记、TODO、内部 ID、YAML 或残留 HTML 注释；任何失败都不得改变既有输出或源章节。

导出器成功后会执行严格清洁检查。最后人工确认章节顺序、标题和正文完整，且不含真相档案、创作笔记、审计结论或其他剧透元信息。

## 10. 权威关系与版本规则

- `project-charter.md`：项目契约和用户边界的唯一所有者。
- `case-bible.md`：客观真相、世界规则和 `Q-###` 的唯一所有者。
- `outline.md`：叙事计划与读者信息顺序的唯一所有者。
- `mystery-ledger.md`：`C/F/R-###` 生命周期的唯一所有者。
- `style-guide.md`：语言约束与原创锚点的唯一所有者。
- `notes.md`：临时检查点和待晋升信息，不覆盖任何权威文件。
- `audit-report.md`：最近一次正式审计快照；它引用各版本，不成为事实来源。

权威内容发生实质变化时，递增该文件版本并更新下游引用；所有覆盖旧版本的审计快照立即变为 `stale`。只有回归范围、版本和章节覆盖都已记录的正式审计，才可标记为 `current`。
