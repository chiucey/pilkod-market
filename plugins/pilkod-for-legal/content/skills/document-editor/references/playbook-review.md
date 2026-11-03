# 以 playbook 审查 DOCX

推荐不会生效。只有用户明确选用一本 playbook 或推荐的规则后才开始；自然语言“用这本检查”已经足够，无需 UI 重复选择。被编辑/审查文档只支持 DOCX。默认先按 [呈现流程](./editor-context-and-navigation.md) 打开真实 Editor，再渐进写入。

默认 generateSuggestions=false，只检查并返回逐项结论；用户明确要求提出修改建议时才设为 true。无 playbook 的普通审查不得自动选择最近 playbook。分类按所选规则计数，每项只计一次，不按证据条数累加；待判断和未检查不计入符合。用户后续请求首选或退让立场修改时，读取同一 run 的固定规则，沿用 append_suggestions 和已有建议关联，不改写原检查结论。

## 开始与接续

1. 新任务导入明确指定的 DOCX，用稳定 editorId 调用 `open_document_editor`。继续已有文档可用 `list_document_editors` 按名称查找，不猜最近任务。读取 `get_document_editor`，确认正文保存、当前 revision 与请求范围。
2. 查找并读取被明确选用的保存版本。`start_document_playbook_review` 提交固定 `rulesSource:{kind:library_version,playbookId,versionId}`、非空 ruleIds、whole 或精确 selection、用户说明及 generateSuggestions。审查固定规则、范围和正文，后续库的新版本不影响它。用户要求“只检查”设置 generateSuggestions=false，仍显示 UI。
3. 工作台右侧可直接选择 playbook、勾选审查项及填写补充要求；这些准备不会创建审查。点击“开始审查”会先保存并固定当前正文，再启动原生后台任务，不向主聊天 append。返回管理后仍沿用用户已经选定的版本，不自行换成最新版本。收到后台目标时，沿用给出的 `workRef`、editorId/runId 和本轮 `execution`，直接读取原 run，不重复 start、不换最新规则。`read_document_playbook_review(section=run)` 查看生命周期、currentness、remainingRuleIds 和固定规则；section=content 按返回 nextOffset 读取冻结正文。
4. 按完整审查项渐进提交。current 且 ready/partial 可继续原 run；complete 只核对已完成结果。stale/cancelled 不接受新输出；重新检查需用户明确请求创建新 run。用户明确按同一文档历史规则复查时可选 `rulesSource:{kind:review_snapshot,previousRunId}`，不可跨文档复用历史快照或自动代替已删库版本。

## 写检查与建议

`submit_document_playbook_review(mode=checks)` 每批提交完整 checks。assessment 为 conforming、acceptable_fallback、deviation、needs_judgment、not_applicable；每项提供与规则对应的解释，不把未检查等同合规。找到条款使用 quote 的精确 UTF-16 range/originalText；未找到时使用 missing 说明查找覆盖范围。

有修改建议时，同一次提交提供完整 changes 及 newChangeLinks；links 指向本批 check/finding/local change ID，由服务原子生成并保存真实身份。已有合法 pending 建议可用 existingChangeLinks 关联，避免重复红线。不得先普通 propose 再补 links。pending/queued 冲突不阻止只保存检查；建议受阻时如实返回 blocked 和真实冲突，不伪报已创建修改。

每次用实际读取的 expectedRunRevision/expectedEditorRevision 与稳定幂等键提交。绑定后台任务必须携带本轮 `execution`，服务同时校验固定目标、凭据和双版本；不能省略凭据、换工作区、另建 run 或先普通 propose 绕过。收到 review 目标只用 `mode=checks` 处理 remainingRuleIds；收到 suggestions 目标只用 `mode=append_suggestions`，关联指定 checkId，遵守本轮首选或退让立场。runId 本身不授予后台写回资格。覆盖数由服务计算，全部规则有结果即 complete，没有 finish/claim/lease/attempt；不要发送虚构百分比、token 流或 UI 动画字段。

## 检查后调整

用户明确为已经完成的检查拟修改时，可对 current 且未取消 run 使用 `mode=append_suggestions`，链接持久 check/finding IDs；不覆盖原 assessment，也不增加覆盖数。工作台的“建议修改”直接派发固定检查和立场的新后台任务，仍使用该 run 冻结的规则，不把退让立场保存回 playbook。只有原 checks 隐含完成，不表示建议被接受或正文已修改。

接受/拒绝仍由现有 UI 建议卡处理。接受修改、人工正文变更或历史还原后，依赖旧正文的审查永久 stale；恢复相同文字也不会复活旧 run，接受建议不等于自动判定合规。建议卡反馈保存固定 queued 引用并追加到主会话，用户发送后按 [Editor 反馈流程](edit-proposals.md#建议卡反馈) 响应原请求，不重复创建、不另起普通隐藏任务，也不改写原 playbook 审查。旧审查来源保留在建议历史中，不伪报已完成复查。

工作台“停止”先撤销本轮执行写入资格，再请求 Host 停止；已返回检查和建议保留。停止请求返回不等于 Host 已收尾，收尾前不启动竞争任务。执行停止不永久取消业务 run：current 的 ready/partial 可由用户继续剩余项，complete 可按明确要求补建议，新一轮使用新凭据。后台不可用时明确拒绝并保留输入，不退回主聊天交接；普通对话不能替换绑定任务的凭据。

`control_document_playbook_review(action=cancel)` 则永久停止该 run 接受后续输出，保留已完成项；它不是工作台执行“停止”的替代，也不能声称停止了 Host 模型进程。写结果未知先用原参数/原 key 重放或读 receipt，不能只改 revision 或新建 run 绕过。保存后再次 read 核对实际数量、建议和有效性。
