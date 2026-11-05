---
name: ppt-notes-extractor
description: 从PowerPoint演示文稿（PPT/PPTX文件）中提取演讲者备注。当用户上传演示文稿并要求提取备注、导出备注、查看每页备注内容时使用。支持按页码+备注格式或标准备注样式导出。
---

# PPT演示文稿备注提取器

## 功能概述

此技能使用Python的python-pptx库提取PowerPoint演示文稿中的演讲者备注（Speaker Notes），并支持多种导出格式。

## 核心功能

1. **提取备注**：从PPTX文件中读取所有幻灯片的备注
2. **页码标注**：为每个备注标注对应的幻灯片页码
3. **格式导出**：支持多种导出格式（文本、Markdown、JSON）
4. **批量处理**：支持处理多个文件

## 技术实现

### 依赖库

```python
from pptx import Presentation
import json
import re
```

### 核心代码逻辑

```python
def extract_notes_from_pptx(pptx_path, output_format='text'):
    """
    从PPTX文件中提取所有幻灯片的备注

    参数:
        pptx_path: PPTX文件路径
        output_format: 输出格式 ('text', 'markdown', 'json')

    返回:
        格式化后的备注内容
    """
    prs = Presentation(pptx_path)
    notes_data = []

    for index, slide in enumerate(prs.slides, start=1):
        notes_slide = slide.notes_slide
        if notes_slide and notes_slide.notes_text_frame:
            notes_text = notes_slide.notes_text_frame.text.strip()
            if notes_text:
                notes_data.append({
                    'slide_number': index,
                    'notes': notes_text
                })

    # 根据输出格式返回结果
    if output_format == 'json':
        return json.dumps(notes_data, ensure_ascii=False, indent=2)
    elif output_format == 'markdown':
        return format_as_markdown(notes_data)
    else:
        return format_as_text(notes_data)

def format_as_text(notes_data):
    """格式化为纯文本"""
    result = []
    for item in notes_data:
        result.append(f"【第 {item['slide_number']} 页】\n{item['notes']}\n")
    return '\n'.join(result)

def format_as_markdown(notes_data):
    """格式化为Markdown"""
    result = ["# 演示文稿备注\n"]
    for item in notes_data:
        result.append(f"## 第 {item['slide_number']} 页\n\n{item['notes']}\n")
    return '\n'.join(result)
```

## 导出格式

### 1. 文本格式 (默认)
```
【第 1 页】
这是第一张幻灯片的备注内容...

【第 2 页】
这是第二张幻灯片的备注内容...
```

### 2. Markdown格式
```markdown
# 演示文稿备注

## 第 1 页

这是第一张幻灯片的备注内容...

## 第 2 页

这是第二张幻灯片的备注内容...
```

### 3. JSON格式
```json
[
  {
    "slide_number": 1,
    "notes": "这是第一张幻灯片的备注内容..."
  },
  {
    "slide_number": 2,
    "notes": "这是第二张幻灯片的备注内容..."
  }
]
```

## 使用示例

### Python代码示例

```python
# 提取单个文件
notes = extract_notes_from_pptx('presentation.pptx', 'markdown')
print(notes)

# 批量提取
import os
for file in os.listdir('.'):
    if file.endswith('.pptx'):
        notes = extract_notes_from_pptx(file)
        with open(f'{file}_notes.txt', 'w', encoding='utf-8') as f:
            f.write(notes)
```

## 注意事项

1. **文件格式**：仅支持PPTX格式（Office 2007+），旧版PPT格式需要转换
2. **备注来源**：只能提取显式添加的备注，非母版备注
3. **编码问题**：确保使用UTF-8编码处理中文内容
4. **空备注处理**：自动跳过没有备注的幻灯片

## 错误处理

```python
try:
    notes = extract_notes_from_pptx('presentation.pptx')
except FileNotFoundError:
    return "错误：文件不存在"
except Exception as e:
    return f"错误：{str(e)}"
```
