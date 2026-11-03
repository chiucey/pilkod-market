---
name: english-dictation-paper
description: 生成“英语词汇默写纸/听写纸/默写表”（双栏对照：左栏看英文写中文、右栏看中文回忆英文），并保持固定排版风格（A4、双栏、打钩框、空线）。当需要把单词表渲染成可打印的 HTML，并进一步导出 PDF（便于打印/发给同学）时使用本技能。
---

# 英语默写纸（HTML + PDF）

使用本技能时，优先复用 `assets/template.html` 的版式与 CSS，不要“重新设计”样式；只替换内容（单词与释义），以确保风格始终一致。

## 快速工作流

### 1) 准备词表输入

支持两种：

- **TXT**（推荐）：每行一条，`word<TAB>meaning`（或 `word - meaning`）
- **CSV**：表头必须包含 `word, meaning`

示例 TXT：

- `cue\tn.暗示，提示...`
- `reign - n.君主统治时期...`

### 2) 生成 HTML（可选再导出 PDF）

在技能目录下运行：

- 仅生成 HTML：
  - `python scripts/make_dictation_sheet.py --input words.txt --out-dir ./out --name 英语默写纸`
- 同时生成 PDF：
  - `python scripts/make_dictation_sheet.py --input words.txt --out-dir ./out --name 英语默写纸 --pdf`

输出：
- `./out/英语默写纸.html`
- `./out/英语默写纸.pdf`（当启用 `--pdf`）

## 可调参数（保持风格不变）

仅建议调整这些“文本类”字段；不要改 CSS：

- `--title`：HTML `<title>`
- `--header`：页面大标题（默认“英 语 词 汇 默 写 纸”）
- `--footer`：页脚说明文字
- `--name`：输出文件名（不带扩展名）

## 输出为 PDF 的实现方式

PDF 由 Playwright(Chromium) 的打印引擎生成（A4 + print CSS）。

若在某些环境首次运行报错（缺少浏览器内核），执行一次：

- `python -m playwright install chromium`

## 资源说明

- `assets/template.html`
  - 固定版式模板，包含 CSS 与页面结构。
  - 通过占位符注入内容：`{{LEFT_ROWS}}` / `{{RIGHT_ROWS}}` 等。

- `scripts/make_dictation_sheet.py`
  - 读取词表 → 生成 HTML →（可选）导出 PDF。
  - 请优先复用该脚本，不要在对话里手写长 HTML。