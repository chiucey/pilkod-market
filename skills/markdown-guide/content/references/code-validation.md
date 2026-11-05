# 代码块校验规则

## 目录

1. [概述](#概述)
2. [语言类型标识校验](#语言类型标识校验)
3. [拼写检查规则](#拼写检查规则)
4. [语法检查规则](#语法检查规则)
5. [各语言语法检查详解](#各语言语法检查详解)
6. [常见错误示例](#常见错误示例)
7. [最佳实践](#最佳实践)

## 概述

代码块校验是 Markdown 文档校验的重要组成部分，确保代码示例的准确性和可读性。

### 校验能力

| 校验类型 | 说明 | 错误级别 |
|:---------|:-----|:---------|
| **语言类型标识** | 检查代码块是否标注语言 | 警告 |
| **拼写检查** | 检查文本内容中的拼写错误 | 警告 |
| **语法检查** | 检查代码语法错误 | 错误/警告 |

### 支持的语言

校验工具支持以下语言的语法检查：

| 语言 | 标识符 | 检查内容 |
|:-----|:-------|:---------|
| JSON | `json` | JSON 语法有效性 |
| YAML | `yaml`, `yml` | 缩进、格式规范 |
| SQL | `sql` | 关键字、括号配对 |
| JavaScript | `javascript`, `js` | 括号、引号配对 |
| TypeScript | `typescript`, `ts` | 括号、引号配对 |
| Python | `python`, `py` | 缩进一致性 |
| HTML | `html` | 标签配对 |
| XML | `xml` | 标签配对 |
| CSS | `css`, `scss` | 大括号、分号 |

## 语言类型标识校验

### 规则说明

所有代码块应明确标注语言类型，以启用语法高亮和校验功能。

### 正确示例

````markdown
```javascript
function hello() {
  console.log("Hello, World!");
}
```

```python
def hello():
    print("Hello, World!")
```

```json
{
  "message": "Hello, World!"
}
```
````

### 错误示例

````markdown
```
function hello() {
  console.log("Hello, World!");
}
```
````

**校验输出：**
```
⚠️  [第 1 行] 代码块未指定语言标识
    💡 建议: 添加语言标识以启用语法高亮和校验，如 ```javascript、```python 等
```

### 未知语言标识

当使用未知或不常见的语言标识时，校验工具会发出警告：

````markdown
```myCustomLanguage
some code here
```
````

**校验输出：**
```
⚠️  [第 1 行] 未知的代码块语言标识: "myCustomLanguage"
    💡 建议: 使用标准的语言标识，如 javascript、python、json 等
```

## 拼写检查规则

### 检查范围

拼写检查仅针对文本类代码块进行：

| 语言标识 | 是否检查 | 原因 |
|:---------|:---------|:-----|
| `text`, `plaintext` | ✅ 检查 | 纯文本内容 |
| `markdown`, `md` | ✅ 检查 | 文档内容 |
| `rst`, `asciidoc` | ✅ 检查 | 文档格式 |
| `javascript`, `python` 等 | ❌ 不检查 | 代码关键字较多 |
| `json`, `yaml` | ❌ 不检查 | 数据格式 |
| `mermaid`, `plantuml` | ❌ 不检查 | 图表语法 |

### 检查规则

1. **跳过编程关键字**：不检查编程语言保留字
2. **跳过技术词汇**：常见技术词汇不报错
3. **跳过驼峰命名**：驼峰命名可能是标识符
4. **检查长度 ≥ 3 的单词**：短单词可能是缩写

### 常见拼写错误

| 错误拼写 | 正确拼写 |
|:---------|:---------|
| `teh` | `the` |
| `adn` | `and` |
| `recieve` | `receive` |
| `occured` | `occurred` |
| `seperate` | `separate` |
| `definately` | `definitely` |
| `accomodate` | `accommodate` |
| `enviroment` | `environment` |
| `goverment` | `government` |
| `knowlege` | `knowledge` |

### 示例

````markdown
```text
This is a simple example with a spelling error: definately should be definitely.
The enviroment variable is not set.
```
````

**校验输出：**
```
⚠️  [第 1 行] 可能的拼写错误: "definately"
    💡 建议: 可能的正确拼写: definitely

⚠️  [第 2 行] 可能的拼写错误: "enviroment"
    💡 建议: 可能的正确拼写: environment
```

## 语法检查规则

### JSON 语法检查

#### 检查内容

- JSON 语法有效性
- 括号配对
- 引号配对
- 逗号位置

#### 正确示例

````markdown
```json
{
  "name": "John",
  "age": 30,
  "skills": ["JavaScript", "Python"]
}
```
````

#### 错误示例

````markdown
```json
{
  "name": "John",
  "age": 30,
  "skills": ["JavaScript", "Python"
}
```
````

**校验输出：**
```
❌ [第 5 行] 语法错误: Expected ',' or ']' after array element
    💡 建议: 检查语法并修正
```

### YAML 语法检查

#### 检查内容

- 缩进一致性（应使用空格）
- 冒号后空格
- Tab 字符检测

#### 正确示例

````markdown
```yaml
server:
  port: 8080
  host: localhost
database:
  name: mydb
  user: admin
```
````

#### 错误示例

````markdown
```yaml
server:
	port: 8080    # 使用了 Tab
  host: localhost
database:
  name:mydb      # 冒号后缺少空格
```
````

**校验输出：**
```
⚠️  [第 2 行] YAML 应使用空格缩进，而非 Tab
    💡 建议: 使用空格代替 Tab

⚠️  [第 5 行] YAML 键值对冒号后应有一个空格
    💡 建议: 在冒号后添加空格
```

## 各语言语法检查详解

### JavaScript/TypeScript 语法检查

#### 检查内容

| 检查项 | 说明 | 级别 |
|:-------|:-----|:-----|
| 括号配对 | `()`, `[]`, `{}` 配对检查 | 错误 |
| 引号配对 | `"`, `'`, `` ` `` 配对检查 | 警告 |
| 控制语句 | `if`, `for`, `while` 后的括号 | 警告 |

#### 正确示例

````markdown
```javascript
function fetchData(url) {
  return fetch(url)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      return data;
    });
}
```
````

#### 错误示例

````markdown
```javascript
function fetchData(url {
  return fetch(url)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      return data;
    });
}
```
````

**校验输出：**
```
❌ [第 1 行] 语法错误: () 括号不匹配: 1 个 "(" 和 0 个 ")"
    💡 建议: 检查语法并修正
```

### Python 语法检查

#### 检查内容

| 检查项 | 说明 | 级别 |
|:-------|:-----|:-----|
| 缩进一致性 | 是否使用 4 空格缩进 | 警告 |
| Tab/空格混用 | 不应混用 Tab 和空格 | 警告 |
| 冒号后缩进 | `: ` 后应有缩进代码块 | 警告 |

#### 正确示例

````markdown
```python
def calculate_area(width, height):
    """Calculate rectangle area."""
    if width > 0 and height > 0:
        return width * height
    return 0

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
```
````

#### 错误示例

````markdown
```python
def calculate_area(width, height):
  """Calculate rectangle area."""  # 缩进只有 2 空格
  if width > 0 and height > 0:
  	return width * height  # Tab 和空格混用
  return 0
```
````

**校验输出：**
```
⚠️  [第 2 行] Python 缩进应为 4 个空格
    💡 建议: 使用 4 个空格缩进

⚠️  [第 4 行] 缩进不应混用 Tab 和空格
    💡 建议: 统一使用空格或 Tab
```

### SQL 语法检查

#### 检查内容

| 检查项 | 说明 | 级别 |
|:-------|:-----|:-----|
| 关键字检查 | 是否包含有效 SQL 关键字 | 警告 |
| 括号配对 | `()` 配对检查 | 错误 |

#### 正确示例

````markdown
```sql
SELECT 
    u.id,
    u.name,
    COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 0
ORDER BY order_count DESC;
```
````

#### 错误示例

````markdown
```sql
SELECT id, name FROM users
WHERE status = 'active'
AND (created_at > '2024-01-01'
ORDER BY name;
```
````

**校验输出：**
```
❌ [第 3 行] 语法错误: 括号不匹配: 1 个 "(" 和 0 个 ")"
    💡 建议: 检查语法并修正
```

### HTML/XML 语法检查

#### 检查内容

| 检查项 | 说明 | 级别 |
|:-------|:-----|:-----|
| 标签配对 | 开始和结束标签配对 | 错误 |
| 自闭合标签 | `<br>`, `<img>` 等自闭合标签 | - |

#### 正确示例

````markdown
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Example</title>
</head>
<body>
    <div class="container">
        <h1>Hello, World!</h1>
        <p>This is a paragraph.</p>
        <img src="image.png" alt="Description">
    </div>
</body>
</html>
```
````

#### 错误示例

````markdown
```html
<div class="container">
    <h1>Hello, World!</h1>
    <p>This is a paragraph.
</div>
```
````

**校验输出：**
```
❌ [第 3 行] 语法错误: 标签 <p> 未闭合
    💡 建议: 检查语法并修正
```

### CSS 语法检查

#### 检查内容

| 检查项 | 说明 | 级别 |
|:-------|:-----|:-----|
| 大括号配对 | `{}` 配对检查 | 错误 |
| 分号结尾 | CSS 属性应以分号结尾 | 警告 |

#### 正确示例

````markdown
```css
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
```
````

#### 错误示例

````markdown
```css
.container {
    max-width: 1200px
    margin: 0 auto;
    padding: 20px;
}
```
````

**校验输出：**
```
⚠️  [第 2 行] 语法警告: CSS 属性应以分号结尾
    💡 建议: 检查语法
```

## 常见错误示例

### 1. JSON 错误

````markdown
❌ 错误:

```json
{
  "name": "John"
  "age": 30,  // 缺少逗号
  "skills": ["JS", "Python",  // 数组未闭合
}
```

✅ 正确:

```json
{
  "name": "John",
  "age": 30,
  "skills": ["JS", "Python"]
}
```
````

### 2. YAML 错误

````markdown
❌ 错误:

```yaml
server:
	port: 8080  # Tab 缩进
  host: localhost
database:
  name:mydb  # 缺少空格
```

✅ 正确:

```yaml
server:
  port: 8080
  host: localhost
database:
  name: mydb
```
````

### 3. JavaScript 错误

````markdown
❌ 错误:

```javascript
function test( {
  return "Hello";
}
```

✅ 正确:

```javascript
function test() {
  return "Hello";
}
```
````

### 4. HTML 错误

````markdown
❌ 错误:

```html
<div>
    <p>Paragraph
</div>
```

✅ 正确:

```html
<div>
    <p>Paragraph</p>
</div>
```
````

## 最佳实践

### 1. 始终指定语言标识

```markdown
✅ 推荐:
```javascript
const x = 10;
```

❌ 不推荐:
```
const x = 10;
```
```

### 2. 保持代码格式一致

- 使用统一的缩进风格（推荐 2 或 4 空格）
- 避免混用 Tab 和空格
- JSON 使用 2 空格缩进
- Python 使用 4 空格缩进

### 3. 提供可运行的代码示例

```markdown
✅ 完整示例:

```javascript
// 计算数组元素之和
function sum(arr) {
  return arr.reduce((a, b) => a + b, 0);
}

// 使用示例
const numbers = [1, 2, 3, 4, 5];
console.log(sum(numbers)); // 输出: 15
```
```

### 4. 添加注释说明

```markdown
✅ 带注释:

```python
def calculate_discount(price, discount_rate):
    """
    计算折扣后的价格
    
    Args:
        price: 原价
        discount_rate: 折扣率 (0-1)
    
    Returns:
        折扣后的价格
    """
    return price * (1 - discount_rate)
```
```

### 5. 使用语法检查工具

在提交文档前，使用校验工具检查代码块：

```bash
# 校验单个文件
npx ts-node scripts/markdown-validator.ts README.md

# 校验多个文件
npx ts-node scripts/markdown-validator.ts *.md
```

### 6. 常见检查清单

- [ ] 所有代码块都指定了语言标识
- [ ] JSON/YAML 语法正确
- [ ] 代码示例可以运行
- [ ] 缩进风格统一
- [ ] 没有拼写错误
- [ ] 注释清晰易懂
