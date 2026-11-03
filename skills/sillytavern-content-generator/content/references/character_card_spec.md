---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c3ee9c929a2c91ea60435ee39bc0eb33
    PropagateID: c3ee9c929a2c91ea60435ee39bc0eb33
    ReservedCode1: 304402205ab1d98f0ed8fe065191e8bf7e46c5ad6d01df6201e83c121f49424f09148f0702207a58e7ad60fcb8f649d6ba80c4ce013a53cdf9b4a5fca83dfacbf1f0bc1e93dc
    ReservedCode2: 30450221008d9e54cb46feaf0b3924e05b5778f2f6c1d9cbba7359559c52b0de480e87f5ce02202d49a11e1ec89a33623bcc39d647b28624a14117e182f1024982afeed43fc6cf
---

# SillyTavern/TavernAI 角色卡 V2 格式完整规范

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V1 | 原始格式 | TavernAI 早期使用的扁平化格式 |
| V2 | 2023-05-17 | 当前规范，嵌套结构，支持扩展 |

## V1 格式（原始格式）

```typescript
type TavernCardV1 = {
  name: string
  description: string
  personality: string
  scenario: string
  first_mes: string
  mes_example: string
}
```

## V2 格式（当前规范）

```typescript
type TavernCardV2 = {
  spec: 'chara_card_v2'
  spec_version: '2.0'
  data: {
    name: string
    description: string
    personality: string
    scenario: string
    first_mes: string
    mes_example: string

    // V2 新增字段
    creator_notes: string
    system_prompt: string
    post_history_instructions: string
    alternate_greetings: Array<string>
    character_book?: CharacterBook

    // 5月8日新增
    tags: Array<string>
    creator: string
    character_version: string
    extensions: Record<string, any>
  }
}
```

## 字段详细说明

### 顶层字段

| 字段名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `spec` | string | 是 | 必须为 `"chara_card_v2"` |
| `spec_version` | string | 是 | 必须为 `"2.0"` |
| `data` | object | 是 | 包含所有角色数据的对象 |

### V1 基础字段（data 内）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | string | 角色名称 |
| `description` | string | 角色描述 |
| `personality` | string | 角色性格 |
| `scenario` | string | 场景设定 |
| `first_mes` | string | 首次消息 |
| `mes_example` | string | 消息示例 |

### V2 新增字段

| 字段名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `creator_notes` | string | 否 | 创建者备注，**不得用于prompt** |
| `system_prompt` | string | 否 | 系统提示词 |
| `post_history_instructions` | string | 否 | 后续历史指令 |
| `alternate_greetings` | Array\<string\> | 否 | 备用开场白数组 |
| `character_book` | CharacterBook | 否 | 角色专属世界书 |
| `tags` | Array\<string\> | 否 | 标签数组 |
| `creator` | string | 否 | 创建者名称 |
| `character_version` | string | 否 | 角色版本号 |
| `extensions` | object | 是 | 扩展字段，**必须默认为 {}** |

## 占位符支持

- `{{original}}` - 在 `system_prompt` 和 `post_history_instructions` 中可用
- `{{char}}` - 在对话中自动替换为角色名
- `{{user}}` - 在对话中自动替换为用户名

## extensions 字段规范

- **必须默认为空对象** `{}`
- 可以包含任意 JSON 键值对
- **不得销毁未知键值对**
- **应使用命名空间**避免冲突，格式如：
  - `"agnai/voice": /* ... */`
  - `"agnai_voice": /* ... */`
  - `"agnai": { "voice": /* ... */ }`

## 图片处理

角色卡图片通常通过以下方式处理：
1. **PNG 格式**：角色卡可嵌入 PNG 图片（带 metadata）
2. **Base64**：图片数据可编码为 Base64 字符串
3. **外部引用**：使用 URL 或本地路径引用

注意：当前规范文档中**未包含**图片格式的具体规范，图片处理由前端应用如 SillyTavern 单独定义。

## 版本区别摘要

| 特性 | V1 | V2 |
|------|----|----|
| 顶层结构 | 直接扁平 | 嵌套在 `data` 对象内 |
| spec 标识 | 无 | ✓ 必须为 `chara_card_v2` |
| 版本号 | 无 | ✓ 必须为 `2.0` |
| 创建者备注 | 无 | ✓ |
| 系统提示词 | 无 | ✓ |
| 后续指令 | 无 | ✓ |
| 备用开场白 | 无 | ✓ |
| 角色书 | 无 | ✓ |
| 标签 | 无 | ✓ |
| 创建者 | 无 | ✓ |
| 角色版本 | 无 | ✓ |
| 扩展字段 | 无 | ✓ |

## 参考链接

- [V1 规范文档](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v1.md)
- [V2 规范文档](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)
- [GitHub 仓库](https://github.com/malfoyslastname/character-card-spec-v2)
