---
name: webpage-to-image
description: 将网页URL或HTML文件转换为图片格式。当用户要求将网页截图、导出网页为图片、生成网页可视化快照或将本地HTML文件转为图片时使用此技能。
---

# 网页/HTML 转图片技能

## 输入要求

### 必填参数
| 参数 | 类型 | 说明 |
|------|------|------|
| source | string | 网页URL或本地HTML文件路径 |

### 可选参数
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| output_path | string | auto-generated | 输出图片路径 |
| format | string | png | 输出格式: png, jpg, jpeg, webp |
| full_page | boolean | true | 是否截取完整页面 |
| width | number | 1920 | 视口宽度(像素) |
| height | number | auto | 视口高度(像素)，auto时根据内容自适应 |
| quality | number | 90 | 图片质量(1-100)，仅对jpg/webp有效 |
| background_color | string | #ffffff | 背景颜色 |

## 执行流程

1. **解析输入**
   - 验证source是URL还是本地文件路径
   - 验证output_path的目录是否存在

2. **配置浏览器环境**
   - 设置视口尺寸(width x height)
   - 配置背景颜色

3. **渲染网页**
   - 如果是URL，直接导航到页面
   - 如果是本地HTML文件，读取内容后加载到浏览器

4. **等待内容加载**
   - 等待网络空闲
   - 等待DOM稳定

5. **截取图片**
   - 根据full_page参数决定截取方式
   - 应用格式和质量设置

6. **保存输出**
   - 生成输出路径(如果未指定)
   - 保存图片文件

## 输出格式

成功时返回JSON:
```json
{
  "success": true,
  "output_path": "/path/to/output.png",
  "format": "png",
  "dimensions": {
    "width": 1920,
    "height": 10800
  },
  "file_size": 1234567
}
```

失败时返回:
```json
{
  "success": false,
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

## 错误代码

| 代码 | 说明 |
|------|------|
| INVALID_SOURCE | 无效的source参数 |
| SOURCE_NOT_FOUND | 网页URL或文件不存在 |
| RENDER_FAILED | 页面渲染失败 |
| OUTPUT_DIR_NOT_EXISTS | 输出目录不存在 |
| SAVE_FAILED | 保存图片失败 |
| TIMEOUT | 操作超时 |

## 使用示例

### 示例1: 基础用法 - URL转图片
```
输入:
source: "https://example.com"
format: "png"

输出:
output.png (完整页面截图)
```

### 示例2: 本地HTML文件转图片
```
输入:
source: "/path/to/index.html"
output_path: "/path/to/preview.jpg"
format: "jpg"
quality: 85
```

### 示例3: 自定义视口尺寸
```
输入:
source: "https://example.com"
width: 375
height: 812
full_page: false
format: "png"
```
