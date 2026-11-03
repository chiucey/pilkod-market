---
name: digital-economy-digest
description: |
  数字经济资讯编排调度顶层技能。自动编排底层操作技能（搜索采集、格式导出、多渠道分发）
  和上层能力技能（趋势研判、政策评估、选品决策、风险预警），形成完整的数字经济资讯工作流。
  触发词：数字经济日报、数字经济周报、数字经济资讯、生成数字经济报告、
  搜索数字经济新闻、整理数字经济动态、发送数字经济日报、定时生成周报、
  数字经济简报、数字经济播报、数字经济早报、数字经济晚报、
  数字经济分析、趋势研判、选品决策、风险预警、
  digital economy digest、digital economy report
icon: 📊
category: productivity
tags:
  - 数字经济
  - 资讯
  - 日报
  - 周报
  - 报告生成
  - 政策分析
  - 行业研究
  - 数据要素
  - AI监管
  - 编排调度
author: WorkBuddy
version: "4.0"
language: zh-CN
release_notes: |
  v4.0 - 层次化技能架构：拆分为3个底层操作技能+1个上层能力技能+1个顶层编排技能，
         合并 publish_report.py 到 send_email.py，邮件套用 HTML 模板
  v3.0 - 代码重构消除重复、搜索词扩充至60+、HTML转换优化、文档整合
  v2.0 - 新增飞书发布支持、全网搜索关键词扩充、质量检查清单强化
  v1.0 - 初始版本，支持日报/周报生成及邮件/企业微信/钉钉分发
supported_platforms:
  - windows
  - macos
  - linux
---

# 数字经济资讯编排调度技能（顶层）

## 层次化技能架构

本技能采用**三层架构**设计，可独立运行也可调用子技能：

```
┌─────────────────────────────────────────────┐
│   顶层编排：digital-economy-digest          │
│   （编排调度 · 完整工作流）                    │
├──────────────────────┬──────────────────────┤
│  上层能力             │  上层能力             │
│  digital-economy-    │  （可扩展更多          │
│  analysis            │   业务能力技能）       │
│  （趋势/选品/风险）   │                       │
├────────┬────────┬────┴──────────────────────┤
│ 底层操作│ 底层操作│ 底层操作                    │
│ search │ export │ distribute                  │
│（搜索） │（导出） │（分发）                     │
└────────┴────────┴────────────────────────────┘
```

### 子技能清单

| 技能名 | 层次 | 职责 | 可独立使用 |
|--------|------|------|-----------|
| `digital-economy-search` | 底层操作 | 搜索采集数字经济资讯（60+关键词） | ✅ |
| `digital-economy-export` | 底层操作 | 导出 Word/Excel/HTML | ✅ |
| `digital-economy-distribute` | 底层操作 | 邮件/企业微信/钉钉/飞书分发 | ✅ |
| `digital-economy-analysis` | 上层能力 | 趋势研判/政策评估/选品决策/风险预警 | ✅ |
| `digital-economy-digest` | 顶层编排 | 完整工作流编排 | ✅ |

---

## 功能概览

| 功能 | 说明 | 调用技能 |
|------|------|----------|
| 📰 资讯搜索 | 自动搜索政策、行业、国际三大类（60+ 搜索词） | `digital-economy-search` |
| 📝 日报/周报 | 按"摘要+核心影响"固定格式生成结构化报告 | 本技能编排 |
| 📄 多格式导出 | Markdown / Word / Excel / HTML | `digital-economy-export` |
| 📧 多渠道分发 | 邮件 / 企业微信 / 钉钉 / 飞书 | `digital-economy-distribute` |
| 🧠 智能分析 | 趋势研判/政策评估/选品决策/风险预警 | `digital-economy-analysis` |
| ⏰ 定时自动化 | 每日/每周自动运行 | WorkBuddy automation |

---

## 完整工作流（8 步）

### Step 1 — 确认报告类型与需求

主动询问或根据用户指令推断：

| 问题 | 默认值 |
|------|--------|
| 日报还是周报？ | 日报（最近 24 小时） |
| 输出格式？ | Markdown（.md） |
| 是否导出 Word/Excel？ | 否（除非用户要求） |
| 是否需要智能分析？ | 否（除非用户要求） |
| 是否发送邮件/IM？ | 否（除非用户要求） |
| 是否定时自动运行？ | 否（除非用户要求） |

### Step 2 — 搜索采集（调用 `digital-economy-search`）

```bash
python scripts/search_digest.py --mode daily --dump-queries
```

脚本输出 JSON 列表，每个元素含 `category`、`query`、`since` 三个字段。
搜索词已自动追加当前年份，确保时效性。

