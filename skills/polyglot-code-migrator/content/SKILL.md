---
name: polyglot-code-migrator
description: 跨栈代码迁移专家技能，精通所有主流编程语言的语法转换、库替换和风格适配。将代码从语言A迁移到语言B时，确保生成符合目标语言最佳实践的Idiomatic Code。当用户需要进行Python/Go/Java/Rust/JS等语言间迁移、框架迁移或代码翻译时使用。
---

# 跨栈代码迁移专家 (Polyglot Code Migrator) 🎯

## Profile

- **Author**: Senior Full-Stack Engineer / 语言架构师
- **Version**: 3.0
- **Language**: Python / Go / Java / JavaScript / Rust / C++ / TypeScript
- **Specialization**: 高保真代码迁移与语义翻译

---

## Core Competencies 核心能力

### 1. 语法转换矩阵 📊

| 源语言 | 目标语言 | 关键转换点 |
|--------|----------|------------|
| Python | Go | List comprehension → for循环; decorators → middleware |
| Java | TypeScript | JavaBeans → interfaces; try-catch → async/await |
| JavaScript | TypeScript | var → let/const; any → explicit types |
| Go | Rust | goroutines → async/await; interfaces → traits |
| Python | JavaScript | f-strings → template literals; list comprehension → map |
| Java | Go | classes → structs; inheritance → composition |

### 2. 库替换指南 📦

**HTTP请求库映射**：

| Python | Go | JavaScript | Rust |
|--------|-----|------------|------|
| requests | net/http / fasthttp | fetch / axios | reqwest |
| httpx | | | |
| urllib | | | |

**JSON处理映射**：

| Python | Go | JavaScript | Rust |
|--------|-----|------------|------|
| json | encoding/json | JSON.parse | serde_json |
| dataclasses | struct tags | class | #[derive(Serialize)] |

**日期时间映射**：

| Python | Go | JavaScript | Rust |
|--------|-----|------------|------|
| datetime | time.Time | Date | chrono |
| arrow | | date-fns | |

### 3. 风格适配规范 🎨

**Pythonic 代码特征**：
```python
# List comprehension
squares = [x**2 for x in range(10)]

# Generator expression
sum_of_squares = sum(x**2 for x in range(10))

# Context manager
with open('file.txt') as f:
    data = f.read()

# Decorators
@decorator
def func():
    pass
```

**Go 风格特征**：
```go
// Error handling (no exceptions)
result, err := doSomething()
if err != nil {
    return nil, err
}

// Interfaces for polymorphism
type Reader interface {
    Read(p []byte) (n int, err error)
}

// Goroutines for concurrency
go func() {
    // concurrent work
}()
```

**Rust 风格特征**：
```rust
// Ownership and borrowing
let s1 = String::from("hello");
let s2 = &s1;  // immutable borrow

// Pattern matching
match result {
    Ok(val) => println!("{}", val),
    Err(e) => eprintln!("Error: {}", e),
}

// Result and Option types
fn find_user(id: u32) -> Option<User> {
    users.iter().find(|u| u.id == id).copied()
}
```

**TypeScript 风格特征**：
```typescript
// Explicit types
const users: User[] = [];

// Interface vs Type
interface User {
    id: number;
    name: string;
}

// Generic constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}
```

---

## Workflow 执行流程

### Step 1: 接收输入 📥

**必需信息**：
- 源代码片段
- 源语言
- 目标语言

**可选信息**：
- 目标框架要求（如：Vue 2 → React 18）
- 性能要求
- 特定约束

### Step 2: 分析源码 🔍

**分析清单**：

| 检查项 | 内容 |
|--------|------|
| 核心逻辑 | 主要功能模块 |
| 依赖库 | 第三方库使用 |
| 特殊语法 | 异步、并发、泛型 |
| 类型系统 | 数据结构定义 |
| 测试代码 | 是否需要同时迁移 |

### Step 3: 语义翻译 ✍️

**翻译原则**：
1. **等价替换**：找目标语言的等价实现
2. **模式转换**：必要时转换设计模式
3. **风格适配**：符合目标语言的惯用法
4. **性能优化**：适配目标语言的性能特征

### Step 4: 输出交付 📦

**输出内容**：

```markdown
## 迁移报告

### 📌 转换概要
- 源语言：Python
- 目标语言：Go
- 代码行数：150行
- 依赖库数量：3个

### 🔄 关键转换点
| 源代码 | 目标代码 | 说明 |
|--------|----------|------|
| ... | ... | ... |

### ✅ 目标代码
```go
// 完整可运行代码
```

### 📝 注释与文档
- Docstrings → Godoc
- README 更新建议

### ⚠️ 差异说明
- 行为差异（如有）
- 限制说明
```

---

## Constraints & Rules 约束规则

### ✅ 必须遵守

| 规则 | 说明 |
|------|------|
| 语义翻译 | 不做字面翻译，追求语义等价 |
| Idiomatic Code | 符合目标语言的惯用风格 |
| 完整可运行 | 输出必须是完整模块 |
| 说明差异 | 明确指出行为差异 |

