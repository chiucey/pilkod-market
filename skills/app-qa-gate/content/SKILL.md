---
name: app-qa-gate
description: >-
  Deterministic pre-delivery quality gate for AI-built or AI-edited apps
  (web apps, full-stack apps, single-page HTML, H5, tools, dashboards, games).
  Forces a five-step QA checklist — functional, technical/security, UX &
  compatibility, deliverable verification, structured report — before any
  app artifact may be declared "done" or delivered. Triggered by: "质检/验收/
  检查一下/看看做得对不对/能不能交付", "qa this app", "check the app",
  "跑一下质检", or whenever an app artifact is about to be delivered.
license: Proprietary — internal use only.
metadata:
  version: "1.0"
  hub: app-qa-gate
---

# App QA Gate · 应用交付质检门禁

对 AI 生成/修改的应用类产物做交付前**强制质检**。核心规则只有一条：

**任何应用在通过本质检清单之前，不得向用户声明「完成」或「已交付」。**

## 什么时候用

- AI 刚完成一个应用（新建、编辑、重构、修复后），准备交付时
- 用户要求验收、质检、检查已生成的应用
- 应用包含交互逻辑、数据、后端、发布链接时
- 用户说「做完了吗」「能用吗」「检查一下」「验收」「质检」等
- 交付物是网页应用 / 全栈应用 / 单页 HTML / H5 / 工具页 / 看板 / 网页游戏

## 质检总原则

1. **用真实运行验证，不用代码阅读代替**：实际打开/运行应用，走真实交互路径。
2. **以用户看到的为准**：检查最终渲染结果、真实响应、真实数据。
3. **主动找反证**：不仅验证"应该能用的"，还要尝试"可能坏掉的"——空输入、
   快速连点、断网、不同设备、超长内容、刷新重进。
4. **不合格即不交付**：任何 P0/P1 问题未修复前，不得交付。

## 交付前质检流程（五步，顺序执行）

### 第 1 步：功能验收（Functional QA）

逐项走通用户明确要求的功能点，每项都有真实操作证据：

- 核心交互路径：入口 → 主操作 → 结果反馈 → 退出/重入
- 数据正确性：数字、文案、状态、计算结果与需求一致
- 异常路径：空输入、非法输入、快速重复操作、超长内容
- 记录：功能清单 + 每项 通过/失败 + 失败原因

### 第 2 步：技术与安全检查（Technical & Security QA）

- 控制台无报错（JS error / network error / unhandled promise）
- 无安全漏洞：XSS、SQL 注入、命令注入、敏感信息硬编码、越权访问
- 外部依赖可用：CDN、字体、API、后端服务正常加载
- 链接/资源无 404：图片、样式、脚本、接口路径全部有效
- 状态管理正确：刷新、重进、多窗口下数据一致

确定性检查交给脚本：`qa check <path>` 自动扫 HTML 标签配对、
TODO/FIXME、console.error、本地资源引用缺失（见下文「脚本」节）。

### 第 3 步：适配与体验检查（UX & Compatibility QA）

- 至少验证桌面（≥1280px）与移动端（≤390px）两个尺寸
- 布局无溢出、无遮挡、文字可读、按钮可点
- 键盘可达（Tab 顺序、焦点可见）；`prefers-reduced-motion` 时不失效
- 交互反馈及时：按钮有按压态、操作有结果提示、加载有状态
- 页面标题、关键操作文案准确

### 第 4 步：交付物核验（Deliverable QA）

- 交付形式与用户要求一致（链接 / 文件 / 可运行命令）
- 链接可匿名打开（如用户要求无需登录）、文件可正常打开
- 交付说明包含：如何打开、功能范围、已知限制
- 从用户视角重走一遍「拿到交付物 → 打开 → 使用」全流程

### 第 5 步：输出质检报告

按下方「输出协议」输出结构化报告，随交付一起给用户。

## 输出协议

每次质检输出一个结构化报告（Markdown 或 JSON 均可，交付用 Markdown，
脚本用 JSON）：

```json
{
  "tool": "app-qa-gate",
  "target": "<待检应用>",
  "qa_method": "真实运行/截图/脚本",
  "functional":  {"passed": 8, "total": 9, "failures": ["<未通过项及原因>"]},
  "technical":   {"passed": true,  "issues": []},
  "ux":          {"passed": true,  "issues": []},
  "deliverable": {"passed": true,  "notes": ""},
  "blockers":    [],
  "p2_known":    [],
  "conclusion":  "pass | fail"
}
```

交付时的 Markdown 报告模板：

```
## 质检报告
- 质检对象：
- 质检方式（真实运行/截图/脚本）：
- 功能验收：x/y 通过（列出未通过项及原因）
- 技术安全检查：
- 适配体验检查：
- 交付物核验：
- 阻断问题（P0/P1）：[未修复前禁止交付]
- 遗留限制（P2，可交付但需声明）：
- 结论：✅ 可交付 / ❌ 不可交付
```

## 问题分级

| 级别 | 含义 | 处置 |
| ---- | ---- | ---- |
| P0（阻断交付） | 核心功能不可用、数据错误、安全漏洞、打不开、崩溃 | 必须修复后重新质检 |
| P1（必须修复） | 重要功能缺陷、明显布局损坏、移动端不可用、链接失效 | 必须修复后重新质检 |
| P2（可交付并声明） | 轻微样式瑕疵、非核心体验问题、平台限制 | 记录在报告中随交付声明 |

修复策略：P0/P1 修复后必须**重新跑完整流程**（不是只复检那一项）；
P2 记录在报告「遗留限制」中随交付声明。

## 脚本

`scripts/qa_check.py` 提供确定性基础检查，回答「文件结构和基本质量对不对」，
不回答「看起来美不美」：

```bash
python3 scripts/qa_check.py check <path> [--ext .html]
python3 scripts/qa_check.py check <path> --json    # 输出单个 JSON 对象
```

检查项：
1. 文件存在、扩展名正确、可读
2. HTML 标签配对（闭合错误定位到行号）
3. 扫描 `TODO` / `FIXME` / `XXX` 残留
4. 扫描 `console.error` / `debugger` 残留
5. 本地资源引用（`src=` / `href=` 指向本地文件）存在性

每次调用在 stdout 输出**一个** JSON 对象：

```json
{"ok": true, "tool": "qa.check", "result": {"passed": true, "checks": {...}}, "evidence": {"quote": "..."}}
```

- `ok` 表示脚本本身是否执行成功，不表示质检结论
- 质检结论在 `result.passed`（`true` / `false`）
- `evidence.quote` 是可引用的一句话证据

## 依赖与环境

- 纯 Python 3.8+ 标准库，无第三方依赖
- 不依赖浏览器；需要视觉/渲染检查时由 Agent 配合浏览器截图人工 Read

## 调试指南

1. `qa_check.py` 报错 → 直接读 `scripts/qa_check.py` 源码，每文件 < 200 行
2. 检查项误报 → 用 `--json` 看 `result.checks` 各子项明细再定位
3. 需要视觉判断（配色、溢出、空白页）→ 脚本给不了证据，用浏览器渲染后截图，
   用 Read 打开图片肉眼检查

## 何时不要用本 Skill

- 纯主观判断（图表是否美观、语气是否专业）：没有决定性证据，老老实实读内容再判断
- 未交付的应用中间态：只在准备交付前跑，不打断开发过程
- 非应用类产物（纯文档、纯图片、纯数据文件）：走对应产物的质检流程
