---
name: bilibili-comment
description: B站评论分析工具。输入B站视频链接或BV号即可获取一级评论数据,支持分页浏览、评论情感分析(积极/负面/需求/竞品),生成精美 HTML 报告。当用户需要查看B站视频评论、分析评论舆情、了解用户反馈时使用。触发词:B站评论、B站视频评论、评论查询、评论分析、评论舆情、看评论、bilibili评论。
dependency:
  python:
    - 无第三方依赖(纯标准库:urllib, json, re, time, argparse, os, sys)
---

# B站评论分析

## 1. 简介

B站评论分析是一款专为内容创作者、UP主、品牌运营和研究人员设计的智能评论洞察工具。输入任意B站视频链接或BV号,即可一键获取评论数据,并通过四维情感分析(积极/负面/需求/竞品)快速了解用户真实反馈,同时生成可离线保存的交互式 HTML 报告。

通过本技能,你可以:
- 📊 逐页获取视频一级评论(每页 20 条,支持翻页)
- 🤖 AI 自动完成四维情感分析,理解B站梗文化
- 📋 生成深色主题交互式 HTML 报告,便于保存与分享

适用于 UP主复盘、品牌舆情监测、竞品分析、内容策略研究等场景。

## 2. 功能特性

### 核心功能

- **评论获取**:粘贴视频链接或 BV 号即可拉取最新评论数据
- **分页浏览**:每页 20 条,支持前后翻页,逐步浏览大量评论
- **四维 AI 分析**:积极/负面/需求/竞品四类情感分析,各维度附代表评论引用
- **置顶标记**:置顶评论特殊标识,一眼识别重要内容
- **HTML 报告**:深色主题交互式报告,支持离线保存与分享

### 特色亮点

- **B站梗文化理解**:识别弹幕术语、缩写(awsl / yyds / xswl / 爷青回 等)及热门梗的真实语境
- **数据完整展示**:作品详情(播放/点赞/投币/收藏/弹幕等)与评论表格全量展示,不截断
- **编码安全回填**:智能编码保障,中文分析内容完整无误地注入报告

## 3. 一键安装

### 鉴权

#### 获取 API Key

