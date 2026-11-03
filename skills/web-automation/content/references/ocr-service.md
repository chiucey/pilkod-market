# OCR 服务模块

## 目录
- [工作场景](#工作场景)
- [工作流程](#工作流程)
- [工作边界](#工作边界)
- [工作结果](#工作结果)
- [调用规范](#调用规范)

---

## 工作场景

需要从图片中提取信息的场景：
- 识别验证码
- 提取图片中的文字
- 从截图提取表格
- 检测特定元素（按钮、文本）

---

## 工作流程

```
1. 确保有图片文件（截图或上传）
   ↓
2. 调用 PaddleOCR 引擎
   ↓
3. 执行识别（文字/表格/元素）
   ↓
4. 返回识别结果
```

---

## 工作边界

### 能做
- 中英文文字识别
- 表格结构识别
- 元素检测（按钮、文本框）
- 验证码识别（简单）
- 置信度评估

### 不能做
- 不能识别复杂手写体
- 不能识别模糊图片（需要预处理）
- 不能处理大尺寸图片（性能限制）
- 不能识别旋转文字（需要预处理）
- 不能处理多语言混合文本（性能下降）

---

## 工作结果

| 操作 | 成功结果 | 失败结果 |
|------|---------|---------|
| 文字识别 | 返回文字内容和置信度 | 图片不存在或无法识别 |
| 表格提取 | 返回结构化表格数据 | 图片不存在或无法识别表格 |
| 元素检测 | 返回检测到的元素列表 | 图片不存在或无法检测 |

---

## 调用规范

### 1. 文字识别

#### 调用方法
```bash
python scripts/ocr_service.py recognize
```

#### 触发条件
- 需要识别图片中的文字
- 需要读取验证码

#### 调用格式
```
--image-path: [str] 图片路径，必需
--language: [str] 语言，可选（ch|en），默认 ch
--gpu: [bool] 是否使用 GPU，默认 False
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--image-path` | str | 是 | - | 图片文件路径（PNG/JPG/JPEG） |
| `--language` | str | 否 | ch | 语言：ch（中文）、en（英文） |
| `--gpu` | bool | 否 | False | 是否使用 GPU 加速 |

#### 结果说明

**成功**：返回识别的文字内容

**失败**：图片不存在或无法识别，可能的原因：
- 图片文件不存在
- 图片格式不支持
- 图片质量过低
- 无文字内容

#### 结果格式

```json
{
  "status": "success|error",
  "message": "识别成功|错误信息",
  "text": "识别的文字内容",
  "confidence": 0.95,
  "regions": [
    {
      "text": "文字块1",
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.95
    }
  ],
  "processing_time": 0.5
}
```

#### 数据流

```
图片文件 → OCR 引擎 → 文字识别 → 返回结果
```

#### 示例

```bash
# 识别中文文字
python scripts/ocr_service.py recognize \
  --image-path=./screenshot.png \
  --language=ch

# 识别英文验证码
python scripts/ocr_service.py recognize \
  --image-path=./captcha.png \
  --language=en

# 使用 GPU 加速
python scripts/ocr_service.py recognize \
  --image-path=./image.png \
  --language=ch \
  --gpu=True
```

---

### 2. 表格提取

#### 调用方法
```bash
python scripts/ocr_service.py extract-table
```

#### 触发条件
- 需要从图片提取表格
- 需要结构化表格数据

#### 调用格式
```
--image-path: [str] 图片路径，必需
--output-format: [str] 输出格式，可选（markdown|json|csv），默认 markdown
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--image-path` | str | 是 | - | 图片文件路径 |
| `--output-format` | str | 否 | markdown | 输出格式：markdown、json、csv |

#### 结果说明

**成功**：返回表格数据

**失败**：图片不存在或无法识别表格，可能的原因：
- 图片文件不存在
- 无表格结构
- 表格过于复杂

#### 结果格式

```json
{
  "status": "success|error",
  "message": "提取成功|错误信息",
  "tables": [
    {
      "headers": ["列1", "列2", "列3"],
      "rows": [
        ["数据1", "数据2", "数据3"],
        ["数据4", "数据5", "数据6"]
      ],
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "table_count": 1,
  "processing_time": 1.5
}
```

#### 数据流

```
图片文件 → OCR 引擎 → 表格检测 → 返回结果
```

#### 示例

```bash
# 提取为 Markdown
python scripts/ocr_service.py extract-table \
  --image-path=./table.png \
  --output-format=markdown

# 提取为 JSON
python scripts/ocr_service.py extract-table \
  --image-path=./table.png \
  --output-format=json
```

---

## 完整工作流示例

### 场景：验证码识别

```bash
# 1. 创建浏览器
python scripts/playwright_manager.py create

# 2. 导航到登录页
python scripts/browser_wrapper.py navigate --url=https://example.com/login

# 3. 截图验证码区域
python scripts/playwright_manager.py screenshot \
  --output-path=./captcha.png \
  --selector=".captcha"

# 4. OCR 识别验证码
python scripts/ocr_service.py recognize \
  --image-path=./captcha.png \
  --language=en

# 5. 输入验证码
python scripts/browser_wrapper.py fill \
  --selector="#captcha" \
  --text="<识别结果>"

# 6. 关闭浏览器
python scripts/playwright_manager.py close
```

### 场景：表格提取

```bash
# 1. 截图表格
python scripts/playwright_manager.py screenshot \
  --output-path=./table.png \
  --selector=".data-table"

# 2. 提取表格
python scripts/ocr_service.py extract-table \
  --image-path=./table.png \
  --output-format=json

# 3. 处理表格数据（由智能体完成）
```

---

## 注意事项

1. **图片质量**：确保图片清晰度，避免模糊或过小的图片
2. **语言设置**：根据图片内容选择正确的语言模式
3. **GPU 加速**：处理大量图片时建议启用 GPU
4. **性能优化**：缓存识别结果，避免重复处理
5. **预处理**：复杂图片可能需要预处理（旋转、裁剪、增强对比度）
