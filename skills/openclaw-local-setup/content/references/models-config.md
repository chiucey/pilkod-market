# Models Provider 配置参考

## 支持的 Provider 类型

| Provider | 说明 | 注册地址 |
|----------|------|---------|
| `minimax` | MiniMax API | https://platform.minimaxi.com |
| `anthropic` | Anthropic Claude 系列 | https://console.anthropic.com |
| `openai` | OpenAI GPT 系列 | https://platform.openai.com |
| `openai-like` | 兼容 OpenAI API 的第三方 | 自定义 |
| `ollama` | 本地 Ollama | https://ollama.com |

---

## Provider 配置示例

### MiniMax

```json5
{
  "provider": "minimax",
  "apiKey": "your-api-key",
  "model": "abab6.5s-chat"
}
```

### Anthropic Claude

```json5
{
  "provider": "anthropic",
  "apiKey": "your-api-key",
  "model": "claude-sonnet-4-20250514"
}
```

### OpenAI 兼容（硅基流动等）

```json5
{
  "provider": "openai",
  "apiBase": "https://api.siliconflow.cn/v1",
  "apiKey": "your-api-key",
  "model": "deepseek-ai/DeepSeek-V2.5"
}
```

### Ollama 本地

```json5
{
  "provider": "openai",
  "apiBase": "http://localhost:11434/v1",
  "model": "qwen2.5:7b"
}
```

---

## 模型推荐（按场景）

| 场景 | 推荐模型 | Provider |
|------|---------|---------|
| 日常助手 | MiniMax / Qwen2.5 | 云端 |
| 逻辑推理 | DeepSeek-R1 / Claude | 云端 |
| 代码生成 | Codellama / GPT-4o | 云端或 Ollama |
| 中文对话 | Qwen2.5 / DeepSeek | 任意 |
| 隐私对话 | Ollama (本地) | 本地 |
| 性价比首选 | 硅基流动 + DeepSeek | 云端 |

---

## RTX 3070 8GB 模型推荐

可流畅运行：
- `qwen2.5:7b` — 中文强，推荐
- `deepseek-r1:7b` — 推理强
- `llama3:8b` — 英文全能
- `codellama:7b` — 代码专用

显存上限：7B 模型约需 6-8GB 显存，14B 模型需要 12GB+，8GB 显存跑 14B 会分页到内存，较慢。

---

## 多模型切换

在 `models.providers` 下定义多个后，可在对话中指定使用哪个模型，或设置 `default` 指定默认模型。
