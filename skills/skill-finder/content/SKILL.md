---
name: skill-finder
description: "搜索、下载、安装和管理 nanobot 技能包。当用户需要查找新技能、安装技能包、管理已安装技能或从 GitHub、HuggingFace 等来源获取扩展能力时触发。关键词：技能搜索、skill search、install skill、技能安装、技能管理"
---

# 技能搜索器 (Skill Finder)

## Overview

自主搜索、下载和安装 nanobot 技能包，让 AI 助手能够动态扩展能力。支持从多个来源（GitHub、HuggingFace、官方仓库、本地文件）查找技能，并自动处理依赖安装和配置。

## 核心能力

1. **搜索技能**：从多个来源查找技能（GitHub、HuggingFace、官方仓库）
2. **预览技能**：显示技能详情、依赖和配置要求
3. **下载技能**：自动下载 .skill 包或 Git 仓库
4. **安装技能**：解压、复制、安装依赖、配置环境变量
5. **验证技能**：测试技能是否正确加载

## Workflow

### 1. 搜索技能

当用户需要查找技能时：

1. 使用 `skill_finder.py` 的 `search` 命令搜索相关技能
2. 解析返回的 JSON 结果
3. 向用户清晰展示可用选项，包含名称、描述、来源和评分等信息

### 2. 安装技能

当用户确认要安装某个技能时：

1. 安装前向用户确认，说明将要安装的依赖
2. 使用 `install` 命令下载并安装技能
3. 自动处理依赖安装
4. 验证技能是否正确加载
5. 报告安装结果

### 3. 管理技能

- 使用 `list` 命令列出已安装的技能
- 使用 `uninstall` 命令卸载不需要的技能

## 命令参考

```bash
# 搜索技能
python3 /workspace/skills/skill-finder/skill_finder.py search "<关键词>"

# 安装技能
python3 /workspace/skills/skill-finder/skill_finder.py install <skill-name>

# 列出已安装技能
python3 /workspace/skills/skill-finder/skill_finder.py list

# 卸载技能
python3 /workspace/skills/skill-finder/skill_finder.py uninstall <skill-name>
```

## 输出格式

所有命令返回 JSON 格式结果，便于 AI 助手解析和处理。

## 支持的技能来源

| 来源 | 说明 |
|------|------|
| GitHub | 搜索 nanobot-skill 相关的仓库 |
| HuggingFace | 搜索 Spaces 和 Datasets 中的技能 |
| 官方仓库 | nanobot 官方技能市场 |
| 本地文件 | 安装本地 .skill 包 |

## 交互规范

1. **搜索结果展示**：清晰列出找到的技能，包含名称、描述、来源
2. **安装确认**：安装前向用户确认，说明将要安装的依赖
3. **错误处理**：遇到错误时提供清晰的解释和解决建议
4. **进度反馈**：在长时间操作时提供进度更新
