---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5daaf7721d694f56b82c6d1e23f9432f
    PropagateID: 5daaf7721d694f56b82c6d1e23f9432f
    ReservedCode1: 3045022100cdc13d103eadd623619e9ebb70085aa5117ca2877ae973e78c21c95eb81957b902202ee293bac3dbc1a94d56b284dfd8eee54c140a9a42179a5a9dd947482490ec57
    ReservedCode2: 3046022100ef7577046f88c0983714f817b6b6eeabf8dd7b494f2b668dd15516293c6adb84022100cf0fa74f038ef68d98a02f5a11d378bd4af3491ec726121a5f53dab719e7375f
---

# Character Card V3 Specification (CCv3)

## 概述

Character Card V3 是角色卡规范的最新版本，是 V2 的超集，支持多媒体资源、装饰器系统和宏语法。

**规范来源**：[kwaroran/character-card-spec-v3](https://github.com/kwaroran/character-card-spec-v3)

---

## 顶层结构

```typescript
interface CharacterCardV3 {
  spec: 'chara_card_v3'      // 必需：必须是此值
  spec_version: '3.0'         // 必需：必须是 "3.0"
  data: CharacterDataV3       // 必需：角色数据对象
}
```

---

## data 对象字段

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `extensions` | `Record<string, any>` | 扩展字段，必须为空对象 `{}` |

### V2 兼容字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `string` | 角色名称 |
| `description` | `string` | 角色描述 |
| `tags` | `Array<string>` | 标签数组 |
| `creator` | `string` | 创建者名称 |
| `character_version` | `string` | 角色版本号 |
| `mes_example` | `string` | 消息示例 |
| `system_prompt` | `string` | 系统提示词 |
| `post_history_instructions` | `string` | 后续历史指令 |
| `first_mes` | `string` | 首次消息 |
| `alternate_greetings` | `Array<string>` | 备用开场白 |
| `personality` | `string` | 性格描述 |
| `scenario` | `string` | 场景设定 |
| `creator_notes` | `string` | 创建者备注 |

### V3 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `character_book` | `Lorebook` | 角色专属世界书 |
| `nickname` | `string` | 昵称（替换 {{char}}） |
| `creator_notes_multilingual` | `Record<string, string>` | 多语言备注（ISO 639-1） |
| `source` | `Array<string>` | 来源 URL 或 ID 数组 |
| `group_only_greetings` | `Array<string>` | 群聊专用开场白 |
| `assets` | `Array<Asset>` | 资源数组 |
| `creation_date` | `number` | 创建时间（Unix 时间戳，秒） |
| `modification_date` | `number` | 修改时间（Unix 时间戳，秒） |

---

## 资源系统 (assets)

### Asset 对象

```typescript
interface Asset {
  type: string   // 资源类型
  uri: string    // 资源 URI
  name: string   // 资源名称
  ext: string    // 文件扩展名（小写，不含 .）
}
```

### 资源类型

| 类型 | 说明 | 备注 |
|------|------|------|
| `icon` | 角色头像 | 必须有一个 `name: "main"` |
| `background` | 背景图片 | 必须有一个 `name: "main"` |
| `user_icon` | 用户头像 | 存在时禁用 persona 功能 |
| `emotion` | 表情图片 | name 如 `happy`, `sad` 等 |

### URI 类型

| 前缀 | 说明 | 示例 |
|------|------|------|
| `https://` / `http://` | HTTP URL | `https://example.com/avatar.png` |
| `data:` | Base64 数据 URL | `data:image/png;base64,...` |
| `embeded://` | 嵌入资源 | `embeded://path/to/asset.png` |
| `ccdefault:` | 默认图标 | `ccdefault:` |

### 嵌入格式 (CHARX)

CHARX 文件是 ZIP 格式，包含：
- `card.json` - 角色卡对象
- `assets/{type}/images/` - 图片资源
- `assets/{type}/audio/` - 音频资源
- `assets/{type}/video/` - 视频资源
- `assets/{type}/l2d/` - Live2D 模型
- `assets/{type}/3d/` - 3D 模型

---

## 装饰器语法

装饰器是以 `@@` 开头的新行，在世界书条目的 `content` 中使用。

### 激活装饰器

| 装饰器 | 值 | 说明 |
|--------|-----|------|
| `@@activate_only_after` | number | 在 N 条助手消息后才生效 |
| `@@activate_only_every` | number | 每 N 条消息生效一次 |
| `@@keep_activate_after_match` | - | 首次匹配后始终生效 |
| `@@dont_activate_after_match` | - | 首次匹配后不再生效 |
| `@@activate` | - | 无条件生效 |
| `@@dont_activate` | - | 除非有 `@@activate` 否则不生效 |

### 深度装饰器

| 装饰器 | 值 | 说明 |
|--------|-----|------|
| `@@depth` | number | 在倒数第 N 条消息处插入 |
| `@@reverse_depth` | number | 同 @@depth 但正序计数 |
| `@@instruct_depth` | number | 在倒数第 N 个 token 处插入 |
| `@@reverse_instruct_depth` | number | 同 @@instruct_depth 但正序 |
| `@@role` | string | 指定消息角色：`"assistant"`, `"system"`, `"user"` |

### 位置装饰器

| 装饰器 | 值 | 说明 |
|--------|-----|------|
| `@@position` | string | 插入位置 |

**位置值**：
- `after_desc` - description 后
- `before_desc` - description 前
- `personality` - personality 字段
- `scenario` - scenario 字段

### 扫描装饰器

| 装饰器 | 值 | 说明 |
|--------|-----|------|
| `@@scan_depth` | number | 覆盖世界书的 scan_depth |
| `@@instruct_scan_depth` | number | 扫描最近 N 个 token |
| `@@additional_keys` | strings | 额外必须匹配的关键字 |
| `@@exclude_keys` | strings | 排除匹配的关键字 |

### 上下文装饰器

| 装饰器 | 值 | 说明 |
|--------|-----|------|
| `@@is_greeting` | number | 仅在特定开场白索引时生效 |
| `@@is_user_icon` | string | 仅在特定用户头像时生效 |
| `@@ignore_on_max_context` | - | 上下文满时不生效 |
| `@@disable_ui_prompt` | string | 禁用 UI 提示类型 |

### 降级装饰器

使用 `@@@` 链式降级：
```
@@risu_only_decorator 4 → @@@activate_every 4
```

---

## 宏语法 (CBS)

所有宏必须以 `{{` 开头，`}}` 结尾（不区分大小写）。

| 宏 | 说明 |
|----|------|
| `{{char}}` | 替换为 nickname 或 name |
| `{{user}}` | 替换为用户显示名称 |
| `{{random:A,B,C,...}}` | 从逗号分隔列表中随机选择 |
| `{{pick:A,B,C,...}}` | 确定性随机（相同 prompt 相同结果） |
| `{{roll:N}}` 或 `{{roll:dN}}` | 掷 N 面骰子 |
| `{{// comment}}` | 注释，替换为空字符串 |
| `{{hidden_key:A}}` | 隐藏关键字，用于递归扫描 |
| `{{comment: text}}` | 行内注释，prompt 中为空 |
| `{{reverse:A}}` | 反转字符串 A |

---

## Lorebook 世界书对象

```typescript
type Lorebook = {
  name?: string
  description?: string
  scan_depth?: number
  token_budget?: number
  recursive_scanning?: boolean
  extensions: Record<string, any>
  entries: Array<LorebookEntry>
}
```

### 条目必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `keys` | `Array<string>` | 触发关键字 |
| `content` | `string` | 条目内容 |
| `extensions` | `Record<string, any>` | 扩展字段 |
| `enabled` | `boolean` | 是否启用 |
| `insertion_order` | `number` | 插入顺序 |
| `use_regex` | `boolean` | 是否使用正则匹配（**V3 必需**） |

### 条目可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `string` | 条目名称 |
| `id` | `number \| string` | 条目 ID |
| `comment` | `string` | 备注 |
| `priority` | `number` | 优先级 |
| `selective` | `boolean` | 需要同时匹配次要关键字 |
| `secondary_keys` | `Array<string>` | 次要关键字 |
| `constant` | `boolean` | 始终插入 |
| `position` | `string` | `'before_char'` 或 `'after_char'` |
| `case_sensitive` | `boolean` | 关键字是否区分大小写 |

---

## V2 vs V3 差异

| 特性 | V2 | V3 |
|------|----|----|
| spec 字段 | 可选 | **必需**：`"chara_card_v3"` |
| spec_version | 可选 | **必需**：`"3.0"` |
| character_book | 不支持 | **支持** 作为 Lorebook 对象 |
| creator_notes_multilingual | 不支持 | **支持**（ISO 639-1 键） |
| nickname | 不支持 | **支持**（替换 {{char}}） |
| assets | 不支持 | **完整**资源系统 |
| source | 不支持 | **数组**来源 URL/ID |
| group_only_greetings | 不支持 | **支持**群聊开场白 |
| creation_date | 不支持 | **Unix 时间戳** |
| modification_date | 不支持 | **Unix 时间戳** |
| use_regex | 可选 | **必需** 在世界书条目中 |
| 嵌入格式 | PNG `chara` 块 | PNG tEXt `ccv3`、JSON、CHARX |

---

## 世界书导出格式

```typescript
{
  spec: 'lorebook_v3',
  data: Lorebook
}
```

---

## 实现建议

### 日期时间处理

```javascript
// 创建时间戳
const creation_date = Math.floor(Date.now() / 1000);

// 格式化展示
const date = new Date(timestamp * 1000);
console.log(date.toISOString()); // "2024-01-01T00:00:00.000Z"
```

### 多语言支持

```javascript
// creator_notes_multilingual
const notes = {
  "zh": "中文备注",
  "en": "English notes",
  "ja": "日本語のメモ"
};

// 获取客户端语言
const clientLang = navigator.language.split('-')[0];
const note = notes[clientLang] || notes["en"];
```

### 资源 URI 处理

```javascript
function resolveAssetUri(asset) {
  if (asset.uri.startsWith('embeded://')) {
    return extractFromPackage(asset.uri);
  } else if (asset.uri.startsWith('data:')) {
    return asset.uri; // Base64
  } else if (asset.uri === 'ccdefault:') {
    return getDefaultIcon();
  }
  return asset.uri; // HTTP/HTTPS URL
}
```

---

## 参考链接

- [Character Card Spec V3 GitHub](https://github.com/kwaroran/character-card-spec-v3)
- [SPEC_V3.md 完整规范](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md)
- [SillyTavern 官方文档](https://docs.sillytavern.app/)
