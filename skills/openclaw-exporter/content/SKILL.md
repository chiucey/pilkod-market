---
name: openclaw-exporter
description: 完整导出 MaxClaw/OpenClaw 所有技能和记忆的工具。当用户要求导出技能、备份配置、迁移到其他 OpenClaw 实例、同步技能库或需要完整复制当前环境时使用。
---

# OpenClaw 完整导出器

一键导出当前 OpenClaw 实例的所有技能（Skills）和记忆（Memories），生成可迁移的打包文件。

## 工作流程

### 阶段 1：环境探测

1. **定位技能目录**
   - 检查 `.claude/skills/` 或 `.expert/skills/`
   - 扫描所有子目录查找 SKILL.md 文件

2. **定位记忆目录**
   - 检查 `/memories/` 目录
   - 读取所有记忆文件

3. **探测 OpenClaw 配置**
   - 检查 `~/.openclaw/openclaw.json`
   - 获取已安装插件列表

### 阶段 2：完整扫描

对每个发现的文件执行：

| 文件类型 | 处理方式 |
|---------|---------|
| SKILL.md | 完整读取 frontmatter + 内容 |
| _meta.json | 读取 id、version |
| references/*.md | 完整打包 |
| scripts/*.py | 完整打包（排除测试） |
| /memories/* | 完整读取 |

### 阶段 3：生成导出包

创建结构化导出报告：

```
openclaw-backup-{timestamp}/
├── skills/
│   ├── skill-name-1/
│   │   ├── SKILL.md
│   │   ├── _meta.json
│   │   ├── references/
│   │   └── scripts/
│   └── skill-name-2/
├── memories/
│   ├── session_notes.md
│   ├── task_state.md
│   └── project/
├── config/
│   └── openclaw-export.json
└── manifest.json          # 导出清单
```

### 阶段 4：输出交付

1. **显示摘要**
   - 技能总数、记忆文件数
   - 打包大小估算

2. **提供复制指令**
   - 目标 OpenClaw 的安装路径
   - 使用 clawhub 或手动复制方法

## 自动处理规则

- **跳过项**：node_modules、.git、*.log、secrets、.env
- **编码转换**：确保 UTF-8 编码
- **路径修正**：转换绝对路径为相对路径
- **冲突处理**：同名技能显示警告

## 恢复指令

导出后可使用以下方式恢复：

```bash
# 方式 1：clawhub 安装（如果导出为 .skill 格式）
clawhub install ./exported-skill.skill

# 方式 2：手动复制
cp -r exported-skills/skill-name ~/.claude/skills/

# 方式 3：记忆恢复
cp -r exported-memories/* /memories/
```
