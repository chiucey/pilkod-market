# MaxClaw 模型配置结构

## 配置架构概览

```
maxclaw-config.yaml
├── model:                          # ✅ 模型配置（本技能修改范围）
│   ├── primary: string             # 主模型 ID
│   ├── fallback: []string          # Fallback 模型列表
│   ├── whitelist: []string        # 模型白名单（可选）
│   └── settings: object           # 模型相关设置
├── gateway:                        # ❌ 网关配置（保留不变）
│   ├── host: string
│   ├── port: number
│   └── ssl: boolean
├── channels:                       # ❌ 渠道配置（保留不变）
│   ├── telegram: object
│   ├── discord: object
│   └── webhook: object
├── plugins:                        # ❌ 插件配置（保留不变）
│   ├── enabled: []string
│   └── settings: object
├── logging:                        # ❌ 日志配置（保留不变）
│   ├── level: string
│   └── output: string
└── security:                       # ❌ 安全配置（保留不变）
    ├── api_keys: object
    └── encryption: object
```

## 模型配置详情

### 完整模型配置示例

```yaml
model:
  # 主模型 - 模型排序后的最优选择
  primary: "anthropic/claude-3-haiku"

  # Fallback 模型列表 - 按优先级排序
  fallback:
    - "openrouter/auto"           # 智能路由（推荐首个）
    - "google/gemini-pro"          # Google 中等模型
    - "google/gemini-flash"        # Google 长文本模型
    - "openai/gpt-3.5-turbo"       # OpenAI 通用模型
    - "deepseek/deepseek-chat"     # 中文优化模型

  # 模型白名单 - 限制可使用的模型（可选）
  whitelist:
    - "anthropic/*"
    - "google/*"
    - "openai/*"

  # 模型相关设置
  settings:
    # 温度参数
    temperature: 0.7

    # 最大 token 数
    max_tokens: 4096

    # 请求超时（秒）
    timeout: 30

    # 重试次数
    retry_count: 3

    # Fallback 触发条件
    fallback_trigger:
      # 速率限制错误码
      rate_limit_codes: [429]
      # 服务不可用错误码
      unavailable_codes: [503, 502]
      # 超时阈值（秒）
      timeout_threshold: 30
      # 连续失败触发阈值
      consecutive_failure_threshold: 3
```

### 最小模型配置

如果只需要基本功能：

```yaml
model:
  primary: "anthropic/claude-3-haiku"
  fallback:
    - "openrouter/auto"
    - "google/gemini-pro"
```

## 配置变更历史

每次模型配置更新都会记录变更历史：

```yaml
model_change_history:
  - timestamp: "2024-01-15T10:30:00Z"
    action: "initial_config"
    primary: "anthropic/claude-3-haiku"
    fallback_count: 5

  - timestamp: "2024-01-16T14:20:00Z"
    action: "update_primary"
    previous_primary: "anthropic/claude-3-haiku"
    new_primary: "google/gemini-pro"
    reason: "User requested switch"

  - timestamp: "2024-01-17T09:15:00Z"
    action: "update_fallback"
    previous_count: 5
    new_count: 3
    reason: "User requested reduction"
```

## 配置验证规则

### 必填字段

```json
{
  "model.primary": {
    "type": "string",
    "required": true,
    "pattern": "^[\w\-]+/[\w\-]+$"
  },
  "model.fallback": {
    "type": "array",
    "required": true,
    "minItems": 1,
    "maxItems": 10
  }
}
```

### 字段验证

| 字段 | 验证规则 | 错误信息 |
|------|----------|----------|
| primary | 非空字符串，格式 `provider/model` | "主模型 ID 格式错误" |
| fallback | 数组长度 1-10 | "Fallback 数量必须在 1-10 之间" |
| fallback[] | 字符串，格式 `provider/model` | "Fallback 模型 ID 格式错误" |
| whitelist | 可选数组 | "白名单格式错误" |

## 配置更新 API

### 读取当前配置

```python
def get_model_config():
    """
    获取当前模型配置
    返回：{
        "primary": string,
        "fallback": []string,
        "whitelist": []string,
        "settings": object
    }
    """
```

### 更新模型配置

```python
def update_model_config(new_config):
    """
    更新模型配置（仅修改模型相关字段）

    参数：
        new_config: {
            "primary": string,      # 可选
            "fallback": []string,   # 可选
            "whitelist": []string   # 可选
        }

    返回：
        {
            "success": boolean,
            "previous_config": object,
            "new_config": object,
            "changes": []string
        }
    """
```

### 回滚配置

```python
def rollback_model_config():
    """
    回滚到上一个有效配置
    用于更新失败时恢复
    """
```

## 安全存储

模型配置中的敏感信息（如 API 密钥）通过以下方式管理：

1. **密钥存储**：API 密钥存储在 MaxClaw 安全存储中，不在配置文件中明文存储
2. **密钥引用**：配置中只存储密钥的引用 ID
3. **密钥轮换**：支持密钥更新而不影响配置文件

```yaml
model:
  provider_credentials:
    openrouter:
      ref: "secret:openrouter_api_key"  # 引用安全存储
    anthropic:
      ref: "secret:anthropic_api_key"
```
