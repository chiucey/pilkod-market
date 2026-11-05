---
name: team-creator
description: |
  自动创建 Agent 团队。提供多种预设模板（如项目管理团队、开发团队等），也可自定义 agent 列表。
  当需要快速搭建多 agent 工作流、创建项目团队时使用。
---

# Team Creator

## 功能

- 多种预设团队模板
- 自定义 agent 列表
- 自动配置 workspace、飞书绑定、模型
- 支持 dry-run 预览
- 支持已存在 agent 跳过
- 模板内置角色与 emoji
- 支持从 JSON 团队配置文件创建
- 支持为不同 agent 指定不同模型
- 支持导出团队配置 JSON
- 支持按现有 agent 名称快速克隆团队配置
- 支持导出飞书 bot 配置骨架
- 支持导出 OpenClaw config.patch 骨架
- 支持创建后自动校验
- 支持 JSON / YAML 团队文件
- 支持按角色自动选择默认模型
- 支持初始化 SOUL.md / AGENTS.md / USER.md
- 支持带 bot 前缀导出 config.patch
- 支持导出 bindings 补丁
- 支持从 assets/templates 加载外部模板
- 支持模板继承（extends）
- 支持按 agent 名称覆盖继承模板中的字段
- 支持模板元信息（description / tags / recommended_for / default_bind_feishu）
- 支持查看模板详情
- 支持模板默认启用飞书绑定
- 支持输出结构化摘要与 JSON 报告

## 预设模板

| 模板 | Agents | 说明 |
|------|--------|------|
| `default` | pm, ui, coding | 默认团队 |
| `full` | pm, ui, coding, tester, devops | 完整团队 |
| `minimal` | pm, coding | 最小团队 |
| `ai` | pm, coding, researcher | AI 开发团队 |
| `web` | frontend, backend, designer | Web 开发团队 |
| `startup` | pm, ui, coding, founder-office, growth | 外部模板示例（继承） |
| `lean-dev` | pm, ui, coding, qa | 外部模板示例（继承 + 字段覆盖） |

## 使用方法

### 方式一：使用模板

```bash
python scripts/team_creator.py --template default
python scripts/team_creator.py --template full --bind-feishu
```

### 方式二：自定义 agent

```bash
python scripts/team_creator.py --agents "pm,ui,coding,tester"
python scripts/team_creator.py --agents "pm,ui,coding" --model minimax/MiniMax-M2.5
```

### 完整选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--template` | 团队模板 | - |
| `--agents` | 自定义 agent 列表 | - |
| `--model` | 模型 | minimax/MiniMax-M2.5 |
| `--bind-feishu` | 绑定飞书 | 否 |
| `--workspace-base` | workspace 根目录 | ~/.openclaw/workspace-{name} |
| `--dry-run` | 仅预览，不实际创建 | 否 |
| `--skip-existing` | 已存在则跳过 | 否 |
| `--team-file` | 从 JSON 文件加载团队配置 | - |
| `--export-team-file` | 导出当前团队配置为 JSON | - |
| `--clone-agents` | 基于现有 agent 名称生成团队配置 | - |
| `--export-bot-skeleton` | 导出飞书 bot 配置骨架 JSON | - |
| `--export-config-patch` | 导出 OpenClaw config.patch 骨架 JSON | - |
| `--validate` | 创建后执行校验 | 否 |
| `--smart-model` | 按角色自动选择默认模型 | 否 |
| `--init-files` | 初始化 SOUL.md / AGENTS.md / USER.md | 否 |
| `--bot-prefix` | 导出 patch 时为 bot 增加前缀 | - |
| `--include-bindings` | 导出的 patch 中包含 bindings | 否 |
| `--describe-template` | 查看模板详情 | - |
| `--no-bind-feishu` | 禁用模板默认的飞书绑定 | 否 |
| `--summary` | 输出结构化摘要 | 否 |
| `--report-file` | 将结构化摘要写入 JSON 文件 | - |

## 示例

```bash
# 使用默认模板创建团队
python scripts/team_creator.py --template default

# 使用外部模板（assets/templates/startup.yaml）
python scripts/team_creator.py --template startup --smart-model --dry-run

# 使用继承 + 字段覆盖模板（assets/templates/lean-dev.yaml）
python scripts/team_creator.py --template lean-dev --smart-model --dry-run

# 查看模板详情
python scripts/team_creator.py --describe-template startup

# 使用模板默认飞书绑定（startup 模板）
python scripts/team_creator.py --template startup --dry-run

# 覆盖模板默认行为，不绑定飞书
python scripts/team_creator.py --template startup --no-bind-feishu --dry-run

# 输出结构化摘要与 JSON 报告
python scripts/team_creator.py --template lean-dev --dry-run --summary --report-file /tmp/team-summary.json

# 使用完整模板 + 飞书绑定
python scripts/team_creator.py --template full --bind-feishu

# 自定义团队
python scripts/team_creator.py --agents "pm,ui,coding,analyst" --model minimax/MiniMax-M2.5

# 从 JSON 团队文件创建
python scripts/team_creator.py --team-file assets/team.example.json --dry-run

# 从 YAML 团队文件创建
python scripts/team_creator.py --team-file assets/team.example.yaml --dry-run

# 导出团队配置
python scripts/team_creator.py --template default --export-team-file /tmp/team.json

# 克隆现有团队配置
python scripts/team_creator.py --clone-agents pm,ui,coding --export-team-file /tmp/cloned-team.json

# 导出飞书 bot 配置骨架
python scripts/team_creator.py --template default --export-bot-skeleton /tmp/bots.json

# 导出 OpenClaw config.patch 骨架
python scripts/team_creator.py --template default --export-config-patch /tmp/team-patch.json

# 导出带 bot 前缀和 bindings 的 patch
python scripts/team_creator.py --template default --export-config-patch /tmp/team-prefixed-patch.json --bot-prefix team1 --include-bindings

# 创建后自动校验
python scripts/team_creator.py --template default --skip-existing --validate

# 按角色自动选择模型
python scripts/team_creator.py --template default --smart-model --dry-run

# 初始化 bootstrap 文件
python scripts/team_creator.py --template default --init-files --skip-existing
```

## 输出示例

```
==================================================
🚀 正在创建团队: default (pm, ui, coding)
   
📦 pm
   ✅ workspace: ~/.openclaw/workspace-pm
   ✅ identity: pm
   ✅ 飞书绑定: bot_pm
   
📦 ui  
   ✅ workspace: ~/.openclaw/workspace-ui
   ✅ identity: ui
   ✅ 飞书绑定: bot_ui
   
📦 coding
   ✅ workspace: ~/.openclaw/workspace-coding
   ✅ identity: coding
   ✅ 飞书绑定: bot_coding

🎉 团队创建完成！

⚠️ 下一步:
   1. 在飞书开放平台发布新 bot（如需要）
   2. 在群里添加 bot
   3. 重启 gateway: openclaw gateway restart
==================================================
```
