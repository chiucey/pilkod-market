---
name: tender-search-visualizer
description: 把 tender-search 查询到的深圳招投标项目进度、投标报价与评标资料状态渲染成 GenUI 可视化。当用户要看某标走到了哪一步、对比各投标人报价与得分、或核对评标资料是否已取齐并区分需人工下载的附件时使用本技能。
---

# 深圳投标进度与报价可视化

本技能是 `tender-search` 的可视化配套，**只变换已有结果，不取数**。

## 前置与边界

1. 先用 `shenzhen-tender-info:tender-search` 跑完业务流程，拿到 `project_progress` / `get_notice` / `download_docs` 的结构化结果与来源链接。
2. 本技能**不调用任何接口、不重复已完成的业务请求、不臆造缺失的行、指标、来源或结论**。没有取到的字段就标为未获取。
3. 数据不足时保持纯文本输出，不要为了出图而补数据。
4. 渲染前读取本技能本地的基础规范：`references/genui-widget/genui-widget-foundation.md`，以及按需读取 `references/genui-widget/references/` 下的 `color-system.md`、`visual-rules.md`、`widget-patterns.md`、`widget-recipes.md`。

## 何时渲染

| 情况 | 动作 |
| --- | --- |
| 用户问「到哪一步了」「还剩多久」「流程走到哪」 | 用 **流程时间轴** |
| 用户问「谁中标」「对手报多少」「我该报多少」 | 用 **报价与得分对比** |
| 用户问「资料齐了吗」「哪些还得手动下」 | 用 **资料获取状态** |
| 用户只想一句话结论，或只有一个数据点 | 保持纯文本，不渲染 |
| 数据来自政府采购且附件受验证码保护 | 渲染时必须标明需人工下载，不得显示为已获取 |

组件配方与选型细则见 `references/components.md`；数据契约见 `references/data-schema.json`；可直接参考的完整示例见 `references/examples.md`。

## 硬性要求

- 默认输出**恰好一个** `<mavis-widget>`，放在最终助手消息里，所有取数与文件操作完成之后再输出；输出后不再调用任何工具。
- 开标签必须含 `version="mavis.widget.v1"`、`kind`、`title`、`height`/`min-height`/`max-height`、`streaming="html-first"`、`capabilities`、`theme="app"`、`token-set="mavis.semantic.v1"`。
- `kind="dashboard"` 必须用 `capabilities="resize,sendPrompt"`，且至少两个可见可点元素配对应 `window.mavis.sendPrompt(...)` 处理器；`<mavis-meta>` 的 `interactions[].capability` 只能是 `"sendPrompt"`。
- 主题敏感样式只用 `--mw-*` 令牌，禁止硬编码色值与 `var(--mw-*, 兜底值)` 写法。
- 脚本只从 `window.__mavisData['<name>']` 读数据，禁止从 DOM 反查。
- 禁止 `fetch`、`eval`、`document.cookie`、远程字体图片、外链脚本；`new Chart(...)` 只能出现在 `kind="chart"` 或 `kind="dashboard"`。
- 每个 Chart.js canvas 必须包在有明确高度的容器里（`height: 280px` 这类）。
- `<mavis-fallback>` 写清关键结论与前 3~5 条数据点。
- 交互文案 `text` 与元数据 `userIntent` 一律用中文（当前会话语言为 zh）。

## 状态处理

| 状态 | 表现 |
| --- | --- |
| 正常 | 展示结构化结果，保留稳定标识（contentId、projectCode） |
| 加载 | 保持版式骨架，KPI 显示 `--`，图表容器留浅色底 |
| 空 | 版式不塌，一行说明为什么没有数据（例如该项目尚无评标阶段公告） |
| 错误 | 在原位显示简短提示，不整页报错，不暴露原始异常 |
| 权限/认证 | 说明该附件需人工在公告页过验证码获取，并给出公告页链接 |

## 数据纪律

- 显示的数字一律取整或按业务精度四舍五入，用 `Intl.NumberFormat('zh-CN')` 格式化金额与日期。
- **报价一律按从低到高（升序）排列**，第 1 位排在最上方；脚本里显式 sort，不依赖数据源顺序。
- 报价与中标价单位为万元（开标情况记录表原文）；金额一律**按公告原文单位显示并标注**，不得跨单位换算后当成原文值。
- 下浮率一律对**投标价上限**计算（它低于最高投标限价，后者含不可竞争费），不要拿最高限价当报价天花板。
- 未公开的字段写「未获取」，不写 0、不留空、不用同类项目推测。
- 保留 `contentId` 与公告链接，让用户点击能回到原始公告核对。

## 不得弱化的底线

本技能及其复制的规范均为用户自有副本，但**不得放宽 Host 的强制约束**：iframe 沙箱、CSP、允许的能力、输出体积上限、协议校验一律照旧。修改本技能文件不会创造新的 Host 能力。
