---
name: openclaw-local-setup
description: 本地配置 OpenClaw 的完整指南。当用户需要：（1）在本地电脑（Windows）安装和配置 OpenClaw；（2）配置 API（如 MiniMax、SiliconFlow、Ollama）；（3）配置飞书等频道；（4）了解 OpenClaw 的 models provider 配置时触发此技能。提供从零开始搭建 OpenClaw 完整开发环境的步骤、配置模板和最佳实践。
---

# OpenClaw 本地配置指南

本 skill 指导你在本地电脑（Windows）上从零配置 OpenClaw。

## 目标设备参考

- **设备**：DESKTOP-5AA5T99（AMD Ryzen 7 7800X3D + RTX 3070 8GB + 32GB RAM）
- **操作系统**：Windows 64位
- **目标**：配置 OpenClaw + 飞书频道 + 本地/云端模型

---

## 配置步骤总览

```
第一步 → 安装 OpenClaw
第二步 → 配置模型 Provider（API）
第三步 → 配置飞书频道
第四步 → 验证运行
```

---

## 第一步：安装 OpenClaw（Windows）

### 方式 A：直接下载（推荐）

```powershell
# 在 PowerShell 或 CMD 中运行
# 下载最新版本的 OpenClaw 安装包
irm https://github.com/openclaw/openclaw/releases/latest/download/openclaw-windows-x64.zip -o openclaw.zip

# 解压到指定目录（建议 C:\Tools\OpenClaw）
Expand-Archive openclaw.zip C:\Tools\OpenClaw

# 进入目录
cd C:\Tools\OpenClaw

# 验证安装
.\openclaw.exe --version
```

### 方式 B：npm 全局安装（需要 Node.js）

```powershell
npm install -g openclaw
```

### 方式 C：Docker 方式

```powershell
docker pull openclaw/openclaw
docker run -v $env:USERPROFILE\.openclaw:/root/.openclaw openclaw/openclaw
```

---

## 第二步：配置模型 Provider

配置文件路径：`~/.openclaw/openclaw.json`

### 推荐 Provider 1：MiniMax（性价比首选）

注册地址：https://platform.minimaxi.com

```json5
{
  "models": {
    "providers": {
      "minimax": {
        "provider": "minimax",
        "apiKey": "your-minimax-api-key",
        "model": "abab6.5s-chat"
      }
    }
  }
}
```

### 推荐 Provider 2：硅基流动（聚合多家模型，国内直连）

注册地址：https://siliconflow.cn

```json5
{
  "models": {
    "providers": {
      "siliconflow": {
        "provider": "openai",
        "apiBase": "https://api.siliconflow.cn/v1",
        "apiKey": "your-siliconflow-api-key",
        "model": "deepseek-ai/DeepSeek-V2.5"
      }
    }
  }
}
```

### 推荐 Provider 3：Anthropic Claude（最强推理）

注册地址：https://console.anthropic.com

```json5
{
  "models": {
    "providers": {
      "claude": {
        "provider": "anthropic",
        "apiKey": "your-anthropic-api-key",
        "model": "claude-sonnet-4-20250514"
      }
    }
  }
}
```

### 推荐 Provider 4：Ollama 本地（你的 RTX 3070 专用）

安装地址：https://ollama.com

**安装模型（PowerShell）：**

```powershell
# 安装 Ollama 后，在终端运行
ollama pull qwen2.5:7b        # 推荐中文模型
ollama pull deepseek-r1:7b    # 推理能力强
ollama pull codellama:7b      # 代码专用

# 验证模型列表
ollama list
```

**OpenClaw 配置：**

```json5
{
  "models": {
    "providers": {
      "ollama-local": {
        "provider": "openai",
        "apiBase": "http://localhost:11434/v1",
        "model": "qwen2.5:7b"
      }
    }
  }
}
```

---

## 第三步：配置飞书频道

> 前提：已有飞书自建应用（App ID + App Secret）

### 飞书应用创建流程

1. 打开 [飞书开放平台](https://open.feishu.cn/app)，创建企业自建应用
2. 在「凭证与基础信息」复制 **App ID** 和 **App Secret**
3. 配置权限（批量导入 JSON）
4. 开启「机器人」能力
5. 事件订阅选择「**长连接接收事件**」，添加 `im.message.receive_v1`
6. 发布应用

### OpenClaw 飞书配置

```json5
{
  "channels": {
    "feishu": {
      "enabled": true,
      "dmPolicy": "pairing",
      "accounts": {
        "main": {
          "appId": "cli_xxxxxxxx",
          "appSecret": "xxxxxxxx"
        }
      }
    }
  }
}
```

### 配对授权

应用启动后，在飞书给机器人发消息，会收到配对码，然后在终端运行：

```powershell
openclaw pairing approve feishu <配对码>
```

---

## 第四步：验证运行

```powershell
# 启动网关
.\openclaw.exe gateway start

# 查看状态
.\openclaw.exe gateway status

# 查看日志
.\openclaw.exe logs --follow
```

---

## 完整配置模板

将以下内容写入 `~/.openclaw/openclaw.json`：

```json5
{
  // 模型配置（选择一个或多个）
  "models": {
    "providers": {
      // 方案1：MiniMax
      "minimax": {
        "provider": "minimax",
        "apiKey": "your-key",
        "model": "abab6.5s-chat"
      },
      // 方案2：硅基流动（DeepSeek / Claude）
      "siliconflow": {
        "provider": "openai",
        "apiBase": "https://api.siliconflow.cn/v1",
        "apiKey": "your-key",
        "model": "deepseek-ai/DeepSeek-V2.5"
      },
      // 方案3：本地 Ollama
      "ollama": {
        "provider": "openai",
        "apiBase": "http://localhost:11434/v1",
        "model": "qwen2.5:7b"
      }
    },
    "default": "minimax"
  },

  // 飞书频道配置
  "channels": {
    "feishu": {
      "enabled": true,
      "dmPolicy": "pairing",
      "accounts": {
        "main": {
          "appId": "cli_xxxxxxxx",
          "appSecret": "xxxxxxxx"
        }
      }
    }
  }
}
```

---

## 常见问题

**Q：Ollama 模型很慢怎么办？**
A：RTX 3070 8GB 跑 7B 模型是流畅的。如果卡顿，检查是否显存被占满（运行 `nvidia-smi`）；建议只跑一个模型。

**Q：飞书连接不上？**
A：确认：① 应用已发布 ② 事件订阅已开启长连接 ③ 配对码已授权

**Q：如何切换不同模型？**
A：在 OpenClaw 配置多个 provider，通过 `model` 字段指定使用哪个。

详见参考文档：
- [models 配置详解](references/models-config.md)
- [channels 配置详解](references/channels-config.md)
