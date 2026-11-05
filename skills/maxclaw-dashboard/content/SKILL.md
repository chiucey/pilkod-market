---
name: maxclaw-dashboard
description: MaxClaw/OpenClaw 控制面板技能。可视化配置和管理 MaxClaw 的各种设置，包括模型配置、渠道管理、插件管理、技能中心和系统设置。当用户要求创建控制面板、仪表盘、配置管理界面或需要管理 MaxClaw 配置时使用。
---

# MaxClaw 控制面板

一个功能完整的 MaxClaw/OpenClaw Web 控制面板，用于可视化管理和配置 MaxClaw 的各种设置。

## 功能模块

### 1. 总览 (Overview)
- 系统状态统计卡片
- 当前模型配置展示
- 配额使用进度条
- 快速操作入口

### 2. 模型配置 (Model Configuration)
- 支持 6 种模型提供商：
  - MiniMax (推荐)
  - OpenAI
  - Anthropic
  - Google Gemini
  - Azure OpenAI
  - Custom Provider
- 模型名称、API端点、API密钥配置
- 环境区域切换（中国大陆/国际版）
- 套餐选择（Free/Pro/Team/Enterprise）
- MiniMax OAuth 快速授权

### 3. 渠道设置 (Channels)
- 飞书集成
- 钉钉集成
- 企业微信集成
- Slack 集成
- Discord 集成
- 各渠道独立开关和高级配置

### 4. 插件管理 (Plugins)
- 已安装插件列表
- 启用/禁用状态管理
- 版本信息展示

### 5. 技能中心 (Skills)
- 技能搜索功能
- 已安装技能浏览
- 技能数量统计

### 6. 系统设置 (Settings)
- 网关配置（端口、绑定地址）
- 后台服务管理
- 危险操作区域

## 技术栈

- React 18 + TypeScript
- Tailwind CSS
- Lucide React Icons
- Vite 构建工具

## 安装说明

### 作为独立项目运行

```bash
# 克隆项目
git clone <repository-url>
cd maxclaw-dashboard

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

### 部署到 Web

```bash
pnpm build
# 将 dist 目录部署到任意静态托管服务
```

## 配置文件

控制面板读取的 MaxClaw 配置文件路径：
- `~/.openclaw/openclaw.json` (Linux/Mac)
- `%USERPROFILE%\.openclaw\openclaw.json` (Windows)

## 使用场景

- 替代命令行配置，提供可视化界面
- 快速切换模型提供商和套餐
- 管理多个消息渠道的集成
- 查看和管理已安装的技能和插件
- 监控网关状态和配额使用情况

## 注意事项

1. 修改配置后需要重启网关使更改生效
2. 敏感信息（如 API Key）会以掩码形式显示
3. 危险操作（如重置配置）需要确认