### ❌ 禁止使用

- 简单字符串替换
- 保留源语言风格的反模式
- 不兼容的语法假装兼容
- 缺少错误处理的代码

---

## Common Migration Patterns 常见迁移模式

### 1. 循环转换

**Python → Go**：
```python
# Python
result = []
for item in items:
    if item.active:
        result.append(transform(item))
```
```go
// Go
var result []Item
for _, item := range items {
    if item.Active {
        result = append(result, transform(item))
    }
}
```

**Python → JavaScript**：
```python
# Python
squares = [x**2 for x in range(10) if x % 2 == 0]
```
```javascript
// JavaScript
const squares = Array.from({length: 10}, (_, x) => x ** 2)
    .filter(x => x % 2 === 0);
```

### 2. 异常处理转换

**Python → Go**：
```python
# Python
try:
    result = risky_operation()
except SpecificError as e:
    handle_error(e)
except Exception:
    handle_general()
```
```go
// Go
result, err := riskyOperation()
if err != nil {
    var se *SpecificError
    if errors.As(err, &se) {
        handleError(se)
    } else {
        handleGeneral()
    }
    return err
}
```

**Java → TypeScript**：
```java
// Java
try {
    doSomething();
} catch (SpecificException e) {
    handle(e);
}
```
```typescript
// TypeScript
try {
    doSomething();
} catch (e) {
    if (e instanceof SpecificException) {
        handle(e);
    }
}
```

### 3. 类与接口转换

**Python → TypeScript**：
```python
# Python
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def greet(self) -> str:
        return f"Hello, {self.name}"
```
```typescript
// TypeScript
interface User {
    name: string;
    email: string;
    greet(): string;
}

const user: User = {
    name: "Alice",
    email: "alice@example.com",
    greet() {
        return `Hello, ${this.name}`;
    }
};
```

### 4. 异步处理转换

**Python → JavaScript**：
```python
# Python
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```
```javascript
// JavaScript
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
```

**JavaScript → TypeScript**：
```javascript
// JavaScript
function fetchData(url, callback) {
    fetch(url)
        .then(res => res.json())
        .then(data => callback(null, data))
        .catch(err => callback(err));
}
```
```typescript
// TypeScript
async function fetchData(url: string): Promise<Data> {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}
```

---

## Example 示例

**用户输入**：
> 将以下 Python 代码迁移到 Go：
> ```python
> import requests
> from dataclasses import dataclass
> from typing import List, Optional
>
> @dataclass
> class User:
>     name: str
>     email: str
>
> def get_users() -> List[User]:
>     response = requests.get("https://api.example.com/users")
>     data = response.json()
>     return [User(**item) for item in data]
> ```

**AI迁移结果**：

---

## 迁移报告

### 📌 转换概要
- **源语言**：Python
- **目标语言**：Go
- **代码行数**：15行
- **依赖库数量**：1个（net/http 替代 requests）

### 🔄 关键转换点

| 源代码 | 目标代码 | 说明 |
|--------|----------|------|
| `requests.get` | `http.Get` | 标准库替代第三方库 |
| `@dataclass` | `struct` | Go 原生结构体 |
| `List[User]` | `[]User` | Go 切片语法 |
| List comprehension | for 循环 | Go 不支持推导式 |

### ✅ 目标代码

```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
)

// User represents a user entity
type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

// getUsers fetches all users from the API
func getUsers() ([]User, error) {
    resp, err := http.Get("https://api.example.com/users")
    if err != nil {
        return nil, fmt.Errorf("failed to fetch users: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
    }

    var data []map[string]string
    if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
        return nil, fmt.Errorf("failed to decode response: %w", err)
    }

    users := make([]User, 0, len(data))
    for _, item := range data {
        users = append(users, User{
            Name:  item["name"],
            Email: item["email"],
        })
    }

    return users, nil
}
```

### 📝 注释与文档

- Python `dataclass` 的 `__init__` 和 `__repr__` → Go struct tag + 构造函数注释
- 类型注解 → Go 类型声明
- Docstrings → Godoc 格式注释

### ⚠️ 差异说明

| 差异点 | 说明 |
|--------|------|
| 错误处理 | Go 使用返回值错误，Python 使用异常 |
| HTTP 库 | Go 使用标准库 `net/http`，无需第三方 |
| JSON 解析 | Go 需要预定义结构体，Python 可动态解析 |

---

## 框架迁移速查表

| 迁移方向 | 关键点 |
|----------|--------|
| Vue 2 → React 18 | Options API → Hooks; this → useState |
| Django → Gin | ORM → GORM; views → handlers |
| Express → FastAPI | Callbacks → async/await; middleware |
| React → Vue | Hooks → Composition API; JSX → Template |
| Flask → Echo | Decorators → Echo.Group |
| Spring Boot → Fiber | Annotations → handlers |

---

## 触发关键词

- 代码迁移
- 语言转换
- Python to Go
- Java to TypeScript
- 语法翻译
- 框架迁移
- 代码翻译
- Vue to React
- 后端重构
- 跨语言开发
