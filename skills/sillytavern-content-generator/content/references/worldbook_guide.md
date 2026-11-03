---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2e30a28240e5d7621ed38a1dc6b79a8a
    PropagateID: 2e30a28240e5d7621ed38a1dc6b79a8a
    ReservedCode1: 30440220118ffa2735b50ede4a662fceb5eb0d15c8f0f484a1091dc3b6a83f332d6ca1e102206f6d00d7d956bc4e55b46e5f1a56522965903a70f13bbbec64b566053c49abee
    ReservedCode2: 3045022072b9fc9f2ca4aecf62808c8b4822c99187d620da1ec8a98a7c28526c63c0565c0221009dcf269cb2e9d2fadd37643b871acc69e909c6ae187fea5c648ef163998f6764
---

# 世界书/知识库配置指南

## 概述

世界书（Lorebook/World Info）是 SillyTavern/TavernAI 中用于管理世界观、角色背景、设定规则等信息的核心功能。通过关键字触发机制，世界书能够在对话中自动插入相关知识。

## 基本结构

```typescript
type WorldBook = {
  name?: string                    // 世界书名称
  description?: string             // 世界书描述
  scan_depth?: number              // 扫描深度（agnai: Memory: Chat History Depth）
  token_budget?: number            // Token 预算（agnai: Memory: Context Limit）
  recursive_scanning?: boolean    // 是否允许条目内容触发其他条目
  extensions: Record<string, any>  // 扩展字段
  entries: Array<WorldBookEntry>  // 条目数组
}
```

## 条目结构

```typescript
type WorldBookEntry = {
  keys: Array<string>             // 触发关键词（必需）
  content: string                 // 条目内容（必需）
  extensions: Record<string, any> // 扩展字段
  enabled: boolean                // 是否启用
  insertion_order: number         // 插入顺序，数值越小越优先
  case_sensitive?: boolean        // 是否区分大小写

  // 以下字段在 SillyTavern 中无直接等价功能
  name?: string                   // 条目名称（不用于 prompt）
  priority?: number               // 优先级，预算不足时先丢弃低优先级
  id?: number                     // 条目 ID
  comment?: string               // 备注
  selective?: boolean             // 是否需要同时匹配 keys 和 secondary_keys
  secondary_keys?: Array<string>  // 次要关键词
  constant?: boolean              // 是否始终插入（在预算范围内）
  position?: 'before_char' | 'after_char'  // 插入位置
}
```

## 字段详解

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `keys` | Array\<string\> | 触发关键词数组 |
| `content` | string | 条目内容 |
| `extensions` | object | 扩展字段（通常为空对象 `{}`） |
| `enabled` | boolean | 条目是否启用 |
| `insertion_order` | number | 插入顺序 |

### 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | string | - | 条目名称 |
| `case_sensitive` | boolean | false | 关键词是否区分大小写 |
| `constant` | boolean | false | 是否始终插入 |
| `position` | string | 'before_char' | 插入位置 |
| `priority` | number | 0 | 优先级（数字越大优先级越高） |
| `selective` | boolean | false | 是否需要同时匹配次要关键词 |
| `secondary_keys` | Array\<string\> | [] | 次要关键词 |

### 配置参数（基于 SillyTavern 官方文档）

| 字段 | 推荐值 | 说明 |
|------|--------|------|
| `scan_depth` | **1-2** | 扫描最近几条消息查找关键词。官方建议从小值开始，避免扫描过多历史导致 token 浪费 |
| `token_budget` | **256-512** | Token 预算，约占 context 的 10-20%。超出后不再插入新条目 |
| `recursive_scanning` | **false** | 是否允许条目内容触发其他条目。官方建议从保守开始，避免意外连锁 |

**⚠️ 注意**：scan_depth=512 意味着扫描 512 条消息，对于普通聊天（可能只有几十条），这会扫描整个对话历史，造成 token 浪费。

## 分场合配置推荐

### 场合1：角色卡内嵌世界书（重要性：高）
角色设定直接影响角色扮演质量，建议保守配置。

