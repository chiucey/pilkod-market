---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3f92146805d59d75f0ec09be96d8f096
    PropagateID: 3f92146805d59d75f0ec09be96d8f096
    ReservedCode1: 304502203d6d95810402fd24b274a8c22139fe4a0b4fbf06129fa9bd43f437168965b129022100bb050319ecac0469a08917c26d26d479a3c7c337d017891e8c561e474fd45278
    ReservedCode2: 304402201589fca617042937e92060c4867e3396d88c0adb1705f86b5765fad1bfd67ee102203dca95dc9e570351c28452829ee527e5a17ea7ccf6726f246b05cf8c6dbdb650
---

# TavoAI 世界书格式规范

## ⚠️ 重要配置建议（基于 SillyTavern 官方文档）

| 字段 | 推荐值 | 说明 |
|------|--------|------|
| `scanDepth` | **1-2** | 扫描最近几条消息查找关键词。官方建议 1-2，512 会扫描整个对话历史 |
| `sticky` | **1** | 角色卡内嵌条目建议设为 1（常驻生效） |
| `constant` | **true** | 重要条目设为常驻，不受 scanDepth 限制 |

**⚠️ 注意**：`scanDepth=512` 对于普通聊天（可能只有几十条消息）过大，会扫描整个对话历史造成 token 浪费。

## 完整格式结构

```json
{
  "entries": {
    "0": {
      "uid": 0,
      "disable": false,
      "use_regex": false,
      "name": "条目名称",
      "comment": "条目备注",
      "content": "条目内容",
      "constant": true,
      "vectorized": false,
      "position": 0,
      "depth": 4,
      "role": 0,
      "key": ["关键词1", "关键词2"],
      "keysecondary": ["次级关键词"],
      "selective": true,
      "selectiveLogic": 0,
      "caseSensitive": false,
      "matchWholeWords": true,
      "scanDepth": 2,
      "useGroupScoring": false,
      "excludeRecursion": false,
      "preventRecursion": false,
      "delayUntilRecursion": false,
      "useProbability": true,
      "probability": 100,
      "sticky": 1,
      "cooldown": 0,
      "delay": 0,
      "group": "",
      "groupOverride": false,
      "groupWeight": 100,
      "display_index": 100,
      "order": 100
    }
  }
}
```

## 字段详解

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `uid` | number | 唯一标识符 |
| `disable` | boolean | 是否禁用 (false=启用) |
| `use_regex` | boolean | 是否使用正则匹配 |
| `name` | string | 条目名称 |
| `content` | string | 条目内容 |
| `key` | array | 触发关键词数组 |

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `comment` | string | "" | 备注信息 |
| `constant` | boolean | false | 是否常驻 |
| `position` | number | 0 | 插入位置 |
| `depth` | number | 4 | 深度设置 |
| `role` | number | 0 | 角色类型 |
| `keysecondary` | array | [] | 次级关键词 |
| `selective` | boolean | false | 是否选择性匹配 |
| `selectiveLogic` | number | 0 | 选择逻辑 |

### 匹配设置

| 字段 | 类型 | 推荐值 | 说明 |
|------|------|--------|------|
| `caseSensitive` | boolean | false | 区分大小写 |
| `matchWholeWords` | boolean | true | 全词匹配（中文建议设为 false） |
| `scanDepth` | number | **1-2** | 扫描最近几条消息，官方建议 1-2 |

### 概率与冷却

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `useProbability` | boolean | true | 使用概率 |
| `probability` | number | 100 | 触发概率 (0-100) |
| `sticky` | number | 0 | 持久化 (0=否, 1=是) |
| `cooldown` | number | 0 | 冷却时间 |
| `delay` | number | 0 | 延迟注入 |

### 递归控制

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `excludeRecursion` | boolean | false | 排除递归 |
| `preventRecursion` | boolean | false | 阻止递归 |
| `delayUntilRecursion` | boolean | false | 延迟至递归 |

### 分组系统

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `group` | string | "" | 分组名称 |
| `groupOverride` | boolean | false | 分组覆盖 |
| `groupWeight` | number | 100 | 分组权重 |

### 排序

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `display_index` | number | 100 | 显示顺序 |
| `order` | number | 100 | 插入顺序 |

## Position 值说明

| 值 | 说明 |
|----|------|
| 0 | before_char (角色消息前) |
| 1 | after_char (角色消息后) |
| 2 | system (系统消息) |

## Role 值说明

| 值 | 说明 |
|----|------|
| 0 | all (全部角色) |
| 1 | user (仅用户) |
| 2 | character (仅角色) |

## 示例

```json
{
  "entries": {
    "0": {
      "uid": 0,
      "disable": false,
      "use_regex": false,
      "name": "太极玄清道",
      "comment": "青云门功法",
      "content": "太极玄清道是青云门镇派功法...",
      "constant": true,
      "vectorized": false,
      "position": 0,
      "depth": 4,
      "role": 0,
      "key": ["太极玄清道", "修炼"],
      "keysecondary": [],
      "selective": true,
      "selectiveLogic": 0,
      "caseSensitive": false,
      "matchWholeWords": true,
      "scanDepth": 2,
      "useGroupScoring": false,
      "excludeRecursion": false,
      "preventRecursion": false,
      "delayUntilRecursion": false,
      "useProbability": true,
      "probability": 100,
      "sticky": 1,
      "cooldown": 0,
      "delay": 0,
      "group": "",
      "groupOverride": false,
      "groupWeight": 100,
      "display_index": 100,
      "order": 100
    }
  }
}
```

## 分场合配置建议

### 场合1：角色卡内嵌世界书（重要性：高）
```json
{
  "scanDepth": 2,
  "sticky": 1,
  "constant": true
}
```
**原因**：角色设定重要，需要常驻生效。

### 场合2：独立世界书 - 复杂剧情（重要性：中）
```json
{
  "scanDepth": 2,
  "sticky": 0,
  "constant": false
}
```
**原因**：需要更多触发空间，但仍需控制。

### 场合3：独立世界书 - 简单设定（重要性：低）
```json
{
  "scanDepth": 1,
  "sticky": 0,
  "constant": false
}
```
**原因**：保守配置，够用即可。

### 场合4：长期记忆/递归触发（谨慎使用）
```json
{
  "scanDepth": 2,
  "excludeRecursion": false,
  "preventRecursion": false
}
```
**警告**：递归扫描容易产生意外连锁，造成 token 爆炸。

## 导出注意

- 使用 `.json` 扩展名
- 文件名格式建议: `Tavo_名称_xqRT.json` (xqRT 是自动生成的标识)
- 导入时 TavoAI 会自动处理格式
