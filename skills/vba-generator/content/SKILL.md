---
name: vba-generator
description: PPT VBA代码生成专家，能够根据用户提供的PPT大纲自动生成可运行的VBA代码，快速创建幻灯片结构、填充内容和设置格式。支持PowerPoint和WPS平台。当用户要求PPT VBA、VBA代码、PowerPoint VBA、WPS VBA、自动生成PPT、批量生成PPT、PPT宏、幻灯片自动化、VBA脚本时使用。
---

# PPT VBA代码生成器

## 技能概述

PPT VBA代码生成专家，能够根据用户提供的PPT大纲自动生成可运行的VBA代码，快速创建幻灯片结构、填充内容和设置格式。支持PowerPoint和WPS平台。

## 核心能力

- 根据大纲自动生成完整VBA代码
- 支持创建多种幻灯片类型
- 批量插入文本和图片
- 自动应用样式和格式
- 支持PowerPoint和WPS双平台
- 提供详细的使用说明
- 包含常见问题解答
- 支持代码注释和说明

## 支持的操作

- 创建/删除幻灯片
- 设置幻灯片布局
- 插入文本框和设置格式
- 插入图片和调整位置
- 创建表格和图表
- 设置幻灯片母版
- 批量处理多张幻灯片
- 导出和保存操作

## 平台支持

### PowerPoint
- API: PPTX Object Model
- 文件扩展名: .pptm, .pptx
- 说明: 支持完整的VBA编程

### WPS
- API: ET Object Model
- 文件扩展名: .wps, .et
- 说明: 兼容大部分PowerPoint VBA语法

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| outline | object | 是 | - | PPT大纲结构 |
| platform | enum | 否 | PowerPoint | 目标平台：PowerPoint/WPS/Both |
| template_file | string | 否 | - | 模板文件路径（可选） |
| content | object | 否 | - | 各页面内容 |
| styling | object | 否 | - | 样式设置 |

## 输出结构

```json
{
  "vba_code": "生成的VBA代码",
  "instructions": ["使用说明数组"],
  "troubleshooting": ["常见问题解答数组"]
}
```

## 代码模板

### 创建幻灯片
```vba
Sub CreateSlide(title As String, content As String, slideType As String)
    ' Create a new slide with specified content
End Sub
```

### 设置样式
```vba
Sub SetSlideStyle(slideIndex As Integer, bgColor As Long, fontColor As Long)
    ' Apply styling to a slide
End Sub
```

### 插入图片
```vba
Sub InsertImage(slideIndex As Integer, imagePath As String, position As String)
    ' Insert image into slide
End Sub
```

### 批量创建
```vba
Sub BatchCreateSlides(outlineData As Variant)
    ' Batch create multiple slides from data
End Sub
```

## 使用示例

**示例1：基础VBA生成**
- 输入：生成VBA代码：5页PPT，第一页封面，第二页目录，第三到五页内容页
- 输出：完整的VBA代码，包含创建幻灯片、设置样式、插入内容的函数和示例调用

**示例2：批量生成**
- 输入：需要批量生成100张产品介绍幻灯片，模板文件是template.pptx
- 输出：批量处理VBA代码，支持从Excel读取产品数据并自动填充到模板

## 最佳实践

1. 提供清晰的PPT大纲结构
2. 指定目标平台（PowerPoint/WPS）
3. 如有模板文件，附带说明
4. 明确内容填充的数据源
5. 说明需要的样式效果

## 相关技能

- pptx_generator
- slide_designer
- html-presentation-generator
