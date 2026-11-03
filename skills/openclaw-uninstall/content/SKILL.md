---
name: openclaw-uninstall
description: 一键全自动卸载 OpenClaw CLI 工具及其所有相关文件和配置。当用户要求卸载 openclaw、删除 openclaw、清理 openclaw 或完全移除 openclaw 安装时使用此技能。支持 npm/pip/uv 三种安装方式的检测和清理。
---

# OpenClaw 卸载技能

## 执行步骤

### 1. 检测安装状态

自动检测以下安装方式：
- **npm 全局包**: `openclaw`, `clawd`, `@openclaw/cli`
- **pip 包**: `openclaw`
- **uv pip 包**: `openclaw`

### 2. npm 卸载

```bash
npm uninstall -g openclaw
npm uninstall -g clawd
npm uninstall -g @openclaw/cli
```

### 3. pip 卸载

```bash
pip uninstall openclaw -y
uv pip uninstall openclaw
```

### 4. 清理配置文件

删除以下目录（如果存在）：
- `~/.openclaw`
- `~/.config/openclaw`
- `~/.clawd`
- `~/.openclaw-plugins`

### 5. 清理残留文件

```bash
rm -rf ~/.npm/_npx/*openclaw*
rm -rf /tmp/.npm-global/lib/node_modules/openclaw*
```

### 6. 验证卸载

检查以下命令确保卸载成功：
```bash
which openclaw  # 应返回空
pip show openclaw  # 应返回空
uv pip show openclaw  # 应返回空
```

## 成功标准

- `which openclaw` 不存在
- pip/uv 中无 openclaw 包
- 所有配置文件已删除

## 平台支持

- Linux (npm/pip/uv)
- macOS (npm/pip/uv)
- Cloud Shell 环境
