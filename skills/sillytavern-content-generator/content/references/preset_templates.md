---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7a293914a85e1ed2775fc30e3c42789a
    PropagateID: 7a293914a85e1ed2775fc30e3c42789a
    ReservedCode1: 3045022014491af3f82db384cd8ee4dceeb28747582477ea2c2f1893cb80f5a510cc00e7022100ffce905464b94d80dc95ee9b3dc80a384ef44d4c30ba0bc98ec122864e01c646
    ReservedCode2: 304402206602847ff1dd3b010fd5f9ba237428ef58ef2bdb86b07c080f9d890967528b2d022078006f6f2c940070942ac04a8d64f61c05bd35473c3fb8fc03352fa9f79bbe6c
---

# 预设模板参考

## 概述

预设（Presets）用于存储 SillyTavern/TavernAI 的对话配置，包括系统提示词、生成参数、指令设置等。通过预设，用户可以快速切换不同的对话模式和风格。

## 预设结构

```typescript
type Preset = {
  name: string              // 预设名称
  description?: string      // 预设描述
  prompt: string            // 主提示词（system prompt）
  prompt_depth?: number     // 提示词深度
  bias?: object            // 词汇偏差
  order: Array<string>      // 提示词顺序
  use_name_prompt?: boolean // 是否使用名称提示
  continue": boolean       // 是否启用 continue 功能
  delay_prompt?: number    // 延迟提示（毫秒）
  injection_depth?: number  // 注入深度
  name: string             // 用户名
  context: string          // 上下文设置
  greeting?: string        // 开场白
  sample_multi: string     // 示例多重选择
  cyphers: string          // 加密设置
  chat_completion_mode?: boolean // 聊天补全模式
  dynamic_temp?: boolean   // 动态温度
  dynamic_temp_min?: number // 动态温度最小值
  dynamic_temp_max?: number // 动态温度最大值
  dynamic_temp_var?: number // 动态温度变化
  max_context: number      // 最大上下文
  max_response: number     // max_response_length
  repetition_penalty?: number // 重复惩罚
  repetition_penalty_range?: number // 重复惩罚范围
  repetition_penalty_slope?: number // 重复惩罚斜率
  repetition_penalty_frequency?: number // 重复惩罚频率
  response_temp?: number   // 响应温度
  response_top_p?: number  // 响应 top_p
  response_top_k?: number  // 响应 top_k
  response_min_p?: number  // 响应 min_p
  response_epsilon_cutoff?: number // 响应 epsilon_cutoff
  response_tfs?: number    // 响应 tfs
  response_top_a?: number  // 响应 top_a
  response_mirostat?: number // Mirostat 模式
  response_mirostat_tau?: number // Mirostat tau
  response_mirostat_eta?: number // Mirostat eta
  banned_tokens?: Array<string> // 禁用 token
  frequency_penalty?: number  // 频率惩罚
  cache_prompt?: boolean     // 缓存提示
  images?: boolean           // 图像支持
  image_style?: string       // 图像风格
  voice?: string             // 语音设置
  arrival_bias?: boolean     // 到达偏差
}
```

## 常用预设模板

### 1. 角色扮演模式

```json
{
  "name": "角色扮演",
  "description": "沉浸式角色扮演，适合故事创作",
  "prompt": "{{original}}",
  "prompt_depth": 0,
  "order": ["prompt", "context", "syrup"],
  "continue": false,
  "injection_depth": 2,
  "name": "User",
  "context": "你是一个故事叙述者，专注于创造引人入胜的角色扮演体验。",
  "sample_multi": "Quality character roleplay is detailed, immersive, and stays true to established character traits.",
  "chat_completion_mode": false,
  "max_context": 8192,
  "max_response": 512,
  "response_temp": 0.9,
  "response_top_p": 0.9
}
```

### 2. 创意写作模式

