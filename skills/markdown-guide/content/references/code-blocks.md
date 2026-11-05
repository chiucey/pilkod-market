# Markdown 代码块使用指南

## 目录

1. [行内代码](#行内代码)
2. [代码块基础](#代码块基础)
3. [语言标识](#语言标识)
4. [高级特性](#高级特性)
5. [最佳实践](#最佳实践)

## 行内代码

### 语法

使用单个反引号包裹：

```markdown
这是 `行内代码` 示例。
```

### 使用场景

- 函数名、变量名：`getUserInfo()`
- 命令名称：`npm install`
- 文件路径：`/usr/local/bin`
- 短代码片段：`const x = 10;`

### 包含反引号的行内代码

使用双反引号包裹：

```markdown
``包含`反引号的代码``
```

## 代码块基础

### 基本语法

使用三个反引号包裹：

````markdown
```
代码内容
```
````

### 示例

````markdown
```javascript
function hello() {
  console.log("Hello, World!");
}
```
````

## 语言标识

### 为什么指定语言

1. **语法高亮**：提高代码可读性
2. **复制功能**：部分渲染器支持一键复制
3. **语义化**：明确代码类型

### 常用语言标识

| 语言 | 标识符 | 示例 |
|------|--------|------|
| JavaScript | `javascript` 或 `js` | ```js |
| TypeScript | `typescript` 或 `ts` | ```ts |
| Python | `python` 或 `py` | ```python |
| Java | `java` | ```java |
| C/C++ | `c`, `cpp` | ```cpp |
| Go | `go` | ```go |
| Rust | `rust` | ```rust |
| HTML | `html` | ```html |
| CSS | `css` | ```css |
| SQL | `sql` | ```sql |
| Shell/Bash | `shell`, `bash`, `sh` | ```bash |
| JSON | `json` | ```json |
| YAML | `yaml` 或 `yml` | ```yaml |
| Markdown | `markdown` 或 `md` | ```markdown |
| Dockerfile | `dockerfile` | ```dockerfile |

### 示例展示

**JavaScript：**
````markdown
```javascript
const greeting = (name) => {
  return `Hello, ${name}!`;
};

console.log(greeting("World"));
```
````

**Python：**
````markdown
```python
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
```
````

**Bash：**
````markdown
```bash
#!/bin/bash

# 安装依赖
npm install

# 启动服务
npm start
```
````

**SQL：**
````markdown
```sql
SELECT 
    users.name,
    orders.product,
    orders.amount
FROM users
JOIN orders ON users.id = orders.user_id
WHERE orders.created_at > '2024-01-01'
ORDER BY orders.amount DESC;
```
````

## 高级特性

### 1. 显示文件名

部分平台支持在语言标识后添加文件名：

````markdown
```javascript:app.js
const app = require('express')();

app.get('/', (req, res) => {
  res.send('Hello World');
});

app.listen(3000);
```
````

### 2. 行号显示

部分 Markdown 渲染器支持显示行号（需要配置）：

````markdown
```javascript {.line-numbers}
function add(a, b) {
  return a + b;
}
```
````

### 3. 高亮特定行

使用 `{数字}` 或 `{开始-结束}` 高亮行：

````markdown
```javascript {2,4-5}
function example() {
  console.log("这一行会被高亮");  // 高亮
  const x = 10;
  const y = 20;  // 高亮
  return x + y;  // 高亮
}
```
````

### 4. 折叠代码块

使用 `<details>` 标签实现折叠：

```markdown
<details>
<summary>点击展开代码</summary>

```python
def hidden_function():
    return "这段代码默认折叠"
```

</details>
```

### 5. Diff 显示

使用 `diff` 语言显示差异：

````markdown
```diff
- const oldCode = "旧代码";
+ const newCode = "新代码";
```
````

### 6. 代码块嵌套

使用更多反引号包裹：

`````markdown
````markdown
```javascript
// 这是嵌套的代码块示例
```
````
`````

## 最佳实践

### 1. 始终指定语言

**不推荐：**
````markdown
```
function example() {
  return "没有语言标识";
}
```
````

**推荐：**
````markdown
```javascript
function example() {
  return "有语言标识，支持语法高亮";
}
```
````

### 2. 代码块前后添加空行

**不推荐：**
```markdown
这是一段文字。
```python
print("代码块")
```
这是另一段文字。
```

**推荐：**
```markdown
这是一段文字。

```python
print("代码块")
```

这是另一段文字。
```

### 3. 添加代码说明

**推荐：**
````markdown
以下代码演示了如何使用 async/await 处理异步操作：

```javascript
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    const user = await response.json();
    return user;
  } catch (error) {
    console.error('获取用户失败:', error);
  }
}
```

**代码说明：**
- 使用 `async/await` 语法
- 包含错误处理
- 返回用户对象
````

### 4. 保持代码简洁

- 移除不必要的空白行
- 避免过长的代码（超过 30 行考虑拆分）
- 使用有意义的变量名

### 5. 命令示例包含输出

**推荐：**
````markdown
```bash
$ npm install lodash
+ lodash@4.17.21
added 1 package in 2.5s
```
````

### 6. 配置文件示例

**JSON：**
````markdown
```json
{
  "name": "my-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2"
  }
}
```
````

**YAML：**
````markdown
```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
```
````

## 常见错误

### 错误 1：缺少语言标识

```markdown
```
const x = 10;
```
```

**修正：** 添加语言标识 `javascript` 或 `js`

### 错误 2：反引号数量不匹配

````markdown
```javascript
const x = 10;
````
````

**修正：** 确保开头和结尾的反引号数量一致

### 错误 3：代码块未正确闭合

````markdown
```javascript
const x = 10;
继续写文字...
````

**修正：** 代码块必须使用三个反引号单独一行闭合

### 错误 4：语言标识拼写错误

````markdown
```javscript
const x = 10;
```
````

**修正：** 正确拼写为 `javascript`

## 快速参考

| 需求 | 语法 |
|------|------|
| 行内代码 | `` `code` `` |
| 代码块 | ```` ``` ```` 包裹 |
| 指定语言 | ```` ```javascript ```` |
| 显示文件名 | ```` ```javascript:app.js ```` |
| 高亮行 | ```` ```javascript {2,4-5} ```` |
| 折叠代码 | `<details>` 标签 |
| Diff 显示 | ```` ```diff ```` |
