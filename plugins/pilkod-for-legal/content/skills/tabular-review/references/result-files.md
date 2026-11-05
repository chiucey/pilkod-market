# 结果文件提交

本流程用于已获普通审阅写入委托的文档任务；只读模式不写入。
普通当前格默认用平铺单格参数直接调用 set_cell_analysis，不写请求文件。
当前格完整请求 JSON（UTF-8）预计超过 8 KiB、需要按区间或跨页引用原文、已有本次提交的请求文件需要重交，或本文档首次明确参数结构拒绝后，改用请求文件。
结构拒绝包括缺必填字段、字段层级错误及类型错误；按 schema 修正后写入请求文件提交，当前格及本次文档任务后续格均走文件通道。业务、证据、权限或版本拒绝按其原因处理，不因换通道绕过，分类见 [文档分析规则](document-analysis.md)。
修正结构时保持法律内容与列格式，包括 conclusion 的字符串 "true"/"false"；明确拒绝后改参用新幂等键，不能自动改 Cell 版本。
未知回执仅原样重交同一请求文件与键，不改文件内容、不切通道。
8 KiB 是普通提交方式的选择阈值，不是内容上限或错误恢复门槛；不得删减结论、说明或必要证据，也无需精确计数。
版本、证据和幂等校验始终由保存工具执行；Host 文件工具或必要路径不可用时报告具体阻碍，保留已保存格与其他已就绪结果，不把未提交结果称为完成。
请求文件提交明确拒绝后只修具体问题；一次修正后同类错误仍拒绝则停止该格自动重交、报告阻碍并继续其他就绪格，不回退 inline，取得新依据或确认新的可修正问题后才再提交。

provisional 回执提供 `repairFile` 时，插件已生成按引用 ID 补交的单格修复请求；仅修正已核验的待修引文或定位，保留结论、说明、低置信度标记及其他引用。先核对 `changes` 的目标与转换摘要，再原样用 `repairFile.arguments` 调用 `submit_cell_analysis_file`，不重写整格，也无需为传参重读文件。摘要不足以判断时可核对文件或原文。准备好的修复请求不代表已保存；继续检查 accepted/provisional/rejected。无 repairFile 或仍需判断的证据沿原修复流程，不丢弃失败引文换取 completed。

确需新建请求文件时，每核验完成一格，立即用单项 items 写一个请求文件并提交，再继续下一格；不先生成整行答案或整批引文请求。不复用旧要求或旧分析的文件；批量接口能力不是等待其他格的理由。请求文件用 Host 文件工具写在本包提供的 resultDirectory（位于工作文件夹 `minimax-for-legal/exports/tabular-review/results` 内），使用真实绝对路径；每次新提交使用新文件名，未知回执才重交原文件：

```json
{"reviewId":"<本次审阅>","items":[{"expectedCellRevision":0,"idempotencyKey":"<本格尝试键>","analysis":{"documentId":"<本文件>","dimensionId":"<授权列>","conclusion":null,"isLowConfidence":true,"explanation":[{"text":"当前材料未提供被引用附件，无法确定本列值。","citationIds":[]}],"citations":[]}}]}
```

每项沿用 [文档分析规则](document-analysis.md) 的 analysis 结构，expectedCellRevision/idempotencyKey 与 analysis 同层；workRef 只传给 `submit_cell_analysis_file`，不写进请求文件。conclusion 必填，示例 null 是分析者依据材料作出的判断，插件不会给漏填字段补值，也不改成占位文本；有有效值时换成符合列格式的字符串。版本、键和 isLowConfidence 按该格真实情况填写。后台任务提供 executionId 时，在请求顶层原样填写，证据补交也使用同一 ID。写好后用 `submit_cell_analysis_file` 传 workRef、reviewId 和 requestFile；插件读取、定位引文并按单格规则写入，不需要本机脚本，也不重读或复述文件再调用 set_cell_analysis。

短引文默认填写 `{id,quote}`，省略 locator，由插件计算页码与坐标。长引文、跨页片段或需要消歧时，把该引用写成 `{id:"c1",selection:{...}}`，不同时填写 quote/locator：

- `{startOffset,endOffset}`：已核对的规范正文 UTF-16 半开区间（可取自 read_legal_document_text 的分页偏移或候选位置），插件复制原文，无需抄写长引文；
- `{quote}`：从规范正文原样复制的片段，只接受唯一匹配，允许空白和直/弯引号排版差异。

插件保存时定位并计算页码；片段跨页时自动按页拆成多条引用，首条沿用原 ID，其余为 `c1~2`、`c1~3`……，说明中关联 c1 的片段自动关联全部拆分 ID。选择无法唯一定位时该格被拒绝，回执给出候选位置与上下文；回读原文后改用区间或更长的连续片段，不猜候选、不反复改写引文试错。已保存的 provisional 引用可在 citationPatches 中用 `{id, selection}` 按单页片段补正；跨页片段需重新提交整格。

逐项检查保存回执。completed 已完成；provisional 已暂存但未完成，有 repairFile 按上方步骤提交，否则修证据后使用回执 cellRevision、新幂等键和新请求文件；rejected 只修该格。未知结果复用完全相同的文件、版本和键；禁止改文件后用旧键重交，也不通过重开 context 或换键绕过未知结果。版本冲突回读并重新评估，不换版本强行覆盖；旧 provisional 回执不保证还能生成新修复请求，已取得的原文件仍保留供原样重交。请求文件最大 2 MiB，超过限制时把已就绪 items 分批写入；文件本身不授予额外权限。

本文件全部授权目标完成，或存在明确阻碍无法继续时，才简短回报完成/未完成范围并结束文件任务；一格成功后继续其余目标。无需额外模型轮次清理临时文件，请求文件保留供未知回执恢复；不在本次任务中删除用户文件或审阅数据。
