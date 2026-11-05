---
name: research-claw-assistant
description: Research Claw AI research assistant skill. Use when users need to manage LaTeX paper projects, sync Overleaf, search academic literature, track conference deadlines, use multi-agent collaboration, automate research workflows, configure IM channels (Telegram/Feishu/QQ/DingTalk), or need a self-hosted AI academic research assistant.
---

# Research Claw - AI 学术研究助手

Research Claw 是一个自托管的 AI 学术研究助手，专门用于帮助研究人员管理论文项目、搜索文献、追踪截止日期和自动化研究工作流。

## 核心功能

### LaTeX 论文管理
- 通过对话读取、编写和重构 `.tex` / `.bib` 文件
- 一键编译 LaTeX 并自动诊断错误
- 内置顶会格式技能：NeurIPS, ICML, ICLR, AAAI, ACL, CVPR

### Overleaf 同步
- 双向同步 - 无需浏览器即可 pull/push 更改
- 自动 Git 提交每次 AI 编辑，便于回滚

### 多智能体协作
- 使用 `/task` 命令分解复杂任务为 DAG 并行执行
- 子智能体在隔离沙箱中工作，避免文件覆盖
- 5 阶段工作流：UNDERSTAND → PROPOSE → PLAN → EXECUTE → FINALIZE

### 文献搜索
- arXiv, PubMed, OpenAlex 集成
- 支持 PDF 全文阅读和分析

### 研究雷达 (Research Radar)
自动化任务，包括：
| 任务 | 功能 | 默认调度 |
|------|------|----------|
| Daily Scan | 搜索新论文并总结 | 每日早晨 |
| Direction Drift | 检测研究领域变化和新兴趋势 | 每日 |
| Deadline Watch | 追踪会议截止日期 | 每日 |
| Conference Track | 监控目标会议 CFP | 每周 |
| Weekly Digest | 编译周总结 | 周一早晨 |

结果推送到：Telegram, Feishu, DingTalk, Email 或任何 Apprise 兼容渠道

### 多渠道访问
- **Web UI** - 浏览器仪表板配置和监控
- **CLI** - 全功能交互终端
- **IM Bots** - 飞书、Telegram、QQ、钉钉

## 常用命令

| 命令 | 功能 |
|------|------|
| `/task <目标>` | 分解复杂目标为子任务，并行执行 |
| `/compile` | 编译 LaTeX 为 PDF |
| `/sync pull` | 从 Overleaf 拉取最新文件 |
| `/sync push` | 推送本地更改到 Overleaf |
| `/git` | 进入交互式 Git 模式（历史、diff、回滚） |
| `/reset` | 清除当前会话历史 |
| `/back` | 返回默认大厅 |
| `/done` | 结束当前任务会话 |

## 架构概览

```
CLI / Web UI / 飞书 / Telegram / QQ / 钉钉
                    ↓
              MessageBus
                    ↓
         ┌──────────────────┐
         │    AgentLoop     │
         │  (主智能体)      │
         └────────┬─────────┘
                  ↓
         ┌──────────────────┐
         │   ToolRegistry   │
         │   (40+ 工具)     │
         └────────┬─────────┘
                  ↓
     Project / LLM Provider / Automation
```

## 快速开始

### 安装
```bash
git clone https://github.com/nanoAgentTeam/research-claw.git
cd research-claw
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 配置（第一步）
```bash
python cli/main.py gateway --port 18790
```
然后在浏览器打开 **http://localhost:18790/ui**：
1. **Provider Management** - 添加 LLM 提供商（API Key, 模型名, base URL）
2. **Channel Accounts** - (可选) 添加 IM 机器人凭证
3. **Push Subscriptions** - (可选) 配置自动化结果推送

### Overleaf 授权（可选）
```bash
pip install overleaf-sync
ols login  # 打开浏览器登录
```

### 运行
```bash
# CLI 模式
python cli/main.py agent

# Gateway 模式（启动 Web UI）
python cli/main.py gateway --port 18790
```

## 技能系统

技能是领域特定的 SOP（标准操作程序），智能体可以按需激活。添加自定义技能：

1. 在 `config/.skills/` 下创建文件夹
2. 添加 `SKILL.md` 文件定义技能

## 配置参考

| 文件/部分 | 用途 |
|-----------|------|
| `settings.json` | 运行时配置（LLM 提供商、渠道、功能） |
| `config/tools.json` | 工具注册表 |
| `config/commands.json` | 斜杠命令定义 |
| `config/agent_profiles/` | 智能体角色配置 |
| `workspace/{project}/project.yaml` | 项目级设置 |

## 使用场景示例

1. **论文写作**：使用 `/task` 分解论文写作任务，多个子智能体并行完成各章节
2. **文献调研**：使用 Research Radar 自动追踪领域最新论文，定期推送摘要
3. **版本管理**：使用 `/git` 命令回滚不满意的 AI 修改
4. **跨平台协作**：通过飞书/Telegram 与研究助手交互，随时随地管理项目
