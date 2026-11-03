---
name: ppt-notes-importer
description: 批量将备注文件导入PowerPoint演示文稿。当用户需要将文本备注批量添加到PPT幻灯片中，或将独立的备注文件导入到演示文稿时使用。触发短语：导入备注、批量导入PPT备注、添加演讲者备注、notes导入、备注文件导入。
---

# PPT备注导入技能

批量将备注文件导入到PowerPoint演示文稿中。

## 工作流程

### 步骤1：确认文件格式

**重要**：在处理前，务必检查用户提供的备注文件是否符合格式规范。

查看格式规范：
```
/workspace/temp-skills/ppt-notes-importer/references/format_guide.md
```

### 步骤2：收集文件信息

用户需要提供：
1. PowerPoint文件（.ppt或.pptx）
2. 备注文件（建议.txt格式）

### 步骤3：执行导入

使用Python脚本执行批量导入：

```bash
python /workspace/temp-skills/ppt-notes-importer/scripts/import_notes.py <pptx文件路径> <备注文件夹路径> [--output <输出文件夹>]
```

### 步骤4：验证结果

脚本运行后，检查输出文件夹中的文件，确认备注已正确导入。

## 格式规范摘要

备注文件命名规范：`[序号]_[可选描述].txt`
- 序号必须与幻灯片顺序对应
- 例如：`01.txt`、`02_intro.txt`、`03_main_content.txt`

每行对应一个幻灯片的备注内容。

## 输出

生成带有备注的新PowerPoint文件，保存在指定输出目录。
