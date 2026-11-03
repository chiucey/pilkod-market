---
name: smiles-to-iupac
description: 将分子 SMILES 表达式转换为标准 IUPAC 命名。当用户要求转换 SMILES 为 IUPAC 名称、分析化学结构命名、或识别分子时使用。
---

# SMILES to IUPAC Converter

使用 PubChem REST API 将 SMILES 字符串转换为 IUPAC 命名。

## 工作流程

### 1. 获取 PubChem CID

使用 PubChem PUG REST API 的 SMILES 查询端点：

```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/property/IUPACName/JSON
```

**注意**：SMILES 字符串中的特殊字符需要 URL 编码：
- `#` → `%23`
- `@` → `%40`
- `+` → `%2B`
- `/` → `%2F`
- `\` → `%5C`

### 2. 解析响应

API 返回 JSON 格式的分子属性，包括 `IUPACName` 字段。

### 3. 处理结果

- **成功**：返回 IUPAC 命名
- **失败**：返回错误信息及可能的原因

## 示例

### 示例 1：苯甲酰胺

**输入 SMILES**：`NC(=O)c1ccccc1`

**API 调用**：
```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/NC%28%3DO%29c1ccccc1/property/IUPACName/JSON
```

**输出**：`benzamide`

### 示例 2：阿司匹林

**输入 SMILES**：`CC(=O)Oc1ccccc1C(=O)O`

**API 调用**：
```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/CC%28%3DO%29Oc1ccccc1C%28%3DO%29O/property/IUPACName/JSON
```

**输出**：`2-acetyloxybenzoic acid`

## 错误处理

| 错误情况 | 处理方式 |
|---------|---------|
| 无效 SMILES | 返回"无法识别的 SMILES 字符串" |
| 分子不存在 | 返回"未在 PubChem 中找到该分子" |
| API 请求失败 | 返回"PubChem API 请求失败，请稍后重试" |
| 网络错误 | 返回"网络连接错误" |

## 工具选择

使用 `mcp__matrix__extract_content_from_websites` 工具调用 PubChem API。
