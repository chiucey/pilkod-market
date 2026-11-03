---
name: openclaw-install
description: Install and configure the OpenClaw CLI tool and OpenClaw IM plugins for OpenClaw, ClawdBot, and MoltBot
---

# Install OpenClaw

Install, update, and maintain the OpenClaw CLI tool and OpenClaw IM plugins.

> This skill applies to **OpenClaw**, **ClawdBot**, and **MoltBot**. They are different names for the same tool. Use this skill for installing, updating, maintaining, and configuring OpenClaw, as well as installing OpenClaw IM plugins.

# Prerequisite Environment Check

First, check the user's operating system. Possible systems include, but are not limited to, macOS and Windows. For Windows, use PowerShell only for now, because setting up WSL2 is inconvenient for many users.

**You must determine whether OpenClaw is already installed. If it is not installed, proceed with the installation process.**

# OpenClaw Installation
## Detailed OpenClaw Installation Process

Before starting the installation, make sure the following requirements are met. **If the user is missing any dependency, help them install it first before continuing.**

### Requirements

| Dependency | Minimum Version | Description |
| ------- | ------- | ----------- |
| Node.js | 22.0.0+ | Runtime environment. Download from [https://nodejs.org](https://nodejs.org) |
| npm | 10.0.0+ | Package manager, installed with Node.js |
| Git | 2.0+ | Version control system |

#### Install Node.js (if missing)

**Using `nvm` is recommended** because it makes version management easier:

- **macOS / Linux**:
  ```bash
  # Install nvm (users in mainland China can use the Gitee mirror)
  # For users outside mainland China:
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  # For users in mainland China:
  curl -o- https://gitee.com/mirrors/nvm/raw/v0.40.1/install.sh | bash

  # Reload shell configuration
  source ~/.bashrc  # or source ~/.zshrc

  # Install Node.js 22
  # Users in mainland China can run this first for a faster mirror:
  # export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node
  nvm install 22
  nvm use 22
  ```
- **Windows**: Use [nvm-windows](https://github.com/coreybutler/nvm-windows/releases), or download the installer from [https://nodejs.org](https://nodejs.org)

**Direct installation** (without `nvm`):

- **macOS**: `brew install node@22`
- **Windows**: Download the installer from [https://nodejs.org](https://nodejs.org)
- **Linux (Ubuntu/Debian)**:
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```

**Configure an npm mirror** (recommended for users in mainland China)

Users in mainland China are recommended to use the npmmirror registry to speed up package downloads:

```bash
npm config set registry https://registry.npmmirror.com
```

> Verify the configuration with: `npm config get registry`

#### Install Git (if missing)

- **Windows**
If the system is x64, ask the user to download and install:
[https://registry.npmmirror.com/-/binary/git-for-windows/v2.51.0.windows.1/Git-2.51.0-64-bit.exe](https://registry.npmmirror.com/-/binary/git-for-windows/v2.51.0.windows.1/Git-2.51.0-64-bit.exe)

If the system is ARM64, ask the user to download and install:
[https://registry.npmmirror.com/-/binary/git-for-windows/v2.51.0.windows.1/Git-2.51.0-arm64.exe](https://registry.npmmirror.com/-/binary/git-for-windows/v2.51.0.windows.1/Git-2.51.0-arm64.exe)

- **Mac**
Homebrew is required. If the user does not have it, help them install Homebrew first. In mainland China, use an appropriate mirror if needed for faster downloads.
After that, install Git with `brew install git`.

### Install OpenClaw

### 1. Install OpenClaw without configuring it yet

macOS
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

Windows
```powershell
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
```

### 2. Configure OpenClaw

#### Ask the user to choose a model provider and connect an API key

Use the following wording:

Now let's connect OpenClaw to a model provider. This is the underlying AI model that powers OpenClaw's responses.

1. Choose a model
  - MiniMax-M2.5 (recommended)
  - Other models (by OpenAI, Anthropic, Google Gemini, etc.)
2. Connect your API key
  1. MiniMax: Log in via OAuth (recommended) or enter an API key manually.
  2. Other models: Enter your API key directly.

China mainland: https://platform.minimaxi.com/subscribe/coding-plan
International: https://platform.minimax.io/docs/coding-plan/intro

About MiniMax Agent credits
MiniMax Agent is the interface that helps you install, configure, and troubleshoot OpenClaw. Agent credits are used for this setup assistance. They're separate from the API charges above.

### 3. Configure the model

**CRITICAL: When configuring the model, you MUST refer to the actual model names listed at [https://docs.openclaw.ai/providers](https://docs.openclaw.ai/providers). NEVER guess or fabricate model names. For MiniMax models specifically, check the official MiniMax platform for the latest available models:**
- **Mainland China: https://platform.minimaxi.com**
- **International: https://platform.minimax.io**

#### Configure MiniMax

If the user chooses a MiniMax model, OAuth mode can be used, but API key mode must also be supported. If using OAuth mode, which is the recommended option, run:

```bash
openclaw plugins enable minimax-portal-auth  # skip if already loaded.
openclaw gateway restart  # restart if gateway is already running
openclaw onboard --auth-choice minimax-portal
```

Step 1: On the disclaimer screen, instruct the user to use the left and right arrow keys to select `yes`, then press Enter.

Step 2: On the onboarding mode screen, guide the user to choose `QuickStart`, then press Enter.

Step 3: On the config handling screen, guide the user to choose `Use existing values`, then press Enter.

Step 4: Ask the user to choose the platform environment they purchased. For mainland China, choose `CN` (`api.minimaxi.com`). For outside mainland China, choose `Global` (`api.minimax.io`). Then press Enter.

Step 5: The user only needs to log in on the page that opens.

#### If using a MiniMax API key, or when configuring other models

Refer to [https://docs.openclaw.ai/providers](https://docs.openclaw.ai/providers) for the specific configuration method. **You MUST check the provider's documentation page to find the correct, currently available model names. Do NOT invent or assume model names from memory -- always verify against the official source.**

**Important:** MiniMax has different base URLs for mainland China and outside mainland China. The base URL depends on the environment, so you must confirm this with the user.

### 4. Configure the required skill
#### Install the clawhub CLI
```bash
npm i -g clawhub
```

#### Install the required skill

**CRITICAL: You MUST execute ALL of the following install commands. Do NOT skip any of them. After installation, verify each one completed successfully before proceeding to the next step.**

```bash
clawhub install mmxagent-guardian --force
clawhub install skill-scanner
clawhub install skill-guard
clawhub install prompt-injection-guard
```

**After running the above commands, confirm that all four skills were installed successfully by checking the command output. Do NOT proceed to the next step until all installations are confirmed.**

### 5. Configure other settings
#### Additional system settings
```bash
openclaw onboard --non-interactive --accept-risk --mode local  --gateway-port 18789 --gateway-bind loopback --install-daemon --skip-skills
```

#### Configure certain channels

Ask the user whether they need extra channel configuration. Officially supported channels are listed at:
https://docs.openclaw.ai/channels

Below are the setup guides for each supported channel. Only follow the relevant section based on the user's choice.

---

##### Feishu (飞书)

###### Install / Update the Feishu plugin

Install:
```bash
npx -y @larksuite/openclaw-lark install
```

Update:
```bash
npx -y @larksuite/openclaw-lark update
```

###### Installation walkthrough
During installation, the user scans a QR code in the Feishu client to create a Feishu bot automatically.

Important: the QR code is often printed in tool output, which the user may not be able to see directly. After running the install command, if a QR code or login payload is returned, you must surface it in the model response so the user can scan it.

If the installer prints an ASCII QR code, include that QR code directly in the model response inside a fenced code block. Do not leave it only in the tool output.

###### Post-install verification
1. After creation, click "Open Bot" and send any message to the bot in Feishu to start a conversation.
2. To quickly complete user authorization so that OpenClaw can perform tasks on your behalf (messages, docs, bitable, calendar, etc.), send `/feishu auth` in the Feishu conversation for batch authorization.
3. To let OpenClaw learn the new Feishu plugin capabilities, send "learn my newly installed Feishu plugin and list its abilities" in the Feishu conversation.
4. Verify installation: send `/feishu start` in the Feishu conversation. If a version number is returned, installation was successful.

###### Optional Feishu settings

After installation, ask the user if they want to enable these features:

**Streaming output** (explain what streaming output means to the user):
```bash
openclaw config set channels.feishu.streaming true   # enable
openclaw config set channels.feishu.streaming false  # disable
```

**Extra info in streaming mode:**
```bash
openclaw config set channels.feishu.footer.elapsed true  # show elapsed time
openclaw config set channels.feishu.footer.status true   # show status
```

**Thread session** (independent context per thread, supports parallel tasks -- explain to the user and warn about potential cost increase):
```bash
openclaw config set channels.feishu.threadSession true   # enable
openclaw config set channels.feishu.threadSession false  # disable
```

**Reply mode in groups:**

Mode 1: Only reply when @mentioned (most common)
```bash
openclaw config set channels.feishu.requireMention true --json
```

Example config:
```json
{
    "channels": {
        "feishu": {
            "enabled": true,
            "appId": "cli_YOUR_APP_ID",
            "appSecret": "YOUR_APP_SECRET",
            "requireMention": true,
            "groupPolicy": "open"
        }
    }
}
```

Mode 2: Reply to all messages without @mention
Requires extra permission in the developer console: `im:message.group_msg` (sensitive permission).
```bash
openclaw config set channels.feishu.requireMention false --json
```

Example config:
```json
{
    "channels": {
        "feishu": {
            "enabled": true,
            "appId": "cli_YOUR_APP_ID",
            "appSecret": "YOUR_APP_SECRET",
            "requireMention": "open",
            "groupPolicy": "open"
        }
    }
}
```

**Multi-bot (not recommended for most users):**
1. Create bots manually at: https://open.feishu.cn/page/openclaw?form=multiAgent
2. Configuration reference: https://bytedance.larkoffice.com/docx/WNNXdhKxmo8KDJxMM9dc0GD5nFf

Reference: https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh

---

##### DingTalk (钉钉)

###### Prerequisites
The user must have developer permissions for an organization, or obtain developer permissions from an organization admin.

###### 1. Create a DingTalk app and bot

**Create the app:**
1. Log in to the developer console: https://open-dev.dingtalk.com/
2. Click "Application Development" and then "Create Application".
3. Fill in the app name and description, then click Save.
4. In the app details page, under "Credentials & Basic Info", get the **Client ID** and **Client Secret**.

**Create the bot:**
1. Open the target app's details page.
2. In the left menu, select "Add App Capabilities" and add the bot capability.
3. Enable bot configuration, fill in the bot name and other required fields, then click Publish.

**Publish the app:**
1. Open the target app's details page.
2. Under "Permission Management", add these permissions: `Card.Streaming.Write`, `Card.Instance.Write`, `qyapi_robot_sendmsg`.
3. In the left menu, select "Version Management & Release" and create a new version.
4. Fill in the version number, description, and select the availability scope, then click Save.

**Configure AI Card (optional -- enhances streaming output):**
Explain what streaming output means to the user, then ask if they want to set this up now.
1. Visit the DingTalk Card Platform: https://open-dev.dingtalk.com/fe/card
2. Click "New Template".
3. Set card type to "Message Card", card template scenario to "AI Card", and associate the app created above. Click Create.
4. On the template editor page, do NOT use a preset template. Save and publish directly, then return to the template list.

###### 2. Install the DingTalk plugin
```bash
openclaw plugins install @dingtalk-real-ai/dingtalk-connector
```

###### 3. Configure openclaw.json

The config file is usually at `~/.openclaw/openclaw.json`. Add the following under `channels/dingtalk-connector`, `gateway/auth`, and `gateway/http/endpoints`:

```json
{
  "channels": {
    "dingtalk-connector": {
      "clientId": "DingTalk Client ID",
      "clientSecret": "DingTalk Client Secret",
      "gatewayToken": "Gateway auth token (value of gateway.auth.token in openclaw.json)",
      "gatewayPassword": "",
      "sessionTimeout": 1800000
    }
  },
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "Gateway auth token"
    },
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  }
}
```

**Important:** Only modify the fields shown above. Do not change other properties.

###### 4. Using the bot

**In group chats:**
1. Open a DingTalk group (the group's organization must match the bot's organization).
2. Go to Group Settings (top right) > Bots > Add Bot.
3. Search for and add the bot you created.
4. @mention the bot to trigger auto-replies.

**In direct messages:**
1. Search for the bot name in the top search bar.
2. Send a message to start a conversation.

###### DingTalk FAQ

**405 error:** Enable the `chatCompletions` endpoint in `~/.openclaw/openclaw.json`:
```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  }
}
```

**401 error:** Check that `gateway.auth.token` (or password) in `~/.openclaw/openclaw.json` is correct.

**Bot not responding:**
1. Confirm the gateway is running: `curl http://127.0.0.1:18789/health`
2. Confirm the bot is in Stream mode (not Webhook).
3. Confirm the Client ID / Client Secret are correct.

