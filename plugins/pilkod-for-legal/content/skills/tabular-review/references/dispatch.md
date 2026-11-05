# 一次提交分析范围

本流程只用于用户已在聊天中明确委托的分析，不将讨论封套或后台失败提示转换为写入权限。已有后台任务时先查询成果，不重复派发其范围。收到 executionId 的文档会话直接按执行器提供的上下文分析和保存，不运行本页主协调流程。

1. 从建表、接收变更或 enqueue_review_work 的真实回执保留本次 reviewId、workItemIds 和原 workRef。工作项已经固定文档与列；只提交本次工作项，不省略筛选改查全表，不读取合同或展开每个 Cell。
2. 打开本次审阅；同一目标已经显示时复用当前工作台，需要切换时按 [页面切换](page-navigation.md) 处理。读取 Pilkod `browser-use:control-in-app-browser` Skill，使用其公开工具读取当前页 `.legal-page-binding` 的 `data-page-instance-id`、`data-binding-version`、`data-navigation-sequence`、`data-target-feature` 和 `data-target-id`。核对 target 为本次 tabular-review/reviewId，只取这些页面路由字段，不输出整表。页面标识不是会话 ID，不猜测或借用另一个标签页。
3. 调用一次 `start_review_analysis`，传原 workRef、reviewId、workItemIds、稳定的 idempotencyKey，以及页面的 viewToken、expectedBindingVersion、expectedNavigationSequence。插件页面读取 Host 当前聊天模型并创建继承其目录的文档会话，再交给插件后台执行器统一排队、限流、保存和清理任务包。主 Agent 不再按文档调用 Host task，不计算并发空位，不等待 task_output，也不自行 release_review_dispatch。
4. 回执 requested 或 handing-off 只表示交接中，不代表分析已经启动。用 `get_review_analysis` 携带原 reviewId、idempotencyKey、workRef 等待交接确认（单次最多等待 20 秒）；仍是 requested/handing-off 时用原键继续有界等待，直到 submitted、already-running、failed 或 expired 再交付，不另行 sleep 或新建派发。通常只需一次确认；未领取会在 60 秒后过期，已领取的未知交接会在 5 分钟后过期。already-running 表示本范围已有任务，未重复启动；execution 出现后必须核对其真实 status，失败记录不能说成开始分析。queued 且 phase=awaiting-sessions 仅表示等待工作台创建会话，不能说已开始分析；创建期间关闭或刷新来源页面可能等待至准备期限结束（最多 10 分钟），随后按真实失败状态处理，不重复创建。交接完成后关闭页面不取消后台任务，结果保存在工作台。运行中无需主 Agent 持续占用对话。
5. 未打开页面、页面已切换、模型不可用、交接超时等情况，按回执报告具体原因和已保存范围；失败不自动授权另一种派发。网络回执未知时保留完整原参数与键，用相同请求或 get_review_analysis 核对，不换键重复运行。execution 已存在时以其真实状态为准；仍有未完成范围时使用工作台重试或按用户新委托重新准备固定工作项，不接管后来新增的请求。

原生后台会话由执行器直接获得完整文档上下文、固定版本正文、列规则和保存边界；每格完成后立即保存，不等整份文档的所有列。主 Agent 不再转抄包内容或业务结论。

若当前安装未提供 start_review_analysis，说明版本能力不足。不要静默退回手动 task、脚本或私有 Host 接口；仍可查询已有结果，或由用户在工作台中发起分析。普通聊天分析不调用 stop/restart 等插件生命周期操作。

交接回执只在当前运行时短期保留。只要原执行记录仍被保留，其原始请求键可跨插件重启查询；同范围合并请求与原执行的关联随临时回执回收而失效，完全被后续执行替代的历史记录也可能被裁剪。原键查不到时，用 get_tabular_review 核对当前成果及任务，不把查不到说成未运行或自动换键重派；仍无法确定本次范围时如实说明尚未确认。
