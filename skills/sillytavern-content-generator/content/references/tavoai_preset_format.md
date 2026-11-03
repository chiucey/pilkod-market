---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 37d7775712699214082f050156263e38
    PropagateID: 37d7775712699214082f050156263e38
    ReservedCode1: 30450221008c314a7054e2cc31def6326fe820585f87eafdc9cfc1cd8fe86e5b241f73ee0102204f79e5c768650b5247cee1dca3663d5436c8bc79dba49c9bae15b1d68f57585c
    ReservedCode2: 3043021f7a6a37d37488c30164ec43e2c7f6b366d9e724efe59f70d7f4f7157592045902206253ebc25f7805f7ae3945c7a5dd1ea32f4de56246a83212a8f4d76305351415
---

# TavoAI 预设格式规范

## 完整格式结构

```json
{
  "impersonation_prompt": "[Write your next reply from the point of view of {{user}}...]",
  "new_chat_prompt": "[Start a new Chat]",
  "new_group_chat_prompt": "[Start a new group chat. Group members: {{group}}]",
  "new_example_chat_prompt": "[Example Chat]",
  "continue_nudge_prompt": "[Continue your last message without repeating its original content.]",
  "scenario_format": "{{scenario}}",
  "personality_format": "{{personality}}",
  "group_nudge_prompt": "[Write the next reply only as {{char}}.]",
  "wi_format": "{0}",
  "prompts": [
    {
      "identifier": "main",
      "name": "Main Prompt",
      "system_prompt": true,
      "marker": false,
      "content": "Write {{char}}'s next reply...",
      "role": "system",
      "injection_position": 0,
      "injection_depth": 4,
      "forbid_overrides": false
    }
  ],
  "prompt_order": [
    {
      "character_id": 100001,
      "order": [
        {"identifier": "main", "enabled": true},
        {"identifier": "worldInfoBefore", "enabled": true},
        {"identifier": "personaDescription", "enabled": true},
        {"identifier": "charDescription", "enabled": true},
        {"identifier": "charPersonality", "enabled": true},
        {"identifier": "scenario", "enabled": true},
        {"identifier": "enhanceDefinitions", "enabled": false},
        {"identifier": "nsfw", "enabled": false},
        {"identifier": "worldInfoAfter", "enabled": true},
        {"identifier": "dialogueExamples", "enabled": true},
        {"identifier": "chatHistory", "enabled": true},
        {"identifier": "jailbreak", "enabled": false}
      ]
    }
  ]
}
```

## 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `impersonation_prompt` | string | 模拟用户提示 |
| `new_chat_prompt` | string | 新对话提示 |
| `new_group_chat_prompt` | string | 新群聊提示 |
| `new_example_chat_prompt` | string | 示例对话提示 |
| `continue_nudge_prompt` | string | 继续生成提示 |
| `scenario_format` | string | 场景格式模板 |
| `personality_format` | string | 性格格式模板 |
| `group_nudge_prompt` | string | 群聊提示 |
| `wi_format` | string | 世界书格式模板 |
| `prompts` | array | Prompt 定义数组 |
| `prompt_order` | array | Prompt 顺序配置 |

## prompts 数组

### 预定义 Prompt 标识符

| identifier | name | 说明 |
|------------|------|------|
| `main` | Main Prompt | 主提示词 |
| `worldInfoBefore` | Lorebook Before | 世界书(前) |
| `personaDescription` | Persona Description | 用户设定 |
| `charDescription` | Char Description | 角色描述 |
| `charPersonality` | Char Personality | 角色性格 |
| `scenario` | Scenario | 场景设定 |
| `enhanceDefinitions` | Enhance Definitions | 增强定义 |
| `nsfw` | Auxiliary Prompt | 辅助提示 |
| `worldInfoAfter` | Lorebook After | 世界书(后) |
| `dialogueExamples` | Chat Examples | 对话示例 |
| `chatHistory` | Chat History | 聊天历史 |
| `jailbreak` | Post-History Instructions | 后历史指令 |

