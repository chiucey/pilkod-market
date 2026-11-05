# NanoResearch 架构参考

## 项目结构

```
nanoresearch/
├── nanoresearch/
│   ├── cli.py              # CLI 入口
│   ├── config.py           # 配置管理
│   ├── agents/             # 各阶段 Agent
│   │   ├── ideation.py     # 文献检索与假说
│   │   ├── planning.py     # 实验方案设计
│   │   ├── coding.py       # 代码生成
│   │   ├── execution/      # 本地/集群执行
│   │   ├── analysis/       # 结果分析
│   │   ├── figure_gen/     # 图表生成
│   │   ├── writing/        # 论文撰写
│   │   └── review/          # 审稿与修订
│   ├── pipeline/           # 编排器 & 状态机
│   ├── schemas/            # Pydantic 数据模型
│   ├── prompts/            # YAML 提示词模板
│   ├── templates/          # LaTeX Jinja2 模板
│   └── latex/              # LaTeX 自动修复
├── mcp_server/             # MCP 工具服务
├── skills/                 # Claude Code 技能
└── pyproject.toml
```

## 执行配置文件

| Profile | 说明 |
|---------|------|
| `fast_draft` | 轻量级草稿模式，快速迭代 |
| `local_quick` | 优先本地执行，需要时可升级到 SLURM |
| `cluster_full` | 集群优先，适合重量级实验 |

## 预估费用

| 场景 | 模型选择 | 时间 | 预估费用 |
|------|---------|------|---------|
| 仅生成论文（跳过实验） | 全部 DeepSeek-V3.2 | ~30 分钟 | ~$0.5 - $1 |
| 仅生成论文（跳过实验） | 混合（Claude 写作，DeepSeek 其余） | ~30 分钟 | ~$3 - $8 |
| 完整流水线（含实验） | 全部 DeepSeek-V3.2 | 2 - 5 小时 | ~$1 - $3 |
| 完整流水线（含实验） | 混合（Claude/GPT 代码+写作） | 2 - 5 小时 | ~$10 - $20 |

## 工作空间结构

```
~/.nanobot/workspace/research/{session_id}/
├── manifest.json          # 流水线状态追踪
├── papers/                # 文献检索产物
├── plans/                 # 实验方案和分析
├── experiment/            # 生成的实验代码 + 结果
├── figures/               # 生成的论文配图
├── drafts/                # 论文草稿和审稿意见
├── output/                # 最终导出
└── logs/                  # 运行日志
```

## 飞书机器人命令

| 命令 | 描述 |
|------|------|
| `/run <课题>` | 启动研究流水线 |
| `/status` | 查看当前任务进度 |
| `/list` | 列出所有历史研究会话 |
| `/stop` | 停止当前运行的流水线 |
| `/export` | 导出最近完成的研究 |
| `/new` | 清除对话记忆，重新开始 |
| `/help` | 显示帮助信息 |