**AI Card not showing (plain text only):** Enable `Card.Streaming.Write` and `Card.Instance.Write` permissions and republish the app.

References:
- https://open.dingtalk.com/document/dingstart/build-dingtalk-ai-employees
- https://open.dingtalk.com/document/dingstart/install-openclaw-locally

---

##### WeCom (企业微信)

###### 1. Create a long-connection bot
1. In the WeCom client, go to Workbench > Smart Bot > Create Bot, and select API mode.
2. Choose the **long connection** method and obtain the **Bot ID** and **Secret**.

###### 2. Install the WeCom plugin
```bash
openclaw plugins install @wecom/wecom-openclaw-plugin
```

Restart the gateway:
```bash
openclaw gateway start
```

###### 3. Configure openclaw.json

Add the WeCom channel under `channels`:
```json
{
  "channels": {
    "wecom": {
      "enabled": true,
      "botId": "YOUR_BOT_ID",
      "secret": "YOUR_BOT_SECRET",
      "allowFrom": [],
      "dmPolicy": "pairing"
    }
  }
}
```

###### 4. Pair the bot
Save the bot in WeCom and send it a message. It will reply with a pairing code. Ask the user to share that message, then use the pairing code to complete the setup.

Reference: https://work.weixin.qq.com/nl/index/openclaw

