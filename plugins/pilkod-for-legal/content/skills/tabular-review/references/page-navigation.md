# 已有工作台的目标切换

`open_tabular_review` 创建或恢复业务审阅，不负责打开宿主页面。通过宿主公开的 Browser 能力读取此次 `open` 对应页面 `.legal-page-binding` 节点的 `data-page-instance-id`、`data-binding-version`、`data-navigation-sequence`、`data-target-feature` 与 `data-target-id`；页面初始化完成后才有可用的关联标识。这些是本应用公开的页面信息，不是宿主会话 ID 或访问授权。

已有工作台需要切换成果时，先读取公开页面状态，并用 `bind_legal_page` 请求当前页打开 `target: { feature: "tabular-review", id: reviewId }`，让现有未保存输入和在途操作保护参与切页；不要用 Host 强制导航绕过它们。传刚读到的 `viewToken`、`expectedBindingVersion`、`expectedNavigationSequence` 和稳定的 `idempotencyKey`。返回 `receipt.status: requested` 只表示请求已登记，浏览器确认并提交后才是 `applied`；核对公开 DOM 的目标与业务实际显示一致后再声称已打开。核对请求进展或网络重试均复用完整原参数，查询同一回执；`rejected`、`superseded`、`expired` 或版本冲突时尊重当前页面，不生成新键反复抢回。页面控制令牌与 commit/release 由浏览器拥有，Agent 不获取或调用。

单纯打开空工作台不产生审阅 ID；同一目标已显示时直接继续。普通分析写入、进度和完成不请求切页，分析始终使用本次请求固定的审阅。页面标识只在当前生命周期有效，重开后重新读取。

业务 ID 由工作台和工具传递，用户无需手动输入或复制。如果公开 Browser 无法定位此次打开的页面或关联失败，明确说明展示未核验；已获用户委托的分析可继续保存，不用全局最近审阅、其他任务的页面或宿主私有状态替代。
