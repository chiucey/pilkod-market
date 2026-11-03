---
name: craft-detective-fiction
description: 创作、续写、改稿和审计以谜案或调查为核心的侦探／推理小说，包括密室、不可能犯罪、程序调查、叙述诡计与系列案件；也用于诊断既有稿件的因果、时间线、线索公平性、连续性、揭晓和风格。不用于现实犯罪策划、规避侦查、普通小说或法律咨询。
---

# 专业侦探小说创作

把客观真相、读者接收信息的顺序和清洁正文分层管理。先闭合真相，再设计误读，最后写场景与句子。

## 核心原则

1. **真相优先。** 在正式长篇正文前闭合真凶、动机、手法、机会、真实时间线、掩饰行为和失败点。
2. **公平但不明显。** 揭晓前提供完成核心推理所需的信息；让误读来自真实事实的多种解释。
3. **精确信息类型。** 分别管理推理线索、普通伏笔、红鲱鱼和纯氛围细节。
4. **单一权威来源。** 每类项目状态只在其所有者文件中更新，其他文件引用它。
5. **真实误导。** 红鲱鱼的观察事实成立，并在后文获得合理解释。
6. **档案与读者稿分离。** 内部档案保存真相、ID、创作笔记和审计结论；清洁正文只保留读者可见内容。
7. **按任务缩放。** 点子、单场景、短篇和诊断只执行产生可靠结果所需的步骤。
8. **逻辑设硬门槛，艺术保留自由。** 伏笔比例、章节间隔、结构百分比和反转数量由作品需要决定。

## 项目状态契约

- `project-charter.md` 管理经用户确认的创作契约与内容边界。
- `case-bible.md` 管理客观真相及 `Q-###` 终局结论 ID。
- `outline.md` 管理叙事计划与读者信息顺序。
- `mystery-ledger.md` 管理 `C-###` 线索、`F-###` 伏笔和 `R-###` 红鲱鱼的生命周期。
- `style-guide.md` 管理语言约束与用户确认的原创风格锚点。
- `notes.md` 管理临时检查点、开放问题、研究记录、连续性待办和大纲偏差；它不覆盖权威档案。
- `audit-report.md` 保存最近一次正式审计快照；历史变更保留在各权威档案的变更记录中。

结构性修改先更新 `case-bible.md`，再依次回归检查登记簿、大纲和受影响章节。章节正文只在相关权威状态同步后继续扩写。

## 任务路由

- **点子、梗概或单场景**：直接交付成果，在内部完成最小真相与连续性检查；用户要求保存时再建档。
- **从零创作中长篇**：先完成最小访谈，再按长期项目工作流建档。
- **续写已有项目**：先映射现有大纲、设定、正文和笔记，再恢复缺失的真相、ID 与检查点。
- **诊断或改稿**：先只读列出问题、证据、严重性和修订顺序；用户明确要求修改后再改写。
- **立即开写**：最多询问 3 个真正阻塞的问题，其余采用明确标注的临时假设并先交付可确认方案或样章。

## 安全与原创门槛

- 危险现实细节只表达为不可执行的条件、痕迹、后果和失败点。涉及现实犯罪、伤害、自伤、毒理、武器、安防或执法规避时，立即读取 [research-protocol.md](references/research-protocol.md)，把可复制的参数和步骤转为高层情节、虚构规则或失败机制。
- frontmatter 的排除项是能力边界，不是跳过安全处理的理由；若请求同时包含推理创作与危险能力，只执行安全拒绝和不可执行转译。
- 保留用户的戏剧目标，同时让现实方法不可直接执行；不得优化伤害、目标选择、隐匿尸体、逃避执法或安防绕过。
- 把参考作者或作品转译为视角、节奏、意象和叙事距离等高层特征，产出原创文本；版权与敏感内容按研究协议处理。

## 按需读取资源

所有资源均从本文件一层直达，只读取当前任务需要的部分：

- 创建、恢复或持续维护中长篇项目时，读取 [longform-workflow.md](references/longform-workflow.md)。
- 收集需求或选择类型、结构时，读取 [intake-and-structures.md](references/intake-and-structures.md)。
- 设计真相、嫌疑人、时间线、线索、误导或叙述诡计时，读取 [mystery-engineering.md](references/mystery-engineering.md)。
- 定调、写样章、逐场景写作或做文风修订时，读取 [style-and-scene.md](references/style-and-scene.md)。
- 批准大纲、阶段复盘、揭晓前检查或完稿验收时，读取 [audit-rubric.md](references/audit-rubric.md)。

## 模板与脚本

长期项目使用以下模板资产：

- [project-charter-template.md](assets/project-charter-template.md)
- [case-bible-template.md](assets/case-bible-template.md)
- [outline-template.md](assets/outline-template.md)
- [mystery-ledger-template.md](assets/mystery-ledger-template.md)
- [style-guide-template.md](assets/style-guide-template.md)
- [chapter-template.md](assets/chapter-template.md)
- [notes-template.md](assets/notes-template.md)
- [audit-report-template.md](assets/audit-report-template.md)

探测并使用当前环境可用的 Python 解释器，记作 `<python>`；主文件不假定固定命令名。

- [init_project.py](scripts/init_project.py)：仅在新建的空项目目录中从模板初始化；已有项目先映射现有文件。
- [audit_mystery_project.py](scripts/audit_mystery_project.py)：执行必要文件、模板残留、ID 引用和状态完整性检查；结果是结构证据，人工审计负责重建推理。
- [build_clean_export.py](scripts/build_clean_export.py)：合并章节并移除约定的内部容器；生成后再次执行结构检查并人工确认无剧透档案、内部 ID 或未完成占位符。
- [run_tests.py](tests/run_tests.py)：脚本回归测试，覆盖 frontmatter 解析、canonical 门槛、审计与清洁导出；修改 `scripts/` 后运行，全部通过再交付。

## 质量门槛

出现以下任一硬失败时，暂停扩写并先修结构：

- 核心结论依赖揭晓时才出现的信息。
- 时间、距离、物理条件或人物能力使手法不成立。
- 真凶缺少动机、手段或机会之一。
- 侦探使用读者和当前 POV 无法获得的信息。
- 红鲱鱼建立在无可靠叙述机制的假事实上。
- 结构修改造成权威档案、登记簿、大纲和正文版本不一致。
- 危险现实细节达到可复制、可优化或可规避侦查的程度。

章末完成条件：本章 `ledger_actions` 已与登记簿实际位置和状态核销，连续性与偏差检查点已写入 `notes.md`，且不存在未处理的硬失败。

清洁导出完成条件：导出后结构检查无错误，人工检查确认章节顺序正确且不含 YAML、内部注释、内部 ID、占位符或完整谜底档案。

线索过显、节奏偏慢或嫌疑人存在感不足等软性问题记为警告，在最近复盘点处理，不阻塞当前可靠产出。

## 协作方式

- 只询问会实质改变结果的选择；其余给出推荐方案并记录假设。
- 每次交付先给用户可读成果，再简要列出需要确认的关键决策。
- 正文交付聚焦清洁文本；阶段状态、经典作品分析和内部编号留在工作档案。
- 用户要求查看真相档案时再展示完整谜底，并先给出剧透提醒。
- 用户希望加速时缩短流程并保留硬门槛，持续推进到当前交付完成。
