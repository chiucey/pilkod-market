---
name: official-document
description: 生成符合中国政府公文标准格式的Word文档，支持标题分级、字体字号、段落格式、行距等全套公文排版规范
description_zh: "中国政府公文格式Word文档生成工具"
description_en: "Generate Word documents in official Chinese government document format"
version: 1.0.0
---

# 公文格式技能

本技能用于生成符合中国政府公文标准格式（GB/T 9704-2012）的Word文档。

## 公文格式规范

### 字号与字体

| 级别 | 字号 | 字体 | 加粗 | 对齐 |
|------|------|------|------|------|
| 一级标题 | 2号（约22磅） | 方正小标宋简体 | 否 | 居中 |
| 二级标题 | 3号（约16磅） | 黑体 | 否 | 两端对齐 |
| 三级标题 | 3号（约16磅） | 楷体_GB2312 | 是 | 两端对齐 |
| 四级标题 | 3号（约16磅） | 仿宋_GB2312 | 是 | 两端对齐 |
| 正文 | 3号（约16磅） | 仿宋_GB2312 | 否 | 两端对齐 |

### 段落格式

- 左右缩进：0字符
- 首行缩进：2字符（仅正文）
- 段前间距：0行
- 段后间距：0行
- 行距：固定值28磅

### 页面设置

- 纸张：A4
- 页边距：上下2.54厘米，左右3.17厘米

## 使用方法

### Python脚本调用

```python
from official_document import OfficialDocument

# 创建文档
doc = OfficialDocument()

# 添加标题（会自动应用对应级别格式）
doc.add_heading("文件标题", level=1)  # 一级标题
doc.add_heading("第一章  总则", level=2)  # 二级标题
doc.add_heading("第一条", level=3)  # 三级标题
doc.add_heading("（一）", level=4)  # 四级标题

# 添加正文
doc.add_paragraph("这是正文内容，需要首行缩进两个字符。")

# 保存文档
doc.save("公文.docx")
```

### 命令行调用

```bash
python official_document.py --title "公文标题" --content "正文内容" --output "公文.docx"
```

## 格式说明

本技能基于 `python-docx` 库实现，自动处理：
- 中文字体嵌入（WPS/Office兼容）
- 公文标准行距（固定值28磅）
- 标题分级自动格式化
- 正确的首行缩进

### 注意事项

1. 方正小标宋简体需要系统安装该字体
2. 如字体缺失，程序会自动回退到黑体
3. 生成的文档建议用WPS或Microsoft Word打开查看
