---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fe5ea228ff896c19b11c320c0f0e2c0e
    PropagateID: fe5ea228ff896c19b11c320c0f0e2c0e
    ReservedCode1: 3045022040185dececef38af4005f83672122c75edcc645591fa4b3bd09912bd897a990f022100f19d0acd438b5feff4663297ba32f041a32c34dfcbf81a68f866090ed0d9b672
    ReservedCode2: 304502202e1a72668a6a15322b3b19d1d42cbb061f1766346584b7008d9f1fcf13f728110221009b26a9fe58ad75e723c2a777971d7aa3953bb800d2d472faa219872cf2c77bbf
---

# TavoAI 正则格式规范

## 完整格式结构

```json
{
  "id": "uuid-string",
  "scriptName": "规则名称",
  "findRegex": "正则表达式",
  "replaceString": "替换内容",
  "trimStrings": [],
  "placement": [2],
  "disabled": false,
  "markdownOnly": true,
  "promptOnly": false,
  "runOnEdit": false,
  "substituteRegex": 0,
  "minDepth": null,
  "maxDepth": null
}
```

## 字段详解

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符 (UUID) |
| `scriptName` | string | 规则显示名称 |
| `findRegex` | string | 正则表达式模式 |

### 替换设置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `replaceString` | string | "" | 替换内容 |
| `trimStrings` | array | [] | 修剪字符串列表 |
| `substituteRegex` | number | 0 | 替换模式 |

### 作用范围

| 字段 | 类型 | 说明 |
|------|------|------|
| `placement` | array | 作用位置数组 |

**Placement 值**:
- `0` = User Message (用户消息)
- `1` = Character Message (角色消息)
- `2` = Display (显示)
- `3` = Extension (扩展)

### 执行条件

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `disabled` | boolean | false | 是否禁用 |
| `markdownOnly` | boolean | true | 仅 Markdown |
| `promptOnly` | boolean | false | 仅 Prompt |
| `runOnEdit` | boolean | false | 编辑时执行 |
| `minDepth` | number/null | null | 最小深度 |
| `maxDepth` | number/null | null | 最大深度 |

### substituteRegex 值

| 值 | 说明 |
|----|------|
| 0 | original (原始) |
| 1 | escaped (转义) |
| 2 | none (无) |

## 示例：选择引导正则

### 正则规则1：动作选项触发

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "scriptName": "动作选项",
  "findRegex": "//#动作",
  "replaceString": "",
  "trimStrings": [],
  "placement": [0, 1, 2],
  "disabled": false,
  "markdownOnly": true,
  "promptOnly": false,
  "runOnEdit": false,
  "substituteRegex": 0,
  "minDepth": null,
  "maxDepth": null
}
```

### 正则规则2：角色名替换

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "scriptName": "角色名替换",
  "findRegex": "雪琪师姐|雪琪妹妹",
  "replaceString": "{{char}}",
  "trimStrings": [],
  "placement": [0, 1],
  "disabled": false,
  "markdownOnly": false,
  "promptOnly": false,
  "runOnEdit": false,
  "substituteRegex": 0,
  "minDepth": null,
  "maxDepth": null
}
```

## 导出格式

### 单条规则

单个规则直接保存为 `.json` 文件。

### 多条规则

多条规则需要**打包成 ZIP 文件**：

1. 将每个规则保存为单独的 `.json` 文件
2. 文件名格式: `tavo1_名称.json`, `tavo2_名称.json`, ...
3. 打包成 ZIP 文件
4. ZIP 文件名格式: `Tavo_模块名称_xqSz.zip`

### ZIP 打包示例

```
Tavo_选择引导_xqSz.zip
├── tavo1_动作选项.json
├── tavo2_对话选项.json
├── tavo3_探索选项.json
├── tavo4_角色名替换.json
└── tavo5_术语规范.json
```

## UUID 生成

可使用在线工具或代码生成：

```javascript
// JavaScript
const uuid = crypto.randomUUID();
// 或
const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
  const r = Math.random() * 16 | 0;
  const v = c === 'x' ? r : (r & 0x3 | 0x8);
  return v.toString(16);
});
```

```python
# Python
import uuid
uid = str(uuid.uuid4())
```
