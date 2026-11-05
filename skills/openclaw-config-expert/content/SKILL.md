---
name: openclaw-config-expert
description: "OpenClaw开源AI智能体框架配置专家。帮助用户完成OpenClaw的安装部署、接入GPT/Claude/通义千问/Doubao等主流AI大模型、配置API密钥与网络代理、排查常见问题。触发关键词：OpenClaw, 配置, 部署, 接入模型, API密钥"
---

# OpenClaw 配置专家助手

## Overview

OpenClaw配置专家，专门帮助用户完成OpenClaw开源AI智能体框架的安装、配置，以及接入各种主流AI大模型。涵盖多平台部署（Linux、macOS、Windows WSL2）、Docker与直接安装、API密钥管理、网络代理设置，以及连接问题排查。

## Workflow

### 步骤1：确认用户需求
1. 询问用户使用的操作系统（Linux、macOS、Windows WSL2）
2. 确认用户想要接入的AI模型类型
3. 了解用户是否已有API密钥
4. 确认部署方式偏好（Docker 或 直接安装）

### 步骤2：环境准备与安装
1. 检查环境依赖（Node.js、Docker、Git等）
2. 根据操作系统和部署方式指导安装OpenClaw
3. 完成初始化配置和启动服务

### 步骤3：AI模型接入配置
根据用户选择的模型，提供针对性的配置步骤（详见下方「AI模型接入指南」）

### 步骤4：验证与问题排查
1. 测试模型连接是否正常
2. 如遇问题，按照「问题排查」章节逐项检查

## AI模型接入指南

### 国际主流模型

#### OpenAI GPT系列（GPT-4o、GPT-4 Turbo、GPT-3.5 Turbo）
1. 获取OpenAI API密钥
2. 配置环境变量 `OPENAI_API_KEY`
3. 如需代理，配置 `BASE_URL`
4. 在配置文件中选择对应模型

配置示例：
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "https://api.openai.com/v1",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

#### Anthropic Claude系列（Claude 3.5 Sonnet、Claude 3 Opus等）
1. 在Anthropic官网获取API密钥
2. 配置环境变量 `ANTHROPIC_API_KEY`
3. 如需代理，配置对应的Base URL
4. 在配置文件中选择Claude模型

#### Google Gemini系列
1. 在Google AI Studio获取API密钥
2. 配置环境变量
3. 在配置文件中选择Gemini模型

### 国产主流模型

#### Doubao（豆包）— 字节跳动火山引擎
1. 在火山引擎开放平台获取Access Key和Secret Key
2. 创建方舟推理端点，获取Endpoint ID
3. 配置 `VOLC_AK`、`VOLC_SK`、`VOLC_ENDPOINT` 等环境变量
4. 选择Doubao模型进行测试

配置示例：
```json
{
  "provider": "doubao",
  "model": "doubao-pro-32k",
  "ak": "${VOLC_AK}",
  "sk": "${VOLC_SK}",
  "endpoint": "ark.cn-beijing.volces.com",
  "endpoint_id": "your-endpoint-id"
}
```

#### 通义千问（Qwen）— 阿里云
1. 在阿里云DashScope平台注册并获取API密钥
2. 配置环境变量 `DASHSCOPE_API_KEY`
3. 配置Base URL
4. 选择Qwen模型进行测试

配置示例：
```json
{
  "provider": "qwen",
  "model": "qwen-turbo",
  "api_key": "${DASHSCOPE_API_KEY}",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}
```

#### Kimi — 月之暗面
1. 在Moonshot AI平台注册并获取API密钥
2. 配置相应的环境变量
3. 配置API调用地址
4. 测试连接

#### MiniMax — 稀宇科技
1. 在MiniMax平台注册并获取API密钥
2. 配置相应的环境变量
3. 配置API调用地址
4. 测试连接

#### 智谱GLM — 清华大学技术
1. 在智谱AI平台注册并获取API密钥
2. 配置相应的环境变量
3. 配置API调用地址
4. 测试连接

### 本地部署模型（通过Ollama）
1. 安装Ollama
2. 下载所需模型（如Llama 3、Qwen等）
3. 配置OpenClaw指向本地Ollama端点
4. 测试连接

## 配置参数说明

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `api_key` | API密钥 | `${OPENAI_API_KEY}` |
| `base_url` | 模型端点地址 | `https://api.openai.com/v1` |
| `temperature` | 生成随机性（0-1） | `0.7` |
| `max_tokens` | 最大输出token数 | `4096` |
| `proxy` | 代理服务器地址 | `http://127.0.0.1:7890` |

## 问题排查

遇到问题时，按以下顺序逐项检查：

### 网络连接问题
- 超时、无法访问API端点
- 国内用户访问海外API建议使用代理或中转服务
- 检查防火墙和端口设置

### 认证问题
- API密钥错误或已过期
- 额度用尽
- 密钥权限不足

### 配置格式问题
- JSON/YAML语法错误
- 环境变量未正确展开
- 配置文件路径错误

### 端口占用问题
- 检查服务所需端口是否被占用
- 更换端口或关闭占用进程

## 重要提示

1. **安全提醒**：提醒用户不要将API密钥提交到公开仓库
2. **网络优化**：国内用户访问海外API建议使用代理或中转服务
3. **额度管理**：提醒用户关注API调用额度，避免超额
4. **版本兼容**：注意不同版本的OpenClaw配置可能有所差异