```json
{
  "name": "创意写作",
  "description": "长篇故事创作，优化叙事流畅性",
  "prompt": "{{original}}",
  "prompt_depth": 0,
  "order": ["prompt", "context"],
  "continue": true,
  "injection_depth": 4,
  "name": "Writer",
  "context": "你是一位专业的小说家，擅长创作生动、详细的叙事内容。",
  "sample_multi": "Creative writing should be descriptive, engaging, and maintain narrative flow.",
  "chat_completion_mode": false,
  "max_context": 16384,
  "max_response": 1024,
  "repetition_penalty": 1.1,
  "response_temp": 1.0,
  "response_top_p": 0.95
}
```

### 3. 对话聊天模式

```json
{
  "name": "轻松聊天",
  "description": "轻松随意的对话模式",
  "prompt": "{{original}}",
  "prompt_depth": 0,
  "order": ["prompt", "context"],
  "continue": false,
  "injection_depth": 2,
  "name": "User",
  "context": "保持对话轻松、自然、有趣。",
  "sample_multi": "Casual conversation should be natural, friendly, and conversational.",
  "chat_completion_mode": false,
  "max_context": 4096,
  "max_response": 256,
  "response_temp": 1.1,
  "response_top_p": 0.9,
  "response_top_k": 50
}
```

### 4. NSFW 模式

```json
{
  "name": "NSFW 角色扮演",
  "description": "包含成人内容的角色扮演",
  "prompt": "{{original}}",
  "prompt_depth": 0,
  "order": ["prompt", "context", "syrup"],
  "continue": false,
  "injection_depth": 2,
  "name": "User",
  "context": "保持角色一致性，使用生动的描写。",
  "sample_multi": "Mature roleplay involves detailed, evocative descriptions while maintaining character authenticity.",
  "chat_completion_mode": false,
  "max_context": 8192,
  "max_response": 768,
  "response_temp": 1.0,
  "response_top_p": 0.95
}
```

### 5. 短篇互动模式

```json
{
  "name": "短篇互动",
  "description": "简洁快速的对话互动",
  "prompt": "{{original}}",
  "prompt_depth": 0,
  "order": ["prompt", "context"],
  "continue": false,
  "injection_depth": 1,
  "name": "User",
  "context": "保持回复简洁有力。",
  "sample_multi": "Short interactions should be concise, impactful, and character-appropriate.",
  "chat_completion_mode": false,
  "max_context": 2048,
  "max_response": 128,
  "response_temp": 0.8,
  "response_top_p": 0.85
}
```

## 参数说明

### 生成参数

| 参数 | 范围 | 说明 |
|------|------|------|
| `response_temp` | 0.0-2.0 | 温度，控制随机性 |
| `response_top_p` | 0.0-1.0 | Nucleus 采样 |
| `response_top_k` | 0+ | Top-K 采样 |
| `response_min_p` | 0.0-1.0 | Minimum probability |
| `repetition_penalty` | 1.0-2.0 | 重复惩罚 |

### 上下文参数

| 参数 | 说明 |
|------|------|
| `max_context` | 最大上下文长度 |
| `max_response` | 单次响应最大长度 |
| `injection_depth` | 提示词注入深度 |

### 特殊参数

| 参数 | 说明 |
|------|------|
| `continue` | 是否启用继续生成 |
| `cache_prompt` | 是否缓存提示 |
| `dynamic_temp` | 动态温度调整 |

## 最佳实践

### 1. 选择合适的上下文长度

- **角色扮演**：建议 8192-16384
- **短对话**：建议 2048-4096
- **长篇创作**：建议 16384+

### 2. 调整温度参数

- **创意写作**：`temp` 1.0-1.2
- **角色扮演**：`temp` 0.8-1.0
- **精确问答**：`temp` 0.5-0.8

### 3. 控制响应长度

- **快节奏对话**：128-256 tokens
- **标准对话**：256-512 tokens
- **详细描述**：512-1024 tokens

### 4. 使用重复惩罚

- 启用 `repetition_penalty`（1.05-1.15）
- 避免生成内容单调重复

## 创建自定义预设

1. 在 SillyTavern 中进入「设置」→「预设」
2. 点击「新建预设」
3. 填写预设名称和描述
4. 配置系统提示词
5. 调整生成参数
6. 保存预设

## 导入/导出

预设文件通常为 `.json` 格式，可以在不同 SillyTavern 实例间导入导出。
