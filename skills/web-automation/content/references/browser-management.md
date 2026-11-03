# 浏览器管理模块

## 目录
- [工作场景](#工作场景)
- [工作流程](#工作流程)
- [工作边界](#工作边界)
- [工作结果](#工作结果)
- [调用规范](#调用规范)

---

## 工作场景

需要创建、配置或关闭浏览器实例的场景：
- 需要访问网页进行自动化操作
- 需要截图保存页面状态
- 需要配置代理、用户代理等
- 需要释放浏览器资源

---

## 工作流程

```
1. 创建浏览器实例
   ↓
2. 配置参数（代理、UA、超时等）
   ↓
3. 初始化 Playwright 引擎
   ↓
4. 返回页面句柄
   ↓
5. 执行操作或截图
   ↓
6. 关闭浏览器
```

---

## 工作边界

### 能做
- 创建 Chromium 浏览器实例
- 配置代理（HTTP/SOCKS5）
- 配置自定义 User-Agent
- 全页截图和元素截图
- 无头模式和有头模式切换
- 设置视口大小
- 设置超时时间

### 不能做
- 不能同时管理多个浏览器实例
- 不能跨进程保持会话
- 不能直接操作其他浏览器（Firefox/Safari）
- 不能处理浏览器崩溃后的自动恢复

---

## 工作结果

| 操作 | 成功结果 | 失败结果 |
|------|---------|---------|
| 创建 | 返回页面句柄 | 抛出异常，说明失败原因 |
| 截图 | 返回图片文件路径 | 抛出异常 |
| 关闭 | 资源释放完成 | 抛出异常 |

---

## 调用规范

### 1. 创建浏览器

#### 调用方法
```bash
python scripts/playwright_manager.py create
```

#### 触发条件
- 用户需要访问网页
- 用户需要截图
- 用户开始自动化任务

#### 调用格式
```
--headless: [bool] 是否无头模式，默认 False
--proxy: [str] 代理地址，可选（如 socks5://127.0.0.1:1080）
--user-agent: [str] 自定义 UA，可选
--timeout: [int] 超时时间（秒），默认 30
--viewport-width: [int] 视口宽度，默认 1920
--viewport-height: [int] 视口高度，默认 1080
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--headless` | bool | 否 | False | 是否无头模式。True 表示不显示浏览器窗口 |
| `--proxy` | str | 否 | 空 | 代理地址，格式：`socks5://127.0.0.1:1080` 或 `http://proxy:port` |
| `--user-agent` | str | 否 | 空 | 自定义 User-Agent 字符串 |
| `--timeout` | int | 否 | 30 | 全局超时时间（秒） |
| `--viewport-width` | int | 否 | 1920 | 视口宽度（像素） |
| `--viewport-height` | int | 否 | 1080 | 视口高度（像素） |

#### 结果说明

**成功**：浏览器创建成功，返回页面句柄

**失败**：抛出异常，可能的原因：
- Playwright 未安装
- 系统资源不足
- 代理地址无效
- 参数错误

#### 结果格式

```json
{
  "status": "success|error",
  "message": "浏览器创建成功|错误信息",
  "page_id": "页面句柄",
  "browser_config": {
    "headless": false,
    "proxy": "代理地址",
    "user_agent": "User-Agent 字符串",
    "viewport": {
      "width": 1920,
      "height": 1080
    }
  }
}
```

#### 数据流

```
输入参数 → Playwright 引擎 → 浏览器实例 → 页面句柄 → 返回结果
```

#### 示例

```bash
# 创建有头模式的浏览器
python scripts/playwright_manager.py create --headless=False

# 使用代理创建浏览器
python scripts/playwright_manager.py create \
  --proxy=socks5://127.0.0.1:1080

# 自定义 UA 和视口
python scripts/playwright_manager.py create \
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..." \
  --viewport-width=1366 \
  --viewport-height=768
```

---

### 2. 截图

#### 调用方法
```bash
python scripts/playwright_manager.py screenshot
```

#### 触发条件
- 需要保存页面状态
- 需要进行 OCR 识别
- 需要调试页面
- 需要记录页面变化

#### 调用格式
```
--output-path: [str] 输出文件路径，默认 .web-automation/screenshots/screenshot.png
--selector: [str] CSS 选择器，可选（默认全页截图）
--full-page: [bool] 是否全页截图，默认 False
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--output-path` | str | 否 | .web-automation/screenshots/screenshot.png | 输出文件路径 |
| `--selector` | str | 否 | 空 | CSS 选择器，用于截图指定元素 |
| `--full-page` | bool | 否 | False | 是否全页截图（包含滚动区域） |

#### 结果说明

**成功**：返回截图文件路径

**失败**：抛出异常，可能的原因：
- 浏览器未创建
- 选择器无效
- 输出路径无写入权限

#### 结果格式

```json
{
  "status": "success|error",
  "message": "截图成功|错误信息",
  "output_path": "截图文件路径",
  "size": {
    "width": 1920,
    "height": 1080
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 数据流

```
页面 → 渲染引擎 → 图像数据 → 文件系统 → 返回路径
```

#### 示例

```bash
# 全页截图
python scripts/playwright_manager.py screenshot \
  --output-path=./screenshot.png \
  --full-page=True

# 截图指定元素
python scripts/playwright_manager.py screenshot \
  --output-path=./captcha.png \
  --selector=".captcha"
```

---

### 3. 关闭浏览器

#### 调用方法
```bash
python scripts/playwright_manager.py close
```

#### 触发条件
- 任务完成
- 需要释放资源
- 切换到其他任务
- 发生不可恢复的错误

#### 调用格式
```
无参数
```

#### 结果说明

**成功**：浏览器关闭，所有资源释放

**失败**：抛出异常，可能的原因：
- 浏览器未创建
- 资源释放失败

#### 结果格式

```json
{
  "status": "success|error",
  "message": "浏览器已关闭|错误信息",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 数据流

```
页面句柄 → 资源释放 → 内存清理 → 返回结果
```

#### 示例

```bash
# 关闭浏览器
python scripts/playwright_manager.py close
```

---

## 完整工作流示例

### 场景：访问网站并截图

```bash
# 1. 创建浏览器
python scripts/playwright_manager.py create --headless=False

# 2. 导航到目标网页（需要配合 browser_wrapper）
python scripts/browser_wrapper.py navigate --url=https://example.com

# 3. 截图保存
python scripts/playwright_manager.py screenshot \
  --output-path=./example.png \
  --full-page=True

# 4. 关闭浏览器
python scripts/playwright_manager.py close
```

---

## 注意事项

1. **资源管理**：操作完成后务必关闭浏览器，避免资源泄漏
2. **代理配置**：确保代理地址格式正确（socks5:// 或 http://）
3. **路径权限**：确保截图输出路径有写入权限
4. **视口大小**：设置合适的视口大小以获得最佳渲染效果
5. **超时设置**：根据网络情况调整超时时间
