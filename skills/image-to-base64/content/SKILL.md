---
name: image-to-base64
description: 将图片文件转换为Base64编码字符串。当用户上传图片并需要其Base64表示时使用，支持PNG、JPG、GIF、WebP等常见图片格式。
---

# 图片转Base64编码器

## 功能说明

这是一个强大的图片转Base64工具，支持拖拽上传、点击选择、批量处理、多种输出格式预览，以及一键复制功能。

## 核心特性

- **拖拽上传**：支持将图片直接拖拽到上传区域
- **点击上传**：点击按钮选择本地图片文件
- **批量处理**：支持同时转换多张图片
- **多种格式预览**：显示Data URL、纯Base64字符串、HTML img标签、Markdown图片等多种格式
- **一键复制**：点击即可复制任意格式的编码结果
- **实时预览**：转换后立即显示原图预览
- **格式信息**：显示图片尺寸、文件大小、MIME类型等详细信息

## 支持的图片格式

- PNG (.png)
- JPEG/JPG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)
- SVG (.svg)
- ICO (.ico)

## 使用方法

1. 上传图片（拖拽或点击选择）
2. 系统自动转换为Base64编码
3. 查看多种格式的输出结果
4. 点击复制按钮获取所需格式

## 输出格式示例

### Data URL格式
```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
```

### 纯Base64字符串
```
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
```

### HTML img标签
```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" alt="Image">
```

### Markdown格式
```markdown
![Image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==)
```

## 技术实现

- 纯前端处理，保护用户隐私
- 使用HTML5 FileReader API读取图片
- 使用Canvas获取图片尺寸信息
- 自动检测MIME类型

## 注意事项

- Base64编码会使文件大小增加约33%
- 大图片的Base64字符串会非常长
- 纯前端处理，无需上传到服务器