请前往 [红狐hub](https://redfox.hk/settings/api-keys?source=minimax) 获取 API KEY。

#### 配置 API Key

方案 1:以 OpenClaw 为例,将 REDFOX_API_KEY 添加到 `~/.openclaw/openclaw.json` 中:

```bash
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }
```

方案 2:终端配置

```bash
export REDFOX_API_KEY="ak_xxxx..."
```

### 依赖安装

本 Skill 使用 Python 3.13+ 纯标准库(urllib、json、re、time、argparse、os、sys),无需安装任何第三方依赖。

### 环境变量配置

| 环境变量 | 说明 | 是否必填 | 获取方式 |
| -------- | ---- | -------- | -------- |
| `REDFOX_API_KEY` | 红狐数据 API Key | 是 | [红狐hub](https://redfox.hk/settings/api-keys?source=minimax) |

## 4. 使用指南

直接用自然语言说出视频链接或 BV 号即可,无需记忆固定命令。

### 常用说法速查

| 意图 | 示例话术 | 效果 |
|------|---------|------|
| 查看视频评论 | 「查看B站视频 BV1xx411c7mD 的评论」 | 获取第 1 页评论 + AI 总结 |
| 通过链接查询 | 粘贴 `https://www.bilibili.com/video/BV1xx411c7mD` | 自动提取 BV 号并拉取评论 |
| 翻页 | 「下一页」「第 3 页」 | 沿用当前视频,获取指定页评论 |
| 生成报告 | 「需要」「生成HTML」 | 回填 AI 分析,生成交互式 HTML 报告 |

### 输出示例

完成查询后,你将依次收到:

1. **作品详情**(标题、UP主、播放量、点赞等核心数据)
2. **评论表格**(当前页全部评论,含昵称链接、内容、点赞数、时间、IP 属地)
3. **四维情感分析**(积极/负面/需求/竞品,各附代表评论)
4. **询问是否生成 HTML 报告**

### 核心执行流程

详细的核心执行流程见 `references/core_workflow.md`,包含以下步骤:

- **Step 1** — 理解用户意图,提取 bvId
- **Step 2** — 调用评论获取脚本(每次只请求一页)
- **Step 3** — 对话中展示评论数据 + AI 总结(A0~A3)
- **Step 4** — 翻页处理
- **Step 5** — 错误处理

> ⚠️ 严格按 `references/core_workflow.md` 执行,可避免编码、翻页、HTML 回填等常见问题。

## 5. 使用场景

| 场景 | 角色 | 示例问法 | 收益 |
|------|------|---------|------|
| 内容复盘 | UP主 | 「看看这个视频的评论怎么样」 | 快速了解观众反馈,优化选题策略 |
| 舆情监测 | 品牌运营 | 「分析这条视频的负面评论」 | 及时发现危机信号,制定应对方案 |
| 竞品分析 | 内容策划 | 「分析竞品视频的用户评论」 | 了解竞品优劣势,找准差异化方向 |
| 用户研究 | 产品经理 | 「看看用户在评论区提了哪些需求」 | 挖掘真实需求,指导产品迭代 |

## 6. 项目架构

### 目录结构

```
bilibili-comment/
├── SKILL.md                          # Skill 定义与使用文档(本文件)
├── references/
│   └── core_workflow.md              # Agent 核心执行流程
├── assets/
│   └── report_template.html          # HTML 报告模板
└── scripts/
    ├── bili_comment_search.py        # 评论获取脚本(调用 API,自动生成 HTML)
    └── backfill_html.py              # AI 分析回填脚本(将分析结果写入 HTML)
```

### 技术栈

| 组件 | 技术 | 说明 |
| ---- | ---- | ---- |
| 运行环境 | Python 3.13+ | 纯标准库,无第三方依赖 |
| 标准库 | urllib, json, re, time, argparse, os, sys | 用于 HTTP 请求、JSON 处理、正则提取、时间控制 |
| 数据接口 | 红狐 API (Redfox) | 通过 REDFOX_API_KEY 鉴权,采用 commentSubmit/commentResult 两步异步接口 |
| 输出格式 | JSON (stdout) + HTML (文件) | JSON 通过 stdout 输出供 AI 解析,HTML 为可视化报告 |

### 核心模块说明

| 模块 | 路径 | 功能 |
| ---- | ---- | ---- |
| 评论获取脚本 | `scripts/bili_comment_search.py` | 调用红狐接口获取 B 站一级评论,支持位置参数(`<bvId>`)和可选参数(`--page`、`--no-html`、`--output-dir`),脚本自动生成含占位符的 HTML 报告 |
| AI 回填脚本 | `scripts/backfill_html.py` | 将 AI 四维分析 JSON 安全回填至 HTML 报告,支持 `--json-file` 文件直读模式,避免管道编码问题 |
| 报告模板 | `assets/report_template.html` | 深色主题交互式报告模板,使用 `{{PLACEHOLDER}}` 占位符 |
| 核心流程 | `references/core_workflow.md` | Agent 端到端执行流程,覆盖意图理解、API 调用、结果展示、翻页、错误处理 |

### 资源索引

- **核心脚本**:`scripts/bili_comment_search.py` — 调用红狐 API 获取评论数据
  - 位置参数:`<bvId>`(BV号或含 BV 号的完整链接)
  - 可选参数:`--page`(页码,默认 1)、`--no-html`(不生成 HTML)、`--output-dir`(HTML 输出目录,默认 `~/Downloads/MiniMaxReports`)
- **回填脚本**:`scripts/backfill_html.py` — 将分析结果回填到 HTML 报告
  - 必填参数:`<html_path>`
  - 数据来源:`--json-file <path>`(推荐) / `--analysis-json '<json>'` / stdin
- **参考文档**:`references/core_workflow.md` — 何时读取:执行查询、翻页、回填 HTML 等任一环节

## 7. 常见问答

### 安装

**Q1: 需要安装哪些依赖?**
A: 本工具使用 Python 3.13+ 纯标准库(urllib、json、re、time、argparse、os、sys),无需安装任何第三方依赖。确保系统已安装 Python 3.13 或更高版本。

**Q2: 如何获取 REDFOX_API_KEY?**
A: 请访问 [红狐hub](https://redfox.hk/settings/api-keys?source=minimax) 注册并申请 API Key,按"一键安装"章节说明配置到本地环境变量。

### 使用

**Q3: 一次能获取多少条评论?**
A: 每次调用获取 1 页(20 条)。如需更多数据,通过翻页命令逐页获取,或前往 [红狐平台](https://redfox.hk?source=minimax) 联系客服获取批量能力。

**Q4: 支持获取二级评论(回复)吗?**
A: 当前版本仅支持一级评论,二级回复暂不支持。

**Q5: AI 四维情感分析的百分比会超过 100% 吗?**
A: 会。四类(积极/负面/需求/竞品)各为独立维度,一条评论可同时属于多个类别,因此总和可能超过 100%。

**Q6: HTML 报告保存在哪里?**
A: 默认输出到 `~/Downloads/MiniMaxReports/` 目录,可通过 `--output-dir` 参数自定义。

### 故障排除

**Q7: HTML 报告中部分中文显示乱码(问号)怎么办?**
A: 这是编码回填环节的兼容性问题。**根本原因**:Write 工具写 JSON 为 GBK 或 PowerShell 管道二次编码损坏。**解决方案**:用 Python `json.dump(ensure_ascii=False)` + `open(f,'w',encoding='utf-8')` 写 JSON,再用 `backfill_html.py --json-file` 直接读文件回填,全程不经过 Write 工具和管道。详见 `references/core_workflow.md` Step 3。

**Q8: 接口返回 502 错误怎么办?**
A: 服务返回 502 错误,可能存在网络不稳定问题。请稍后重试,或检查本地网络环境。

**Q9: 获取 0 条评论怎么办?**
A: 可能原因:(1) 视频本身无评论;(2) 视频已被删除或设置为不可见;(3) BV 号有误。请先核实视频链接或 BV 号是否正确。

**Q10: 评论任务超时怎么办?**
A: 评论数据通过异步任务获取,通常在数秒内返回。如长时间未返回,可重新发起一次查询,或稍后重试。

**Q11: 脚本报错怎么办?**
A: 常见原因:(1) REDFOX_API_KEY 未配置或已过期;(2) Python 版本 < 3.13;(3) 网络问题。请逐一排查。

### 安全许可

**Q12: API Key 如何安全存储?**
A: 推荐使用方案 1(配置到 openclaw.json 的 env 字段中),避免在终端历史中泄露。请勿将 API Key 硬编码在脚本中或上传到公开仓库。

**Q13: 数据来源和版权?**
A: 数据来源于红狐 API 收录的 B 站公开评论。评论版权归原作者所有,本工具仅供学习和内容创作参考使用。