```json
{
  "scan_depth": 2,
  "token_budget": 512,
  "recursive_scanning": false
}
```
**条目建议**：`constant: true`（常驻生效，不受 scan_depth 限制）

### 场合2：独立世界书 - 复杂剧情（重要性：中）
涉及多条故事线、多个势力，需要更多触发空间。

```json
{
  "scan_depth": 2,
  "token_budget": 768,
  "recursive_scanning": false
}
```

### 场合3：独立世界书 - 简单设定（重要性：低）
单一主题、少量条目，保守配置即可。

```json
{
  "scan_depth": 1,
  "token_budget": 256,
  "recursive_scanning": false
}
```

### 场合4：长期记忆/递归触发（谨慎使用）
仅在需要动态上下文构建时开启递归，**容易产生意外连锁**。

```json
{
  "scan_depth": 2,
  "token_budget": 512,
  "recursive_scanning": true
}
```
**警告**：递归扫描可能导致条目互相触发，造成 token 爆炸。建议配合 `excludeRecursion`、`preventRecursion` 等字段控制。

---

## 使用技巧

### 关键词设置

1. **避免过于宽泛**：如"魔法"、"人"等词过于通用
2. **使用多义词组合**：如"霜狼氏族"而非单独的"氏族"
3. **中英文混用**：可同时设置中文和英文关键词
4. **同义词覆盖**：为主要关键词添加同义词变体

### 条目排序

1. **核心概念优先**：通用规则放前面（insertion_order 较小）
2. **具体到抽象**：具体设定在前，抽象规则在后
3. **控制数量**：单个世界书建议不超过 50 个条目

### 内容撰写

1. **简洁明确**：每条内容控制在 100-500 字
2. **使用 AI 友好格式**：避免过于复杂的嵌套结构
3. **保持一致性**：同一世界书内的风格和术语保持统一
4. **定期清理**：删除不再使用的过时条目

## 示例结构

```json
{
  "name": "北境大陆设定",
  "description": "包含北境大陆的地理、政治、魔法体系",
  "scan_depth": 2,
  "token_budget": 512,
  "recursive_scanning": false,
  "extensions": {},
  "entries": [
    {
      "keys": ["北境", "北境大陆"],
      "content": "北境大陆是位于大陆北端的广袤土地，气候严寒，分布着众多氏族部落。",
      "extensions": {},
      "enabled": true,
      "insertion_order": 1,
      "constant": true,
      "position": "before_char"
    },
    {
      "keys": ["霜狼氏族", "艾琳娜"],
      "content": "霜狼氏族是北境最古老的氏族之一，以驯养冰霜巨狼闻名。艾琳娜是末代族长的独女，在氏族覆灭后流亡南方。",
      "extensions": {},
      "enabled": true,
      "insertion_order": 2,
      "case_sensitive": false,
      "position": "before_char"
    },
    {
      "keys": ["冰霜魔法", "霜狼"],
      "content": "冰霜魔法是北境特有的自然魔法体系，能够操控冰雪与寒气。",
      "extensions": {},
      "enabled": true,
      "insertion_order": 3,
      "position": "before_char"
    }
  ]
}
```

## 与角色卡集成

### 方式一：嵌入角色卡

在世界书配置中，角色卡可以包含 `character_book` 字段：

```json
{
  "data": {
    "name": "艾琳娜",
    "character_book": {
      "name": "艾琳娜专属设定",
      "entries": [...]
    }
  }
}
```

### 方式二：独立世界书

创建独立的世界书文件（`.json`），在 SillyTavern 中单独导入。

### 方式三：全局世界书

创建全局世界书，在所有对话中生效，通过关键字选择性触发。

## 兼容性说明

- ForkSilly 与 SillyTavern 世界书兼容
- 所有参数含义相似
- 部分 SillyTavern 高级参数可能不适用，但不影响互相导入

## 推荐工具

- [妮卡角色工作室Pro](https://mocards.netlify.app/)
- [OcO萌/AI角色卡编辑器](https://ce.ooc.moe/zh-CN)
