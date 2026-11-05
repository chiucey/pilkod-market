# 各阶段共享的交付契约

记录服务于实际开发；已有项目复用现有文档位置，微小修复不要求生成全部文件。新项目可使用 scripts/init_workspace.py 创建空记录，并填写真实信息。

## 最小记录

| 材料 | 核心字段 | 使用者 |
|---|---|---|
| scope.md | 用户目标、包含/排除、当前基线、锁定项、验收路径 | 全部阶段 |
| rules.md | 生效文件、作用范围、约束、落实与检查 | 所有实施技能 |
| design-state.json | 页面、方向、候选、确认来源、版本与场景 | 原型/交接/前端 |
| api-contract.md | endpoint、auth、输入输出、错误、owner、幂等/并发 | 前后端 |
| component-map.md | 旧实现、共享组件、语义状态、调用方、复用检查 | 原型/原生 |
| evidence.json | 环境、构建、步骤、预期、实际、证据、结果 | 联调/交付 |

设计状态与验证状态不同。页面选中后仍可能未验证；浏览器收藏不能自动升级为用户确认。记录路径尽量相对于项目，发布通用插件时不得带作者机器路径或用户数据。

## 证据条目

每条 evidence 记录 id、layer、status、environment、steps、expected、actual、artifacts。layer 可为 static/browser/simulator/device/live-service/user-acceptance/publication；status 为 passed/failed/blocked/not-run。passed 必须包含实际结果和可追溯产物，不能用“待补截图”填充。

UI 截图支持外观判断，不证明真实 API；HTTP 成功不证明持久化或用户归属；模拟器不能验证实体相机；运行旧包不证明新代码；上传商店不证明审核通过。跨层结论逐项核对。

## 可体验交付

说明当前运行位置、账号或模式、从哪里开始、如何操作、预期结果与复核方式。提供必要版本和截图/日志链接；已知失败保留。若 user acceptance 未发生，准确标注；若发布被权限阻止，提供已完成包/MR和具体所需权限，不把待处理说成已发布。

提交/推送/MR/合并/部署根据当前授权分别执行；用户已要求测试发布则继续对应测试路径，不能自动追加生产。生产与测试使用独立基线与版本记录。