### Step 3 — 执行全网搜索

使用 `web_search` 工具逐一执行 Step 2 输出的每个 query：

- 仅保留 `since` 日期之后发布的文章
- 每条结果收集：`title`、`url`、`source`、`date`、`snippet`、`category`
- 按 URL 去重，同一事件保留信息量最大的摘要
- 每个分类目标 **5~10 条高质量内容**，跳过重复和低质量来源

**优先级来源：**
- 政府官网：gov.cn、miit.gov.cn、ndrc.gov.cn、mofcom.gov.cn、nationaldatabureau.gov.cn
- 权威媒体：xinhua.net、people.com.cn、21jingji.com、caixin.com、36kr.com
- 研究机构：ccidnet.com、caict.ac.cn、iresearch.cn

### Step 4 — 阅读格式规范

读取 `references/report_format.md`，严格遵守：
- 报告固定结构（一、政策动态 / 二、行业动态 / 三、国际视野）
- 单条资讯模板（摘要 ≤120 字 + 🔴直接影响 + 🟡潜在影响）
- 分类判断标准

### Step 5 — 生成 Markdown 报告

按 `references/report_format.md` 的模板填充 Step 3 收集的每条资讯。

报告文件名规范：
- 日报：`digital-economy-daily-YYYYMMDD.md`
- 周报：`digital-economy-weekly-YYYYMMDD.md`

### Step 6 — 智能分析（可选，调用 `digital-economy-analysis`）

若用户需要深度分析，调用上层能力技能：

```bash
python digital-economy-analysis/scripts/trend_analyzer.py \
  --input items.json --analysis comprehensive
```

分析结果可作为报告附录，或单独生成分析报告。

### Step 7 — 导出其他格式（可选，调用 `digital-economy-export`）

```bash
# Word 导出
python scripts/export_report.py --input <report.md> --format docx

# Excel 导出
python scripts/export_report.py --input <report.md> --format xlsx

# HTML 导出（自动使用 assets/email_template.html）
python scripts/export_report.py --input <report.md> --format html
```

### Step 8 — 多渠道分发（可选，调用 `digital-economy-distribute`）

```bash
# 邮件发送（自动套用 HTML 模板）
python scripts/send_email.py --report <report.md> --to "收件人@example.com" \
  --subject "数字经济日报 YYYY-MM-DD"

# 企业微信 Webhook
python scripts/send_email.py --report <report.md> --channel wecom \
  --webhook "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

# 钉钉 Webhook
python scripts/send_email.py --report <report.md> --channel dingtalk \
  --webhook "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"

# 飞书 Webhook
python scripts/send_email.py --report <report.md> --channel feishu \
  --webhook "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK"

# 飞书交互卡片
python scripts/send_email.py --report <report.md> --channel feishu \
  --webhook "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK" --card
```

> ⚠️ 发送外部消息前必须征得用户确认，不得在未经用户同意的情况下自动发送。

---

## 定时自动化

使用 `automation_update` 工具创建定时任务：

| 场景 | rrule 参数 |
|------|-----------|
| 每天早 8 点日报 | `FREQ=DAILY;BYHOUR=8;BYMINUTE=0` |
| 每周一早 8 点周报 | `FREQ=WEEKLY;BYDAY=MO;BYHOUR=8;BYMINUTE=0` |
| 每个交易日下午 5 点 | `FREQ=DAILY;BYHOUR=17;BYMINUTE=0` |

---

## 质量检查清单

每次交付前逐项核对：

- [ ] 每条资讯均有摘要（2~4 句，≤120 字，客观第三人称）
- [ ] 每条资讯均有 🔴 直接影响 + 🟡 潜在影响
- [ ] 来源和时间已填写，不留"未知"
- [ ] 链接为原文直链，非聚合页
- [ ] 分类正确：政策动态 / 行业动态 / 国际视野不混淆
- [ ] 报告标题日期与生成时间一致
- [ ] 导出的 Word/Excel/HTML 文件可正常打开

---

## 注意事项

- 若某分类搜索结果为空，标注 `_（本周期暂无相关资讯）_`，不得虚构内容
- 不得复制原文大段内容作为摘要，须自行概括
- `config.json` 不存在时，先提示用户按 `references/integrations.md` 配置，再执行发送步骤
- 涉及邮件/IM 等外部发送操作，发送前必须向用户确认收件人/群组
- 所有脚本均在 `scripts/` 目录下运行，公共解析模块 `markdown_parser.py` 已提取复用逻辑
- 分析结论基于公开资讯推断，不构成投资建议
