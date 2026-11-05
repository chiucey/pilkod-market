# OpenRouter 免费模型参考列表

> 数据更新时间：2024年，请以实际 API 返回为准

## 高质量免费模型（Quality Score ≥ 0.9）

| 模型 ID | 提供商 | 上下文长度 | 速率限制 (RPM) | 推荐场景 |
|---------|--------|------------|----------------|----------|
| anthropic/claude-3-haiku | Anthropic | 200K | 50 | 快速任务、日常对话 |
| google/gemini-pro | Google | 128K | 60 | 通用推理、代码 |
| google/gemini-flash | Google | 1M | 60 | 长文本处理 |
| openai/gpt-3.5-turbo | OpenAI | 16K | 200 | 通用对话 |
| mistralai/mistral-7b-instruct | Mistral | 8K | 30 | 指令遵循 |

## 中等质量模型（Quality Score 0.7-0.9）

| 模型 ID | 提供商 | 上下文长度 | 速率限制 (RPM) | 推荐场景 |
|---------|--------|------------|----------------|----------|
| meta-llama/llama-3-8b-instruct | Meta | 8K | 100 | 开源社区 |
|NousResearch/hermes-3-llama-3.1-8b | Nous | 128K | 50 | 长文本分析 |
| deepseek/deepseek-chat | DeepSeek | 32K | 60 | 中文场景 |
| anthropic/claude-3-sonnet | Anthropic | 200K | 40 | 复杂推理 |

## 特殊用途模型

| 模型 ID | 用途 | 限制 |
|---------|------|------|
| openrouter/auto | 智能路由 | 自动选择最佳模型 |
| openrouter/minimax | 免费积分优化 | 节省用量 |

## 模型选择策略

### 推荐配置（通用场景）

```yaml
primary: "anthropic/claude-3-haiku"
fallback:
  - "openrouter/auto"
  - "google/gemini-pro"
  - "google/gemini-flash"
  - "openai/gpt-3.5-turbo"
  - "meta-llama/llama-3-8b-instruct"
```

### 推荐配置（中文场景）

```yaml
primary: "deepseek/deepseek-chat"
fallback:
  - "openrouter/auto"
  - "google/gemini-pro"
  - "anthropic/claude-3-haiku"
  - "openai/gpt-3.5-turbo"
  - "meta-llama/llama-3-8b-instruct"
```

### 推荐配置（长文本场景）

```yaml
primary: "google/gemini-flash"
fallback:
  - "openrouter/auto"
  - "NousResearch/hermes-3-llama-3.1-8b"
  - "anthropic/claude-3-haiku"
  - "google/gemini-pro"
  - "deepseek/deepseek-chat"
```

## 速率限制注意事项

1. **OpenRouter 免费层限制**：
   - 通常 100 RPM 或更低
   - 具体取决于模型和账户状态

2. **Fallback 触发条件**：
   - 当主模型返回 429 错误
   - 当连续 3 次请求超时

3. **智能路由 (openrouter/auto)**：
   - 自动选择当前负载最低的模型
   - 推荐作为首个 fallback
