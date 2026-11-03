# 导出、结束与审阅管理

只执行本次用户明确要求的操作。

## 导出与结束

用户要求 Excel 时，从同一次 `open_tabular_review` 或 `get_tabular_review` 返回的 `workspace` 取得 `revision` 与 `metadataRevision`，作为 `expectedRevision` 与 `expectedMetadataRevision` 调用 `prepare_tabular_review_export`，使用返回的 `exportId` 调用 `export_tabular_review_excel` 获取资源链接。重试沿用原版本对；新名称需重新读取并准备新导出。用户也可直接在工作台下载。

文件超过会话资源传输上限时，`exported` 不含资源 URI 而是 `delivery: "workbench"`，也不附资源链接；请转告用户在表格式审阅工作台中下载，不要猜测或拼接资源地址，也不要反复重试。
返回 `TABULAR_REVIEW_EXPORT_TOO_LARGE` 时，内容超过单个 Excel 文件可安全生成的上限，`retryable` 为 false；消息会说明触发的是文字总量、证据明细行数还是文件大小及其数值，结构化错误中的 `exceededLimit`（`content`、`cells` 或 `file`）与 `limitBytes` 或 `evidenceRows`/`maxEvidenceRows` 给出同样的信息。如实转告，说明完整内容仍可在工作台查看，不要重试，也不要为缩小导出擅自删除文档、列或结果。

尚未完成分析、证据核验或人工核验时仍可导出当前快照，Excel 标注完成与核验状态。工作台没有未完成项或低置信度项时直接下载，有这些情况时会提醒，用户可取消或继续导出；继续导出不标记这些结果为已核验。工具导出同样不代表人工核对，不为导出而清除低置信度标记或改写核验状态。

资源链接返回或下载发起不代表文件已保存。只有用户明确确认“已保存并结束”后，才用 `update_tabular_review` 的 `finish_review`，携带对应 `exportId`，把导出返回的 `revision` / `metadataRevision` 分别传为 `expectedRevision` / `expectedMetadataRevision`，并设 `confirmedSaved: true`。服务端会重检待办、内容与名称版本；其间有修改时，重新导出并等待确认。未确认、下载失败或取消时保留活动审阅。

## 查找与清理审阅

用户要求查找、恢复或清理已保存审阅时，用 `list_tabular_reviews` 查询真实名称和摘要，按需翻页。列表只用于用户明确要求的选择，不将“最近更新”推断为当前任务。

用户明确指定永久删除的范围后，读取最新 revision，再用 `delete_tabular_review`。
对“清理不再需要的”这类模糊请求，先展示候选名称并确认；内部 ID 由工具结果取得，不要求用户提供。
说明删除不可撤销、会移除结果与历史，但不删除用户原始文件或已下载成果。
处理中目标的删除会阻止后续写入，须提醒用户；版本冲突后重新核对，不自动扩大范围或重试删除。
用户也可在当前工作文件夹的首页“表格式审阅”成果列表中找到指定成果，通过该成果的操作菜单选择删除，并在确认弹窗中核对后执行；从任务页面返回首页时先由离页守卫处理未保存内容和在途操作，删除仍沿用所属业务的版本校验和原请求恢复。
