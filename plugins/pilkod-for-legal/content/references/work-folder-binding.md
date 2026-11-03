# 工作文件夹绑定

表格式审阅、文档编辑和时间线分析共用此流程。先绑定保存位置，再调用本地业务工具；全局 `list_review_templates` 和入口状态 `get_workbench_status` 无需绑定。

业务任务从“选择与复用”开始；仅打开工作台或排查入口问题时，跳到[仅打开工作台](#仅打开工作台)。

## 选择与复用

1. 页面交接的任务、反馈或讨论已有 `workRef` 时，沿用它与原 `source`、成果 ID 和请求范围；不因切换 Skill、当前页面变化或材料来自别处而重新绑定。
2. 同一业务任务已经明确保存文件夹并取得有效 `workRef` 时，各功能复用它，不为每次业务调用重新关联；纯打开请求按下文核对并保留已关联页面。业务任务没有绑定时，按[页面核对与旧入口](#页面核对与旧入口)中的公开 Host 会话查询选择项目目录或主目录共享目录。要在另一保存目录工作，使用对应 Host 项目会话；不要用改 URL、刷新或重复 open 绕过已有成果的页面绑定与未保存保护。无法可靠判断时说明原因，不从 Primary working directory、插件进程 cwd、最近成果或材料路径推断。
3. 调用 `open_work_folder({ directory: 规范绝对路径 })` 或无项目时的 `open_work_folder({})`，保存返回的 `work: { workRef, directory, name, initialized, syncLocation? }`。它检查和绑定目录；共享入口会按需建立外壳，但两者均不创建 `minimax-for-legal/` 或业务数据。业务任务在新会话尚无有效引用时，重新 open 取得本次引用；插件读取该文件夹已有的数据，不新建一份历史。

返回 `work.syncLocation` 表示该文件夹疑似位于云同步目录（`provider` 为客户端类别）。在本次业务任务中向用户简短转告一次：同步可能使数据库产生冲突副本或损坏，客户材料也会经由该云服务上传；建议用户在 Pilkod 中改用本机未同步的项目文件夹。不阻断任务，不替用户改选位置，也不把没有该字段解释为文件夹一定未同步。纯打开工作台由页面首页展示提示，无需复述。

`workRef` 是不透明的路由引用，不是文件路径、Host 身份凭据或读取授权。不要自行构造，不让用户填写。用户授权读取的材料可位于其他文件夹；添加材料目录不改变保存位置，也不授权扫描全部内容。

## 首次保存

返回 `initialized: false` 时，仅浏览首页、空工作台或模板无需初始化。用户已明确委托导入材料、创建成果或保存配置时，先调用 `initialize_work_folder({ workRef })`；成功返回 `initialized: true` 后再执行原业务操作，无需为同一已授权保存另行确认。已初始化的绑定直接复用，不重复初始化。

初始化仅创建该文件夹的本地工作数据。失败时保留原位置和错误，不回退到全局目录，不切换到材料目录，也不覆盖、迁移或重建已有但不可读的数据。

用户明确要求关闭工作时才调用 `close_work_folder({ workRef })`，关闭前先处理当前页面的未保存内容。它释放插件连接并保留磁盘数据；共享此引用的页面和任务需重新打开目录，不能继续使用旧引用。不要为了腾出容量擅自关闭其他工作。

## 每次调用与页面交接

- 除上述公共工具及全局模板查询外，所有本地业务工具在原参数顶层加 `workRef`，原业务字段不变。例如 `import_legal_document({ workRef, filePath })`、`get_tabular_review({ workRef, reviewId })`；封套工具仍为 `{ workRef, source, request }`。引用文档中的业务参数示例同样适用这条规则。
- 导入、创建、读取、修改、导出、页面绑定及原参数重试均固定同一 `workRef`。讨论保留原 `source` 的 scope；不能为适应当前绑定改写来源，不能在读取失败后切到同 ID 的另一份副本。绑定失效时说明阻碍，不擅自把旧请求换绑后继续写入。
- 首次打开 Mini App 不需要 `viewToken`。业务功能或成果路径的 Host `miniapp.path` 必须携带 `workRef`，已有成果还需真实目标，例如 `/legal/tabular-review?workRef=实际引用&reviewId=实际ID`；所有动态值分别用 `encodeURIComponent` 编码。业务空页只省略成果 ID，不省略 `workRef`；支持的 Host 可由无参数首页自动关联；显式首次入口由 `workDirectory` 或 `workMode=shared` 建立初始绑定，两者互斥，不与 `workRef` 或成果 ID 混用。打开已有成果不要求重新初始化。
- 业务任务尚无已挂载工作台且已取得有效 `workRef` 时，可打开绑定首页：`{"action":"open","pluginId":"minimax-for-legal","path":"/legal?workRef=<编码后的真实 workRef>"}`，再通过所属功能的公开列表或首页成果目录查找用户指定成果。
  页面实际打开后才能读取其公开页面标识；不要因尚无 `viewToken` 而停止首次打开，也不自行拼接 `plugin://` URL。
- 已有页面切换目标仍遵守各 Skill 的 `bind_legal_page` 与未保存输入守卫，不用再次 open、改 URL 或刷新绕过。页面后续请求与“添加到对话”的交接自动携带当前绑定，用户无需手填引用；收到交接后继续使用其中的原绑定和原成果。

## 仅打开工作台

用户只 @ 本插件或明确要求打开插件时，优先执行入口 Hook 的流程，不先追问业务功能，不加载法律业务 Skill 或执行分析。Host 在消息发送前唤起的无绑定页面只表示插件已启动，不代表已选定保存位置。纯打开不扫描目录或查询模板，也无需逐步说明打开过程。Host 更高优先级明确要求的读取仍按最小范围执行，随后结束本轮。

先按 Hook 提供的**本轮 Host 会话标识**调用一次 `get_workbench_status({ sessionId })`。它仅向该会话所属的当前可见页面发起本次小范围状态读取，不读取整页或正文，也不初始化数据。只有 `status:"ready"` 才表示唯一页面刚响应了本次查询、已关联并挂载可用工作台且无连接或恢复遮罩。此时立即只回复“工作台已打开。”并结束，不再加载 Browser Skill、读取 Browser、查询 pilkod、检索记忆或文件；保留原业务路由和未保存输入，不再次打开。

没有有效会话标识、页面未响应、恢复中或页面有歧义时，不宣称成功、不循环查询、不选择最近页面。需要排查未打开或旧 Host 时，才执行下面的页面核对。状态回执只是本次页面状态，不是 Host 身份认证、目录选择或业务操作授权，不能替代成果绑定及离页保护；关闭、重启后也不能使用旧成功回执。

### 页面核对与旧入口

优先复用本轮已有的最新成功 Browser 页面事实；状态仍未知才通过公开 Browser 核对**本会话**的插件页面，不为已经明确的状态重复 `inspect`。使用 Browser 时按 Host 要求先加载其 Skill，已有有效加载回执时复用。URL 带 `workRef`、`[data-app-shell="legal"]` 已挂载且没有连接或恢复遮罩，表示工作台已关联；保留当前业务路由和未保存输入，不再次 `miniapp.open` 或查询会话。未初始化的首页也属于已关联工作台，不要求 `data-page-instance-id` 非空。正在关联时保留页面等待结果；关联失败使用页面重试，保留原选择。不能可靠识别页面状态时，不强制重开。

无参数首页在支持的宿主中通过公开 `window.mcode.miniapp.agent.session()` 无参读取本页所属主会话，确认 `isDefaultWorkspace` 与项目目录后，直接由页面完成关联。它先核对 `capabilities.has("agent.session")`，需要 `agentAccess:["session.read"]`；仅保留会话标识与保存位置字段，不列举其他会话、不使用回复正文、不依赖模型传目录。已有 `workRef`、显式首次目录或共享入口优先，业务深链和恢复不重新选择位置；为就绪回执读取所属会话标识不改变其绑定。

没有页面时，通过 Host `miniapp({action:"open",pluginId:"minimax-for-legal",path:"/legal"})` 打开首页，让页面关联；`data-host-session-state="pending"` 或连接中时等待结果。权限拒绝、上下文缺失、非法字段和连接失败都保留当前页，不改用 Agent 查询绕过，也不将未知会话当成无项目。重试由页面发起。

只有页面明确未关联且 `data-host-session-state="unsupported"`，即旧 Host 没有当前页面会话查询能力时，才执行旧入口：

1. 在**主会话**调用公开 Host `pilkod({command:"session get",args:{session_id:"me",source:"local"}})`，读取本轮成功回执 `response.session`。`isDefaultWorkspace` 必须为明确布尔值，项目会话的 `workspaceDir` 必须为有效绝对路径；工具不可用、失败或字段缺失时停止，不从 cwd、最近目录或后台子会话推断。
2. `isDefaultWorkspace:false`：调用 Host `miniapp`，参数为 `{action:"open",pluginId:"minimax-for-legal",path:"/legal?workDirectory=" + encodeURIComponent(response.session.workspaceDir)}`。`true`：使用 `path:"/legal?workMode=shared"`。不先调用 `open_work_folder`，不使用历史引用，不自行拼共享目录。
3. 页面代码关联目录、取得当前 runtime 的 `workRef` 并替换 URL，显示已有工作。

收到 Host 成功打开回执不代表已经关联；通过公开 Browser 核对上述已关联状态，证据充分就结束，不遍历成果或复读控件。最终只回复“工作台已打开。”，不列功能、入口或下一步。已关联工作台不再查询会话或重新打开。

共享目录由插件解析为用户主目录下的 `Pilkod For Legal`，所有无项目会话共享其中的工作。纯打开仅按需建立共享目录外壳，不初始化项目数据库或新建成果；同一保存目录的新会话恢复已有工作。项目目录打开只检查已有位置，不创建目录。未获得可靠会话身份或显式入口的页面保持未关联，不能提前显示共享目录内容。

Hook 是指引，不是执行或成功回执。Host 打开失败或结果不明时，立即停止本轮打开并保留当前页，不反复 `open` 或 `inspect`，不调用 `restart`、`stop`、`publish` 自动恢复插件生命周期。`RUNTIME_FAILED` 不等于 runtime 崩溃，也不授权重启共享 runtime；简短说明打开未完成。若原引用失效且页面重试无法恢复，请用户先保留或处理未保存内容，关闭旧工作台标签后在当前对话重新发送 @；不要替用户关闭原页。已有未保存内容或明确成果绑定时，仍通过页面绑定和离页守卫切换，不能用 Host 重载绕过。纯打开成功后不复述目录、内部引用或执行过程；用户询问保存位置或排查问题时再提供必要信息。
