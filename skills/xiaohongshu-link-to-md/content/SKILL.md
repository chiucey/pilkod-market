---
name: xiaohongshu-link-to-md
description: >
  小红书笔记转 Markdown 知识库归档。Use when user provides a Xiaohongshu (小红书/xiaohongshu) URL
  and wants to 整理/沉淀/归档/转存/保存 it, or needs to convert xiaohongshu notes to structured .md
  files with local image caching. Supports 4 image modes (link/embed/url/none).
license: MIT
compatibility: Python>=3.9, requests, network access required, xhs library (optional)
metadata:
  author: Reyes957
  version: "2.1.0"
  triggers:
    required: [小红书, xhs, xhs链接, xiaohongshu]
    optional: [整理, 转md, 转markdown, 沉淀, 归档, 保存, 下载图片, 转存, archive, convert, save]
allowed-tools: Bash(python scripts/*:*) Read Write
---

# Skill: xiaohongshu-link-to-md

## 一句话定位

**用户甩进来一个小红书链接，自动产出一份结构化 Markdown 文档 + 一份本地媒体缓存。**

输入：一条小红书笔记 URL
输出：
- 一份结构化 .md 文档（保存到 `./xiaohongshu-notes/`）
- 一份媒体缓存（保存到 `./.cache/xiaohongshu-link-to-md/{noteId}/`），含原图

## 适用场景

- 看到一条爆款笔记（求职方法论 / AI 教程 / 行业研究 / 理财干货），想沉淀到知识库
- 看了视频笔记，想把口播/板书/演示转成可检索的文本
- 想图也下载到本地（避免 CDN Referer 校验失败 / 链接腐烂）
- 不想手动复制，想批量归档某个作者或某类主题

## 与 `xiaohongshu-collector` 的关系

**互补串联，不要混用。**

| 技能 | 触发方式 | 输入 | 输出 |
|------|---------|------|------|
| `xiaohongshu-collector` | 用户给关键词 | "AI 产品经理求职" | 找 5-10 篇相关笔记 + 采集报告 |
| `xiaohongshu-link-to-md`（本技能） | 用户给单条链接 | "https://xhslink.com/xxx" | 一篇笔记的完整 Markdown + 媒体缓存 |

**典型工作流**：
```
xiaohongshu-collector 找内容 → 拿到一批链接 → 逐条丢给 xiaohongshu-link-to-md → 沉淀为知识库
```

## 核心原则

1. **只处理给定链接**：不主动搜索、不弹确认框、不问"要不要看相关推荐"
2. **原文优先**：金句/段落/评论原文保留，不擅改
3. **图片本地化**：默认下载到本地缓存 + md 用相对路径引用，用户可选择不要图
4. **可二次编辑**：标准 Markdown，无 Notion/Obsidian 专属语法
5. **失败兜底**：抓不到就降级，绝不抛一堆错给用户

## 处理流程

严格按以下步骤执行，不要跳过 Step 4（验证）。

### Step 1: 解析链接

```bash
python scripts/xiaohongshu_common.py --parse-url "<URL>"
```

支持两种格式：
- 短链：`https://xhslink.com/o/xxx`
- 长链：`https://www.xiaohongshu.com/explore/{noteId}`

提取 `noteId`（24 位 hex），供后续调用。

### Step 2: 抓取笔记

```bash
python scripts/fetch_note.py <note_id> --mode auto
```

抓取决策（脚本内部自动完成）：

```
[L1: HTML] ← 不需要 cookie → 标题、正文、作者、图片列表、视频 masterUrl
    ↓ 失败
[L2: API]  ← 需要 cookie   → 上述全部 + 完整评论
    ↓ 失败
[L3: 降级] → 生成"抓取失败"卡片
```

### Step 3: 下载媒体

```bash
python scripts/download_media.py <note_id> --image-mode link
```

4 种 image-mode：

| 模式 | md 中图片处理 | 适用场景 |
|------|-------------|----------|
| `link`（默认） | 相对路径引用本地文件 | 长期归档、知识库 |
| `embed` | base64 内嵌 | 单文件可移植分享 |
| `url` | 保留原始 CDN URL，不下载 | 临时存档 |
| `none` | 不放图，仅文字描述 | 纯文字阅读 |

### Step 4: 渲染 Markdown

```bash
python scripts/xiaohongshu_to_md.py "<URL>" --image-mode link --output-dir ./xiaohongshu-notes/
```

脚本内部自动完成：模板选择（full/mini）、占位符替换、标签去重、金句提取、媒体清单生成。

### Step 5: 验证输出 ⭐

```bash
python scripts/validate_output.py ./xiaohongshu-notes/<output_file>.md
```

验证项：
- 文件存在且非空
- 无残留未替换占位符（`{{xxx}}`）
- 本地图片引用路径实际存在（link/embed 模式下）
- Markdown 基本语法有效

> 验证失败时，阅读错误信息，修复后重新执行 Step 5。只有验证通过才能继续。

### Step 6: 报告结果

告知用户：
1. 输出的 .md 文件路径
2. 媒体缓存位置（`.cache/xiaohongshu-link-to-md/{noteId}/`）
3. 使用的 image-mode 和模板类型
4. 如果用户不满意图片方式，可重新跑 `--image-mode none/url`

## 输出结构

9 个模块，根据内容丰富度自适应：

| 模块 | 必出 | 何时可省 |
|------|------|---------|
| 标题区 | ✅ | — |
| 🏷️ 标签矩阵 | ✅ | — |
| 📌 核心摘要 | ✅ | — |
| 📝 内容重构 | ✅ | — |
| 💬 高赞评论精选 | ✅ | 评论抓不到时留"未抓取"占位 |
| 🏷️ 我的备注 | ✅ | 留空模板也行 |
| 📜 原文附录 | ✅ | 笔记极短（< 50 字）时可省 |
| 📷 媒体清单 | ✅ | 无图片/视频时显示"本笔记无图片" |
| 📎 原文信息卡 | ✅ | — |

## 标签体系

三类标签，**严格去重**（同义/大小写变体只在一处出现）：

| 类型 | 数量 | 用途 |
|------|------|------|
| 主词（核心流量） | ≤5 | 概括内容最核心的关键词 |
| 长尾词（蓝海搜索） | ≤10 | 覆盖小众但精准的搜索场景 |
| 原文标签 | ≤3 | 原笔记 hashtag 独有部分 |

去重规则：同一关键词只出现在最合适的那一类，重复时优先保留在主词。

## Gotchas

### 抓取

- **HTML(L1) 不需要 cookie 但拿不到评论**；API(L2) 需要有效 cookie（平均 7-30 天过期）
- cookie 过期后 API 路径会直接失败，检查 `XIAOHONGSHU_COOKIE` 环境变量或 `~/.config/xiaohongshu-link-to-md/cookie`
- 同一 IP 短时间内频繁抓取会触发 461 / 429 限流，每次请求间隔 ≥1.5s
- **短链（xhslink.com）需要先 follow 302 跳转**才能拿到 noteId，脚本已内置处理
- HTML 路径走移动端 UA，API 路径走 X-s 签名

### 图片

- **xhscdn CDN 直链必须带 `Referer: https://www.xiaohongshu.com/`**，否则 403（脚本已内置）
- 图片下载失败时自动 fallback 到原始 CDN URL——下次打开 md 可能 403
- `--image-mode link` 是默认，md 用相对路径引用 .cache 中的图片——迁移目录时需修复图片路径

### 模板选择

- 自动规则：视频笔记 → `full`，图片 >6 张 → `full`，正文 >1000 字 → `full`，其余 → `mini`
- 完全抓取失败时输出文件名带 `-FAILED-` 前缀
- 所有输出为标准 Markdown，无平台专属语法

### 安全

- cookie 不得硬编码到脚本中，只用环境变量或 `~/.config/` 文件
- 抓取内容仅用于个人知识沉淀，不做二次分发
- 不要并发抓取（必触发 461）

### Playwright L4 兜底（v2.1 新增）

- L1/L2/L3 全部失败后自动尝试 Playwright 浏览器渲染
- 需要安装可选依赖：`pip install playwright playwright-stealth && playwright install chromium`
- 使用移动端 UA + stealth 反检测补丁 + 人类行为延迟模拟
- 未安装时静默跳过，不影响现有流程
- 输出格式与 L1/L2 完全一致，通过 `fetch_note_pw.py` 独立模块实现

## 相关文件

- `scripts/fetch_note.py` — 主抓取脚本（L1/L2/L3 降级 + diagnostics）
- `scripts/xiaohongshu_common.py` — 公共工具（cookie、链接解析、标签去重、金句提取）
- `scripts/xiaohongshu_to_md.py` — 一键集成脚本（URL → .md + 媒体下载 + L4 兜底）
- `scripts/download_media.py` — 媒体下载（视频/图片 + 重试 + Referer 校验）
- `scripts/fetch_note_pw.py` — Playwright L4 浏览器兜底（v2.1 新增，可选）
- `scripts/validate_output.py` — 输出验证（占位符/图片路径/语法检查）
- `scripts/test_e2e.py` — 端到端回归测试（10 个场景）
- `templates/full.md` — 完整版输出模板（9 模块）
- `templates/mini.md` — 迷你版输出模板（7 模块）
- `examples/` — 三个示例（图文 / 视频 / 失效）
- `reference/setup.md` — 环境配置详解（Python 依赖 / cookie 注入 / 可选组件）
- `reference/faq.md` — 常见问题详细解答
- `reference/anti-bot.md` — 反爬应对备忘
