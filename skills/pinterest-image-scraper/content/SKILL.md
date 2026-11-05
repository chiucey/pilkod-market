---
name: pinterest-image-scraper
description: Pinterest 图片抓取器。当用户要求下载 Pinterest 图片、按关键词/类别抓取图片、批量下载 Pinterest 图片集、或者需要将 Pinterest 图片归档整理时使用。
---

# Pinterest 图片抓取器

从 Pinterest 网站按关键词和类别下载并归档图片。

## 工作流程

### 1. 信息收集

当用户触发技能时，执行以下操作：

1. **获取关键词和类别**
   - 从用户请求中提取关键词（如 "风景"、"时尚"、"美食"）
   - 确定下载数量（默认 20 张，可调整）
   - 确认是否需要特定尺寸或质量

2. **确定归档结构**
   - 按类别创建文件夹
   - 命名格式：`{类别}_{关键词}_{日期}`
   - 在 `downloads/pinterest/{类别}/` 下组织

### 2. 图片搜索与下载

使用 `batch_web_search` 和 `images_search_and_download` 工具：

1. **搜索 Pinterest 图片**
   - 搜索关键词：`site:pinterest.com {关键词}`
   - 过滤高质量图片源

2. **下载图片**
   - 使用 `images_search_and_download` 批量下载
   - 设置适当的任务名称便于追踪
   - 保存到指定归档目录

### 3. 归档整理

下载完成后：

1. **整理文件结构**
   ```
   downloads/
   └── pinterest/
       └── {类别}/
           ├── images/
           │   ├── image_001.jpg
           │   └── ...
           └── metadata.json
   ```

2. **生成元数据**
   - 记录下载时间、关键词、来源
   - 保存图片尺寸和格式信息
   - 生成下载报告

## 输出格式

技能执行完成后，输出：
- 下载的图片数量和总大小
- 文件保存路径
- 下载失败的项目（如有）

## 示例用法

**用户输入**: "下载风景类图片 30 张"

**执行**:
1. 搜索 `site:pinterest.com 风景 nature landscape`
2. 下载 30 张高质量风景图片
3. 归档到 `downloads/pinterest/风景/`
4. 生成元数据和下载报告

**输出**:
```
✅ Pinterest 图片下载完成
- 类别: 风景
- 下载数量: 30 张
- 保存位置: downloads/pinterest/风景/
- 总大小: XX MB
```

## 限制说明

- 遵守网站使用条款和版权规定
- 仅下载公开可访问的图片
- 不用于商业批量抓取目的
