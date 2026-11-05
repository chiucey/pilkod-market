---
name: pdf-to-image
description: 将PDF文档转换为图片格式。当用户要求将PDF转图片、PDF转PNG、PDF转JPEG、提取PDF页面为图片时使用。
---

# PDF 转图片技能

将PDF文件的每一页转换为高质量图片（PNG或JPEG格式）。

## 工作流程

1. **接收PDF文件**
   - 获取用户提供的PDF文件路径或URL
   - 确认输出格式（PNG/JPEG）和图片质量

2. **执行转换**
   - 使用Python脚本 `scripts/pdf_to_images.py` 进行转换
   - 支持指定DPI（默认300）、输出格式、输出目录

3. **返回结果**
   - 返回生成的图片文件路径列表
   - 报告转换成功的页面数量

## 使用方式

```
输入: PDF文件路径 [, 输出格式: png/jpeg] [, DPI: 数值] [, 输出目录]
输出: 图片文件路径列表
```

## 示例

- 用户说："把这个PDF转成图片"
- 用户说："PDF转PNG，高清300DPI"
- 用户说："将PDF的每一页转换为JPEG图片"

## 脚本调用

```bash
python scripts/pdf_to_images.py <pdf_path> [--output-dir <dir>] [--format png|jpeg] [--dpi <number>]
```

## 依赖

- Python 3.x
- pdf2image (Poppler后端)
- Pillow

安装依赖：`pip install pdf2image Pillow`（Linux需安装poppler-utils）
