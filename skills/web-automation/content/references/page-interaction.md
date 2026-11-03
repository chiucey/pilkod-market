# 页面交互模块

## 目录
- [工作场景](#工作场景)
- [工作流程](#工作流程)
- [工作边界](#工作边界)
- [工作结果](#工作结果)
- [调用规范](#调用规范)

---

## 工作场景

需要与网页元素交互的场景：
- 导航到指定 URL
- 点击按钮或链接
- 在输入框中输入文本
- 滚动页面
- 提取页面内容（文本、HTML、属性）

---

## 工作流程

```
1. 确保浏览器已创建
   ↓
2. 执行导航/交互操作
   ↓
3. 等待页面/元素加载完成
   ↓
4. 执行目标操作（点击/输入/滚动）
   ↓
5. 提取结果数据
   ↓
6. 返回结果
```

---

## 工作边界

### 能做
- 导航到任意 URL
- 通过 CSS 选择器定位元素
- 点击、输入、滚动等基本交互
- 提取文本、HTML、属性
- 等待特定元素出现

### 不能做
- 不能处理复杂的验证码（需要配合 OCR）
- 不能绕过强反爬（需要配合代理和人机模拟）
- 不能处理需要高级交互的场景（如 Canvas 绘图）
- 不能直接执行 JavaScript（需要扩展）

---

## 工作结果

| 操作 | 成功结果 | 失败结果 |
|------|---------|---------|
| 导航 | 返回页面标题和 URL | 超时或 URL 无效 |
| 点击 | 元素被点击 | 元素不存在或不可点击 |
| 输入 | 文本输入完成 | 元素不存在或不可输入 |
| 提取 | 返回提取的内容 | 元素不存在 |

---

## 调用规范

### 1. 导航

#### 调用方法
```bash
python scripts/browser_wrapper.py navigate
```

#### 触发条件
- 用户需要访问网页
- 需要跳转到指定 URL

#### 调用格式
```
--url: [str] 目标 URL，必需
--wait-for-selector: [str] 等待的 CSS 选择器，可选
--timeout: [int] 超时时间（秒），默认 30
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--url` | str | 是 | - | 目标网页 URL（http:// 或 https://） |
| `--wait-for-selector` | str | 否 | 空 | 等待元素出现的 CSS 选择器 |
| `--timeout` | int | 否 | 30 | 超时时间（秒） |

#### 结果说明

**成功**：页面加载完成

**失败**：超时或 URL 无效，可能的原因：
- URL 无法访问
- 网络超时
- 选择器等待超时

#### 结果格式

```json
{
  "status": "success|error",
  "message": "导航成功|错误信息",
  "url": "当前 URL",
  "title": "页面标题",
  "load_time": 2.5
}
```

#### 数据流

```
URL → 网络请求 → 页面渲染 → 返回结果
```

#### 示例

```bash
# 基本导航
python scripts/browser_wrapper.py navigate --url=https://example.com

# 导航并等待元素
python scripts/browser_wrapper.py navigate \
  --url=https://example.com \
  --wait-for-selector=.content

# 自定义超时
python scripts/browser_wrapper.py navigate \
  --url=https://example.com \
  --timeout=60
```

---

### 2. 点击

#### 调用方法
```bash
python scripts/browser_wrapper.py click
```

#### 触发条件
- 需要点击按钮或链接
- 需要触发交互

#### 调用格式
```
--selector: [str] CSS 选择器，必需
--timeout: [int] 超时时间（秒），默认 10
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--selector` | str | 是 | - | 目标元素的 CSS 选择器 |
| `--timeout` | int | 否 | 10 | 等待元素的超时时间（秒） |

#### 结果说明

**成功**：元素被点击

**失败**：元素不存在或不可点击，可能的原因：
- 选择器无效
- 元素未加载
- 元素被覆盖
- 元素不可见

#### 结果格式

```json
{
  "status": "success|error",
  "message": "点击成功|错误信息",
  "selector": "使用的 CSS 选择器"
}
```

#### 数据流

```
选择器 → 元素定位 → 点击事件 → 返回结果
```

#### 示例

```bash
# 点击按钮
python scripts/browser_wrapper.py click --selector=".submit-btn"

# 点击链接
python scripts/browser_wrapper.py click --selector="a.next-page"
```

---

### 3. 输入

#### 调用方法
```bash
python scripts/browser_wrapper.py fill
```

#### 触发条件
- 需要在输入框中输入文本
- 需要填写表单

#### 调用格式
```
--selector: [str] CSS 选择器，必需
--text: [str] 输入文本，必需
--timeout: [int] 超时时间（秒），默认 10
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--selector` | str | 是 | - | 输入框的 CSS 选择器 |
| `--text` | str | 是 | - | 要输入的文本内容 |
| `--timeout` | int | 否 | 10 | 等待元素的超时时间（秒） |

#### 结果说明

**成功**：文本输入完成

**失败**：元素不存在或不可输入，可能的原因：
- 选择器无效
- 元素不是输入框
- 元素被禁用

#### 结果格式

```json
{
  "status": "success|error",
  "message": "输入成功|错误信息",
  "selector": "使用的 CSS 选择器",
  "text": "输入的文本"
}
```

#### 数据流

```
选择器 + 文本 → 元素定位 → 输入事件 → 返回结果
```

#### 示例

```bash
# 输入文本
python scripts/browser_wrapper.py fill \
  --selector="#username" \
  --text="user123"

# 填写密码
python scripts/browser_wrapper.py fill \
  --selector="#password" \
  --text="password123"
```

---

### 4. 提取

#### 调用方法
```bash
python scripts/browser_wrapper.py extract
```

#### 触发条件
- 需要提取页面文本
- 需要获取 HTML 内容
- 需要读取元素属性

#### 调用格式
```
--selector: [str] CSS 选择器，必需
--type: [str] 提取类型，可选（text|html|attr），默认 text
--attribute: [str] 属性名称，type=attr 时必需
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--selector` | str | 是 | - | 目标元素的 CSS 选择器 |
| `--type` | str | 否 | text | 提取类型：text（文本）、html（HTML）、attr（属性） |
| `--attribute` | str | 否 | - | 属性名称（type=attr 时必需） |

#### 结果说明

**成功**：返回提取的内容

**失败**：元素不存在，可能的原因：
- 选择器无效
- 元素未加载
- 属性名称错误

#### 结果格式

```json
{
  "status": "success|error",
  "message": "提取成功|错误信息",
  "content": "提取的内容",
  "selector": "使用的 CSS 选择器",
  "type": "text|html|attr"
}
```

#### 数据流

```
选择器 → 元素定位 → 内容提取 → 返回结果
```

#### 示例

```bash
# 提取文本
python scripts/browser_wrapper.py extract \
  --selector=".content" \
  --type=text

# 提取 HTML
python scripts/browser_wrapper.py extract \
  --selector=".product-card" \
  --type=html

# 提取属性
python scripts/browser_wrapper.py extract \
  --selector="img.logo" \
  --type=attr \
  --attribute=src
```

---

## 完整工作流示例

### 场景：登录网站

```bash
# 1. 创建浏览器
python scripts/playwright_manager.py create --headless=False

# 2. 导航到登录页
python scripts/browser_wrapper.py navigate --url=https://example.com/login

# 3. 输入用户名
python scripts/browser_wrapper.py fill \
  --selector="#username" \
  --text="user123"

# 4. 输入密码
python scripts/browser_wrapper.py fill \
  --selector="#password" \
  --text="password123"

# 5. 点击登录按钮
python scripts/browser_wrapper.py click --selector=".login-btn"

# 6. 等待登录成功
python scripts/browser_wrapper.py navigate \
  --wait-for-selector=".user-profile"

# 7. 提取用户信息
python scripts/browser_wrapper.py extract \
  --selector=".user-profile" \
  --type=text

# 8. 关闭浏览器
python scripts/playwright_manager.py close
```

---

## 注意事项

1. **元素等待**：使用 `--wait-for-selector` 确保元素加载完成
2. **选择器准确性**：确保 CSS 选择器唯一且正确
3. **超时设置**：根据页面加载速度调整超时时间
4. **异常处理**：遇到元素不存在时应检查选择器和加载状态
5. **文本编码**：特殊字符可能需要转义
