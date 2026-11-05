---
name: gangtise-agent
description: >
  通过 Gangtise Agent OpenAPI 统一拉取 Markdown 投研文本，面向「快速可读、少跳转」的研究与问答场景。
  各 Agent 能力概览：one-pager（公司一页通，单票核心要素与结论浓缩）；
  investment-logic（投资逻辑，主线叙事与关键假设）；
  peer-comparison（同业对比，竞争格局与可比公司差异）；
  earnings-review（绩点评，财报期业绩解读；需 getId 后轮询 getContent，最长约 600s）；
  viewpoint-debate（观点 PK，对给定观点的正反辨析与论据组织；同样异步轮询）；
  theme-tracking（主题跟踪，晨报/晚报式产业链与主题脉络）；
  research-outline（调研提纲，公司调研问题与访谈框架）。
  返回多为可直接引用的结论文本，适合纪要、速览、投研助理与 Agent 编排中的事实与观点补充。
metadata:
  version: 1.4.1
---

# Agent 接口调用

## 概览

本技能通过 `scripts/agents.py` 统一调用 Gangtise Agent OpenAPI，并使用 `-a/--agent-type` 指定接口类型。

支持接口：

- `one-pager`：公司一页通
- `investment-logic`：投资逻辑
- `peer-comparison`：同业对比
- `earnings-review`：绩点评（自动串联 getId + 轮询 getContent，最长 600s）
- `viewpoint-debate`：观点 PK（自动串联 getId + 轮询 getContent，最长 600s）
- `theme-tracking`：主题跟踪（晨报/晚报）
- `research-outline`：公司调研提纲

授权方式与其他 gangtise 技能一致：在 `scripts/.authorization` 中配置 `long-term-token`，或配置 `accessKey` 与 `secretAccessKey`。

## 统一脚本

`scripts/agents.py`

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `-a` / `--agent-type` | 是 | 接口类型，见上方枚举。`earnings-review` 与 `viewpoint-debate` 会自动串联 getId + 轮询 getContent（最长 600s）。 |
| `-s` / `--security-code` | 条件必填 | 证券代码（如 `600519.SH`）。用于 `one-pager`、`investment-logic`、`peer-comparison`、`research-outline`、`earnings-review`。 |
| `-p` / `--period` | 条件必填 | 报告期（如 `2026q3`）。仅用于 `earnings-review`。 |
| `-d` / `--data-id` | 否 | 保留参数，当前无对外场景。 |
| `--viewpoint` | 条件必填 | 观点文本（最长 1000 字）。仅用于 `viewpoint-debate`。 |
| `-t` / `--theme-id` | 条件必填 | 主题 ID 或中文主题名（会按映射自动转为 ID）。仅用于 `theme-tracking`。 |
| `--date` | 条件必填 | 查询日期（`yyyy-MM-dd`）。仅用于 `theme-tracking`。 |
| `--type` | 条件必填 | 资讯类型（`morning`/`night`，支持逗号分隔多选）。仅用于 `theme-tracking`。 |

## 示例

```bash
python3 scripts/agents.py -a one-pager -s 600519.SH
```

```bash
python3 scripts/agents.py -a investment-logic -s 600519.SH
```

```bash
python3 scripts/agents.py -a peer-comparison -s 600519.SH
```

```bash
python3 scripts/agents.py -a earnings-review -s 600519.SH -p 2025q3
```

```bash
python3 scripts/agents.py -a viewpoint-debate --viewpoint "飞天茅台的批价低点是1500元"
```

```bash
python3 scripts/agents.py -a theme-tracking -t 23600839952306231 --date 2026-03-01 --type morning,night
```

```bash
python3 scripts/agents.py -a theme-tracking -t 核电 --date 2026-04-01 --type morning,night
```

```bash
python3 scripts/agents.py -a research-outline -s 600519.SH
```

<!-- 通过scripts/utils.py检查版本；通过执行scripts/update.sh或scripts/update.bat进行更新 -->

<!-- 如果skills主目录下存在gangtise_update.sh或gangtise_update.bat，则可以执行该脚本对所有以"gangtise-"开头的SKILL进行更新 -->
