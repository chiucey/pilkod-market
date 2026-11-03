---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: cac4601892f59cb1ba0ef1228f556173
    PropagateID: cac4601892f59cb1ba0ef1228f556173
    ReservedCode1: 3046022100bde50fa74fc397b54f65f85cee48a8e04aac334bd488a34a913a3b2dc37d182f022100cd5182a375e0a7d5da6e87e92f129280c973081ed8027c26cc5413fd071ae7a0
    ReservedCode2: 30450221008a883d5e390588cec01ca33ee30d4ba9f31cd566053842bc9a0f6670fbb4cbd40220404403a1b629f2c8830322a1e9592f5a3c5e5478bd466371720512ca0c1b87c5
description: 将 MiniMax API 配置到编程工具中。当用户询问如何配置 MiniMax API 到 Claude Code、VSCode Cline、Cursor、Trae、CodeX 等编程工具时使用。
name: minimax-api-config
---

# MiniMax API 编程工具配置指南

本文档详细说明如何将 MiniMax API 配置到各种主流编程工具中，包括 Claude Code、VSCode Cline、Cursor IDE 和 Trae IDE。

## 目录

- [一、MiniMax API 基础准备](#一minimax-api-基础准备)
- [二、Claude Code 配置](#二claude-code-配置)
- [三、VSCode Cline 配置](#三vscode-cline-配置)
- [四、Cursor IDE 配置](#四cursor-ide-配置)
- [五、Trae IDE 配置](#五trae-ide-配置)
- [六、CodeX 配置](#六codex-配置)
- [七、故障排除](#七故障排除)

---

## 一、MiniMax API 基础准备

### 1.1 获取 MiniMax API Key

1. **访问 MiniMax 开放平台**：打开浏览器访问 [MiniMax 开放平台](https://platform.minimaxi.com/) <citation>1</citation>
2. **注册账号**：点击右上角「注册」按钮，使用邮箱完成账户创建
3. **开通订阅计划**：根据需求选择 Coding Plan 或 Token Plan
4. **创建 API Key**：
   - 进入「API Keys」页面
   - 点击「创建新的密钥」
   - 填写密钥名称（如 "Claude-Code-Config"）
   - 点击「Copy」复制生成的密钥 <citation>2</citation>

### 1.2 MiniMax API 端点信息

| 区域 | Base URL | 说明 |
|------|----------|------|
| 国际用户 | `https://api.minimax.io/v1` | 适用于中国境外用户 |
| 中国用户 | `https://api.minimax.chat/v1` | 适用于中国境内用户 <citation>181</citation> |

### 1.3 支持的编程模型

| 模型名称 | 适用场景 | 上下文长度 |
|----------|----------|------------|
| MiniMax-M2.7 | 高性能编程、复杂任务 | 1000k tokens |
| MiniMax-M2.5 | 通用编程、日常开发 | 1000k tokens |
| MiniMax-M2 | 高效编码、Agent 工作流 | 245k tokens |
| MiniMax-M2.1 | 多语言编程、代码工程 | 245k tokens |

---

## 二、Claude Code 配置

Claude Code 是 Anthropic 官方推出的终端编程助手，支持通过第三方 API 配置 MiniMax 模型 <citation>14</citation>。

### 2.1 安装 Claude Code

**Windows（PowerShell）** <citation>58</citation>：

```powershell
irm https://claude.ai/install.ps1 | iex
```

**macOS / Linux**：

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 2.2 配置 MiniMax API（推荐使用 cc-switch）

cc-switch 是一个便捷的切换工具，支持管理和切换 Claude Code 供应商配置 <citation>142</citation>。

#### 安装 cc-switch

**Windows**：

- 前往 [GitHub Releases](https://github.com/farion1231/cc-switch) 下载安装包

**macOS/Linux**：

```bash
brew tap farion1231/ccswitch
brew install --cask cc-switch
brew upgrade --cask cc-switch
```

#### 配置步骤

1. 启动 cc-switch，点击右上角 **「+」**
2. 选择 **MiniMax** 供应商
3. 填入你的 MiniMax API Key
4. 将模型名称设置为 `MiniMax-M2.7`（或 `MiniMax-M2.5`）
5. 点击右下角 **「添加」**
6. 回到首页，点击 **「启用」** <citation>58</citation>

### 2.3 手动配置（备选方案）

#### 方法一：编辑配置文件

编辑 `~/.claude/settings.json` 文件，添加以下内容：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimax.chat/v1",
    "ANTHROPIC_AUTH_TOKEN": "你的MiniMax-API-Key",
    "ANTHROPIC_MODEL": "MiniMax-M2.7"
  }
}
```

> **注意**：如果是国际版 API，使用 `https://api.minimax.io/v1` <citation>181</citation>

#### 方法二：设置环境变量

**Windows PowerShell**：

```powershell
$env:ANTHROPIC_BASE_URL = "https://api.minimax.chat/v1"
$env:ANTHROPIC_AUTH_TOKEN = "你的MiniMax-API-Key"
$env:ANTHROPIC_MODEL = "MiniMax-M2.7"
```

**macOS / Linux**：

```bash
export ANTHROPIC_BASE_URL="https://api.minimax.chat/v1"
export ANTHROPIC_AUTH_TOKEN="你的MiniMax-API-Key"
export ANTHROPIC_MODEL="MiniMax-M2.7"
```

#### 绕过登录配置

编辑 `~/.claude.json`（Windows 为 `用户目录/.claude.json`），添加以下内容防止 Claude Code 弹出登录选项 <citation>58</citation>：

```json
{
  "hasCompletedOnboarding": true
}
```

### 2.4 启动 Claude Code

```bash
# 进入工作目录
cd 你的项目目录

# 启动 Claude Code
claude
```

启动后选择 **「信任此文件夹 (Trust This Folder)」**，即可开始使用。

---

## 三、VSCode Cline 配置

Cline 是 VSCode 上强大的 AI 辅助编程插件，支持接入多种 AI 模型的 API <citation>21</citation>。

### 3.1 安装 Cline

1. 打开 VSCode，进入扩展商店（`Ctrl+Shift+X`）
2. 搜索 **"Cline"** 并安装
3. 安装完成后，左侧活动栏会出现机器人图标 <citation>25</citation>

### 3.2 配置 MiniMax API

1. 点击左侧 Cline 图标
2. 点击右上角齿轮进入 **设置**
3. 选择 **API Provider** 为 **"OpenAI Compatible"**
4. 配置以下参数：

| 参数 | 值 |
|------|-----|
| Base URL | `https://api.minimax.chat/v1`（中国）或 `https://api.minimax.io/v1`（国际） |
| API Key | 你的 MiniMax API Key |
| Model ID | `MiniMax-M2.7` 或 `MiniMax-M2.5` |

5. 保存设置 <citation>22</citation>

### 3.3 配置示例代码

如果需要通过 `settings.json` 手动配置，打开 `.vscode/settings.json`：

```json
{
  "cline.apiProvider": "openai-compatible",
  "cline.openAiBaseUrl": "https://api.minimax.chat/v1",
  "cline.apiKey": "你的MiniMax-API-Key",
  "cline.modelId": "MiniMax-M2.7"
}
```

---

## 四、Cursor IDE 配置

Cursor IDE 原生支持 OpenAI 兼容接口，可通过配置自定义 API 使用 MiniMax 模型 <citation>52</citation>。

### 4.1 基础配置步骤

1. 打开 Cursor 设置（左侧齿轮图标）
2. 切换到 **Models** 选项卡
3. 找到 **"OpenAI API Key"** 部分
4. 启用自定义开关（绿色按钮）
5. 粘贴你的 MiniMax API Key
6. 展开 **"Override OpenAI Base URL"**
7. 输入 Base URL：`https://api.minimax.chat/v1`（中国）或 `https://api.minimax.io/v1`（国际）
8. 在模型列表中添加自定义模型名称：`MiniMax-M2.7` 或 `MiniMax-M2.5`
9. 保存设置 <citation>52</citation>

### 4.2 注意事项

> **重要限制**：最新版本的 Cursor 中，Agent Composer 模式**仅支持**以下模型：
> - Anthropic 官方模型
> - GPT-4o
> - o3-mini
>
> 如需使用 MiniMax 模型，请使用 Chat 模式或普通 Composer 模式 <citation>52</citation>

### 4.3 使用硅基流动平台（备选）

硅基流动平台提供大量国产模型，兼容 OpenAI 格式 <citation>59</citation>：

1. 注册 [硅基流动平台](https://api.siliconflow.cn)
2. 获取模型 ID
3. 在 Cursor 中配置：

| 参数 | 值 |
|------|-----|
| Base URL | `https://api.siliconflow.cn/v1` |
| API Key | 平台 API Key |
| Model ID | 对应的模型 ID |

---

## 五、Trae IDE 配置

Trae 是字节跳动推出的 AI 驱动集成开发环境，支持通过 Cline 插件配置 MiniMax API <citation>35</citation>。

### 5.1 安装 Trae IDE

访问官网下载对应操作系统版本：

- 国内版：https://www.trae.com.cn/
- 国际版：https://www.trae.ai/ <citation>32</citation>

### 5.2 初始配置

1. **选择语言和主题**：中文/英文，暗色/亮色/深蓝
2. **导入现有设置（可选）**：可一键从 VS Code 导入插件、IDE 设置、快捷键等
3. **添加命令行（可选）**：点击「安装 trae 命令」 <citation>35</citation>

### 5.3 安装 Cline 插件

1. 在 Trae 扩展商店搜索 **"Cline"** 进行安装
2. 安装完成后会在侧边栏出现小机器人图标

### 5.4 配置 MiniMax API

1. 打开 Cline 应用
2. 勾选 **「Bring my own API Key」**
3. 填写配置信息：

| 参数 | 值 |
|------|-----|
| API Provider | OpenAI Compatible |
| Base URL | `https://api.minimax.chat/v1` |
| API Key | 你的 MiniMax API Key |
| Model ID | `MiniMax-M2.7` |

4. 保存后测试回复 <citation>35</citation>

### 5.5 配置 Claude Code（可选）

如需使用 Claude 模型，还需额外安装 Claude Code：

```powershell
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 配置环境变量
[Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", "API密钥", "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "平台地址", "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL", "默认模型", "User")
```

然后在 Trae 扩展商店搜索 **"Claude Code for VS Code"** 下载安装 <citation>35</citation>。

---

## 六、CodeX 配置

CodeX 是 OpenAI 推出的 AI 编程工具，支持通过自定义 Provider 配置接入 MiniMax API <citation>11</citation>。

### 6.1 安装 CodeX CLI

**通过 npm 全局安装**：

```bash
npm install -g @openai/codex
```

**验证安装**：

```bash
codex --version
```

### 6.2 MiniMax 官方配置指南

MiniMax 开放平台提供了 CodeX 集成的官方文档支持 <citation>21</citation>：

1. 访问 [MiniMax API 文档 - M2.7 for AI Coding Tools](https://platform.minimaxi.io/docs/guides/text-ai-coding-tools)
2. 获取配置所需的 API Key 和 Base URL

### 6.3 配置 MiniMax Provider

CodeX 支持通过自定义 Provider 机制接入 MiniMax API，编辑 `~/.codex/config.toml` 文件 <citation>27</citation> <citation>29</citation>：

```toml
model_provider = "minimax"

[model_providers.minimax]
name = "MiniMax"
base_url = "https://api.minimax.chat/v1"
wire_api = "chat"  # 或 "responses"（需要 codex >= 0.81.0）
```

### 6.4 使用环境变量配置

也可以通过环境变量配置 MiniMax API <citation>21</citation>：

```bash
export OPENAI_API_KEY="你的MiniMax-API-Key"
export OPENAI_BASE_URL="https://api.minimax.chat/v1"
```

**注意**：
- 国际用户请使用 `https://api.minimax.io/v1`
- 中国用户请使用 `https://api.minimax.chat/v1`

### 6.5 配置自定义模型

如果需要使用特定的 MiniMax 模型，可以在配置中指定：

```toml
model = "MiniMax-M2.7"

[model_providers.minimax]
name = "MiniMax"
base_url = "https://api.minimax.chat/v1"
wire_api = "responses"
```

### 6.6 通过第三方中转平台配置

如果直接使用 MiniMax API 不稳定，可以使用第三方中转平台 <citation>3</citation>：

```toml
model_provider = "32ai"

[model_providers.32ai]
name = "32ai 中转"
base_url = "https://api.32zi.com/v1"
wire_api = "responses"
```

### 6.7 VSCode Codex 插件配置

如果使用 VSCode Codex 插件，按以下步骤配置 <citation>23</citation> <citation>25</citation>：

1. 退出 VSCode
2. 编辑 `~/.codex/config.toml` 文件
3. 添加 MiniMax Provider 配置：

```toml
model_provider = "minimax"

[model_providers.minimax]
name = "MiniMax API"
base_url = "https://api.minimax.chat/v1"
wire_api = "responses"

[model_providers.minimax.headers]
Authorization = "Bearer 你的MiniMax-API-Key"
```

4. 重启 VSCode

---

## 七、故障排除

### 7.1 常见问题

| 问题 | 解决方案 |
|------|----------|
| 配置后无法连接 | 检查 API Key 是否正确、Base URL 是否准确、网络连接是否正常、账户余额是否充足 <citation>52</citation> |
| 响应速度慢 | 检查网络状态、选择更快的模型、优化提示词长度 |
| 提示超出调用限额 | MiniMax Coding Plan 按 5 小时滚动 prompt 数计费，等待当前窗口自然滚动结束 <citation>153</citation> |

### 7.2 网络代理配置（可选）

如需登录 Claude 账号或访问受阻，可配置代理：

**Windows CMD**：

```cmd
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897
```

**Windows PowerShell**：

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
```

**macOS / Linux**：

```bash
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
```

> 端口号通常为 7897 或 7890，根据你的代理软件配置 <citation>58</citation>

### 7.3 MiniMax Coding Plan 计费说明

| 套餐 | 价格 | 额度 |
|------|------|------|
| Starter | $10/月 | 500 requests/5hrs |
| Plus | $20/月 | 4,500 requests/5hrs |
| Max | $50/月 | 15,000 requests/5hrs |

> 注意：不同模型消耗的请求数可能不同，如 MiniMax-M2.5 速度更快、性价比更高 <citation>160</citation>

---

## 参考来源

- [MiniMax 开放平台](https://platform.minimaxi.com/)
- [MiniMax API 文档 - OpenAI 兼容接口](https://platform.minimaxi.io/docs/api-reference/text-openai-api)
- [MiniMax M2.7 for AI Coding Tools](https://platform.minimaxi.io/docs/guides/text-ai-coding-tools)
- [国内使用 Claude Code 保姆级教程](https://blog.csdn.net/Zhangws0107/article/details/159246507)
- [cc-switch GitHub](https://github.com/farion1231/cc-switch)
- [Trae AI 使用第三方 API 配置教程](https://blog.csdn.net/weixin_53403266/article/details/159765500)
- [Cursor 配置 API 教程](https://grapecity.csdn.net/68633e0da6db534ba2b5100d.html)
- [CodeX 自定义 API 配置教程](https://www.cnblogs.com/smileZAZ/p/19406570)
- [CodeX Advanced Configuration](https://developers.openai.com/codex/config-advanced)
- [VSCode Codex 插件 API Key 配置](https://community.openai.com/t/vscode-extension-with-api-key/1355263)