### Prompt 对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `identifier` | string | 唯一标识 |
| `name` | string | 显示名称 |
| `system_prompt` | boolean | 是否为系统提示 |
| `marker` | boolean | 是否使用标记 |
| `content` | string | Prompt 内容 |
| `role` | string | 角色类型 |
| `injection_position` | number | 注入位置 |
| `injection_depth` | number | 注入深度 |
| `forbid_overrides` | boolean | 禁止覆盖 |

## 示例：古风仙侠预设

```json
{
  "impersonation_prompt": "[以{{user}}的身份继续回复，参考聊天历史中的写作风格。不要扮演{{char}}或系统。不要描述{{char}}的动作。]",
  "new_chat_prompt": "[开始新对话]",
  "new_group_chat_prompt": "[开始新群聊。成员: {{group}}]",
  "new_example_chat_prompt": "[示例对话]",
  "continue_nudge_prompt": "[继续你上一条消息，不重复原内容。]",
  "scenario_format": "{{scenario}}",
  "personality_format": "{{personality}}",
  "group_nudge_prompt": "[仅以{{char}}的身份回复。]",
  "wi_format": "{0}",
  "prompts": [
    {
      "identifier": "main",
      "name": "主提示词",
      "system_prompt": true,
      "marker": false,
      "content": "Write {{char}}'s next reply in a fictional chat between {{char}} and {{user}}. Use elegant ancient Chinese style, detailed descriptions, and maintain character personality.",
      "role": "system",
      "injection_position": 0,
      "injection_depth": 4,
      "forbid_overrides": false
    },
    {
      "identifier": "worldInfoBefore",
      "name": "世界书(前)",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "personaDescription",
      "name": "用户设定",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "charDescription",
      "name": "角色描述",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "charPersonality",
      "name": "角色性格",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "scenario",
      "name": "场景设定",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "enhanceDefinitions",
      "name": "增强定义",
      "system_prompt": true,
      "marker": false,
      "content": "If you have more knowledge of {{char}}, add to the character's lore and personality to enhance them but keep the Character Sheet's definitions absolute.",
      "role": "system",
      "injection_position": 0,
      "injection_depth": 4,
      "forbid_overrides": false
    },
    {
      "identifier": "nsfw",
      "name": "辅助提示",
      "system_prompt": true,
      "marker": false,
      "content": "",
      "role": "system",
      "injection_position": 0,
      "injection_depth": 4,
      "forbid_overrides": false
    },
    {
      "identifier": "worldInfoAfter",
      "name": "世界书(后)",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "dialogueExamples",
      "name": "对话示例",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "chatHistory",
      "name": "聊天历史",
      "system_prompt": true,
      "marker": true
    },
    {
      "identifier": "jailbreak",
      "name": "后历史指令",
      "system_prompt": true,
      "marker": false,
      "content": "",
      "role": "system",
      "injection_position": 0,
      "injection_depth": 4,
      "forbid_overrides": false
    }
  ],
  "prompt_order": [
    {
      "character_id": 100001,
      "order": [
        {"identifier": "main", "enabled": true},
        {"identifier": "worldInfoBefore", "enabled": true},
        {"identifier": "personaDescription", "enabled": true},
        {"identifier": "charDescription", "enabled": true},
        {"identifier": "charPersonality", "enabled": true},
        {"identifier": "scenario", "enabled": true},
        {"identifier": "enhanceDefinitions", "enabled": false},
        {"identifier": "nsfw", "enabled": false},
        {"identifier": "worldInfoAfter", "enabled": true},
        {"identifier": "dialogueExamples", "enabled": true},
        {"identifier": "chatHistory", "enabled": true},
        {"identifier": "jailbreak", "enabled": false}
      ]
    }
  ]
}
```

## 导出注意

- 使用 `.json` 扩展名
- 文件名格式: `Tavo_预设名称_xqRm.json` (xqRm 是预设标识)
- 预设格式与角色卡/世界书不同，是独立的配置