### 6. Verify that configuration is complete

```bash
openclaw gateway restart
openclaw status
```

> **Important:** You must use Bash to run `openclaw gateway restart && openclaw dashboard --no-open` to open the control panel. **Do not** ask the user to directly visit `127.0.0.1:18789` or any IP address, or functionality may break.

**You must include the `--no-open` flag when running `openclaw dashboard`, because the dashboard will be opened elsewhere instead of in the default browser.**

## Verify Installation

After installation succeeds, you **must** help the user run `openclaw gateway restart && openclaw dashboard --no-open` to open the browser control panel. **Do not** ask the user to manually visit any IP address. The user can check the gateway status in the control panel and confirm that the configuration is correct.

## Common Commands

| Command | Description |
| -------------------------- | ------------- |
| `openclaw gateway status` | Check gateway status |
| `openclaw gateway run` | Start the gateway |
| `openclaw gateway stop` | Stop the gateway |
| `openclaw gateway restart` | Restart the gateway |

## Having Problems?

If you encounter any issue during installation, copy the full error message and send it to me, and I will help you troubleshoot it.

# OpenClaw Update and Maintenance

Use the `update` command to upgrade OpenClaw:

```bash
openclaw update
```

If the user wants to modify the OpenClaw configuration, including adding channels, changing API keys or models, or adding sub-agents, and any other change involving `openclaw.json`, explain to the user that these changes may cause `openclaw gateway` to fail to restart, which can make OpenClaw unavailable. Proceed carefully.

## Configuration Update Strategy

After updating the configuration, first run:

```bash
openclaw config validate
```

This checks whether the configuration file is valid.

Model changes and channel additions can follow the same process described above for OpenClaw installation.

If the user changes any model-related configuration, **you should ask the user for the model, API key, and base URL, then test the request with `curl`** to confirm that the endpoint works.

**Changes to gateway mode must be handled very carefully.** In general, users should not be encouraged to modify gateway settings. If they insist on changing them, explain the risks according to:
https://docs.openclaw.ai/gateway


