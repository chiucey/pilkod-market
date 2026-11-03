---
name: openclaw-setup-assistant
description: "Clawdbot/openClaw 配置助手。引导用户完成从获取 API Key、安装 clawdbot、配置选项到飞书机器人接入的完整流程。支持依赖检测安装和飞书桥接部署。触发关键词：clawdbot, openclaw, 配置, 安装, setup, 飞书接入"
---

# Clawdbot 配置助手

帮助用户快速设置 clawdbot (openClaw)，引导用户完成从安装到配置的完整流程，包括可选的飞书机器人接入。

## Overview

此 skill 将引导用户完成以下工作：
1. 获取 MiniMax API Key 并安装 clawdbot
2. 完成安装过程中的配置选项选择
3. 修改配置文件并验证安装
4. （可选）接入飞书机器人

**重要：无论用户第一次说什么，都直接从第零步开始引导用户完成配置流程。**

## Workflow

### 第零步：获取 MiniMax API Key

询问用户获取 API Key：
- 访问 [MiniMax 订阅页面](https://platform.minimaxi.com/subscribe/coding-plan) 进行订阅
- 订阅完成后，复制您的 API Key 并提供给我

### 第一步：检测并安装依赖环境（如需要）

在安装 clawdbot 之前，可以先使用依赖检测功能确保环境就绪。参见下方「依赖环境检测与安装」章节。

询问用户是否需要检测和安装依赖，如果需要则运行 `install_all.sh` 脚本完成一键安装。

### 第二步：安装 clawdbot

获取到用户的 API Key 后，帮用户打开终端执行安装命令。

**重要**：环境变量必须在同一个终端会话中设置并使用，所以需要把 export 和安装命令合并执行。

**macOS**:
```bash
osascript -e 'tell application "Terminal" to activate' -e 'tell application "Terminal" to do script "export MINIMAX_API_KEY='"'"'<用户提供的API_KEY>'"'"' && curl -fsSL https://molt.bot/install.sh | bash"'
```

**Linux** (如果有图形界面):
```bash
gnome-terminal -- bash -c "export MINIMAX_API_KEY='<用户提供的API_KEY>' && curl -fsSL https://molt.bot/install.sh | bash; exec bash"
```

告诉用户：
> 我已经打开了终端并开始安装 clawdbot，请按照下面的配置选项进行选择。

### 第三步：配置选项指引

告诉用户在安装过程中按以下选项进行选择：

| 步骤 | 选项 | 选择 |
|------|------|------|
| 1 | Continue? | **Yes** |
| 2 | Onboarding mode | **QuickStart** |
| 3 | Model/auth provider | **MiniMax**（按 2 次下箭头） |
| 4 | MiniMax auth method | **MiniMax M2.1** |
| 5 | Use existing MINIMAX_API_KEY | **Yes** |
| 6 | Default model | **Keep current (minimax/MiniMax-M2.1)** |
| 7 | Select channel | **Skip for now**（按 18 次下箭头到最后） |
| 8 | Configure skills now? | **No**（按右箭头选择 No） |
| 9 | Enable hooks | **Skip for now**（按空格选中后回车） |
| 10 | How do you want to hatch | **Do this later**（按 2 次下箭头） |

### 第四步：等待用户确认安装完成

让用户安装完毕后，告诉你他已经安装完成。

### 第五步：修改 baseUrl

修改 `~/.openclaw/openclaw.json` 配置文件中的 `baseUrl`：

- **原值**: `https://api.minimax.io/anthropic`
- **新值**: `https://api.minimaxi.com/anthropic`

可以使用以下命令自动修改：

```bash
sed -i '' 's|https://api.minimax.io/anthropic|https://api.minimaxi.com/anthropic|g' ~/.openclaw/openclaw.json
```

执行完后需要执行以下命令重启 gateway：
```bash
openclaw gateway restart
```

### 第六步：打开预览页面

帮用户打开浏览器访问 clawdbot 界面，让用户看到效果：

```bash
open http://127.0.0.1:18789
```

或者告诉用户在浏览器中访问：**http://127.0.0.1:18789**

询问用户是否能正常运行，如果用户反馈有问题：

**你需要自己执行以下命令来诊断和修复问题（不要告诉用户执行这些命令，你自己运行并根据结果判断）：**

1. 先运行修复命令：
```bash
openclaw doctor --fix
```

2. 再运行 dashboard 查看状态：
```bash
openclaw dashboard
```

根据命令输出结果判断问题所在，并给用户反馈解决方案。

### 第七步：询问是否需要飞书接入

问用户：**是否需要接入飞书机器人？**

如果用户需要飞书接入，进入下一步；否则配置完成。

### 第八步：获取飞书凭证（仅当用户需要时）

询问用户提供飞书机器人的凭证：
- **FEISHU_APP_ID** - 飞书机器人的 App ID（以 `cli_` 开头）
- **FEISHU_APP_SECRET** - 飞书机器人的 App Secret

提示用户可以在 [飞书开放平台](https://open.feishu.cn/app) 创建和管理机器人。

### 第九步：部署飞书桥接

获取到飞书凭证后：

1. 设置环境变量：
```bash
export FEISHU_APP_ID='<用户提供的APP_ID>'
export FEISHU_APP_SECRET='<用户提供的APP_SECRET>'
```

2. 执行飞书桥接部署（参见下方「Deploy Feishu-Moltbot Bridge」章节的完整步骤）

3. 将配置文件复制到 clawdbot 目录：
```bash
cp <生成的配置文件路径> ~/.clawdbot/
```

### 第十步：配置飞书机器人

部署完成后，指导用户在飞书开放平台完成机器人配置：

#### 1. 添加机器人能力
在应用详情页，点击「添加应用能力」，选择添加「机器人」。

#### 2. 配置权限
在「权限管理」中，添加以下权限：
- 获取与发送单聊、群组消息
- 接收群聊中@机器人消息事件
- 读取用户发给机器人的单聊消息

也可以直接导入以下 JSON 来快速添加权限：
```json
{
  "scopes": {
    "tenant": [
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly"
    ],
    "user": []
  }
}
```

#### 3. 配置事件与回调
- 在「事件与回调」中，选择订阅方式为：**使用长连接接收事件**
- 在下方事件列表中，添加「接收消息」事件

#### 4. 发布应用
在「版本管理与发布」中，创建并发布线上版本。

发布成功后，就可以在飞书中与 clawdbot 机器人进行对话了！

---

## 依赖环境检测与安装

此 skill 包含多个独立脚本用于检测并安装 Moltbot/Clawdbot 运行所需的依赖环境，并配置国内镜像源以加速下载。

### 使用流程

1. **询问用户** 是否需要检测和安装依赖
2. **告知用户** 将检测和安装以下依赖：
   - Node.js v22+
   - npm（配置国内镜像）
   - pnpm
   - Git
   - Homebrew（仅 macOS）
3. **用户同意后** 执行安装脚本

### 脚本结构

| 脚本 | 功能 |
|------|------|
| `install_all.sh` | 主脚本，按顺序调用其他脚本 |
| `install_git.sh` | 安装 Git |
| `install_homebrew.sh` | 安装 Homebrew（仅 macOS） |
| `install_node.sh` | 安装 Node.js 和 pnpm |

### 需要安装的依赖

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| Node.js | v22+ | JavaScript 运行时 |
| npm | - | Node.js 包管理器 |
| pnpm | - | 高效的包管理器 |
| Git | - | 版本控制工具 |
| Homebrew | - | macOS 包管理器（仅 macOS） |

### 配置的国内镜像源

| 工具 | 镜像源 |
|------|--------|
| npm/pnpm | https://registry.npmmirror.com |
| Homebrew | 清华大学镜像 |
| Node.js 二进制 | https://npmmirror.com/mirrors/node/ |

### 执行方式

#### 一键安装（推荐）

```bash
chmod +x install_all.sh install_git.sh install_homebrew.sh install_node.sh
./install_all.sh
```

#### 单独安装

也可以单独运行各个脚本：

```bash
# 仅安装 Git
./install_git.sh

# 仅安装 Homebrew（macOS）
./install_homebrew.sh

# 仅安装 Node.js 和 pnpm
./install_node.sh
```

### 安装流程

1. **[1/3] Git**：macOS 通过 Xcode Command Line Tools 安装，Linux 通过包管理器安装
2. **[2/3] Homebrew**：仅 macOS，使用清华镜像安装并配置镜像源
3. **[3/3] Node.js + pnpm**：macOS 通过 Homebrew 安装，Linux 通过 NodeSource 安装

### 支持的系统

- macOS（Intel 和 Apple Silicon）
- Linux（Debian/Ubuntu、Fedora、CentOS/RHEL）
- WSL（Windows Subsystem for Linux）

### 注意事项

- 请**不要**以 root 用户运行脚本（Homebrew 不支持）
- macOS 安装 Git 时会弹出 Xcode Command Line Tools 安装窗口
- Linux 安装时需要 sudo 权限

---

## Deploy Feishu-Moltbot Bridge

Automatically clone, configure, and start the Feishu-Moltbot bridge from GitHub.

### Prerequisites

Before running this skill, ensure:

1. **Node.js >= 18** is installed
2. **Moltbot/Clawdbot Gateway** is running (`clawdbot gateway status`)
3. **Environment variables** are set:
   - `FEISHU_APP_ID` - Your Feishu bot's App ID (e.g., `cli_xxxxxxxxx`)
   - `FEISHU_APP_SECRET` - Your Feishu bot's App Secret
4. **Feishu bot** is already created on [open.feishu.cn](https://open.feishu.cn/app) with:
   - Bot capability enabled
   - Permissions: `im:message`, `im:message.group_at_msg`, `im:message.p2p_msg`
   - Event `im.message.receive_v1` configured with **WebSocket long-connection**
   - App published

### Deployment Steps

#### Step 1: Clone Repository

```bash
cd ~
git clone git@github.com:AlexAnys/feishu-moltbot-bridge.git
cd feishu-moltbot-bridge
```

#### Step 2: Install Dependencies

```bash
npm install
```

#### Step 3: Configure Credentials

Create secrets directory and store the App Secret:

```bash
# Create secrets directory
mkdir -p ~/.clawdbot/secrets

# Write App Secret from environment variable
echo "$FEISHU_APP_SECRET" > ~/.clawdbot/secrets/feishu_app_secret

# Secure the file (read-only for owner)
chmod 600 ~/.clawdbot/secrets/feishu_app_secret
```

#### Step 4: Start Bridge

Run the bridge with the App ID:

```bash
FEISHU_APP_ID=$FEISHU_APP_ID node bridge.mjs
```

### Automated Script

Complete one-liner for automated deployment:

```bash
cd ~ && \
git clone git@github.com:AlexAnys/feishu-moltbot-bridge.git && \
cd feishu-moltbot-bridge && \
npm install && \
mkdir -p ~/.clawdbot/secrets && \
echo "$FEISHU_APP_SECRET" > ~/.clawdbot/secrets/feishu_app_secret && \
chmod 600 ~/.clawdbot/secrets/feishu_app_secret && \
FEISHU_APP_ID=$FEISHU_APP_ID node bridge.mjs
```

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `FEISHU_APP_ID` | Yes | Feishu App ID (starts with `cli_`) |
| `FEISHU_APP_SECRET` | Yes | Feishu App Secret |
| `CLAWDBOT_CONFIG_PATH` | — | Custom Clawdbot config path (default: `~/.clawdbot/clawdbot.json`) |
| `CLAWDBOT_AGENT_ID` | — | Agent to use (default: `main`) |

### Verification

After starting, you should see:

```
[OK] Feishu bridge started (appId=cli_xxxxxxxxx)
```

Test by sending a message to your Feishu bot. If it responds, the deployment is successful!

### Optional: Set Up Auto-Start (macOS)

To make the bridge start automatically on system boot:

```bash
FEISHU_APP_ID=$FEISHU_APP_ID node setup-service.mjs
launchctl load ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist
```

### Troubleshooting

#### Check if Gateway is running

```bash
clawdbot gateway status
```

#### Check logs

```bash
tail -f ~/.clawdbot/logs/feishu-bridge.err.log
```

#### Verify secret file

```bash
ls -la ~/.clawdbot/secrets/feishu_app_secret
```

#### Stop the service

```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist
```

---

## 常见问题处理

### Token 问题
如果用户反馈遇到 token 相关问题，让用户执行以下命令打开控制面板：
```bash
openclaw dashboard
```

### 安装问题
如果安装过程中出现问题，可以使用以下命令自动修复：
```bash
openclaw doctor --fix
```

## 注意事项

- 确保网络连接正常
- API Key 和飞书凭证请妥善保管，不要泄露
- 如遇安装问题，可运行 `openclaw doctor --fix` 修复
