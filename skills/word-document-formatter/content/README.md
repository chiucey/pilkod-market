# Word 公文智能格式化工具

## 📋 简介

这是一个智能格式化 Word 公文文档的工具，能够自动识别文档类型（请示、报价函、清单等）并应用统一的格式标准。

## ✨ 功能特点

- ✅ **智能识别** - 自动判断文档类型（请示/报价函/清单/通知）
- ✅ **统一标准** - 所有文档使用相同的格式规范
- ✅ **保持内容** - 只改格式，不改内容
- ✅ **简单易用** - 一键格式化或 AI 辅助
- ✅ **灵活扩展** - 可根据需求调整格式规则

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install python-docx
```

### 2. 使用脚本格式化

```bash
# 自动识别文档类型
python scripts/format_doc.py 原文档.docx 格式化后.docx

# 指定文档类型
python scripts/format_doc.py 原文档.docx 格式化后.docx petition
```

### 3. AI 辅助格式化

直接把 Word 文档发给 AI，说："帮我格式化这个文档"

AI 会：
1. 自动识别文档类型
2. 分析内容结构
3. 应用统一格式
4. 返回格式化建议或生成代码

## 📁 文档类型

### 请示/报告类 (petition)
**关键词**: 请示、报告、批示、妥否、请批示

**格式**:
- 标题：二号加粗居中
- 收件单位：三号顶格
- 正文：小四首行缩进2字符
- 日期：右对齐

### 报价函/询价函 (quotation)
**关键词**: 报价函、询价、比价、控制价、供应商

**格式**:
- 标题：二号加粗居中
- 章节标题：三号加粗
- 条款：小四首行缩进
- 落款：右对齐加粗

### 报价单/清单 (price_list)
**关键词**: 报价单、清单、序号、合计、备注

**格式**:
- 标题：二号加粗居中
- 表格：规范重建（表头加粗浅灰背景）
- 备注：编号清晰
- 签名区：预留位置

### 通用文档 (general)
自动检测并应用基本格式规范

## 📐 格式标准

### 字体
- 中文：微软雅黑 (Microsoft YaHei)
- 英文：Arial

### 字号
- 一级标题：二号 (22pt) + 加粗
- 二级标题：三号 (16pt) + 加粗
- 正文：小四 (12pt)
- 表格：五号 (10.5pt)

### 段落
- 行距：1.5倍
- 正文首行缩进：2字符
- 标题居中，正文两端对齐

## 💡 使用示例

### 示例1：格式化请示文档

```bash
python scripts/format_doc.py "信息技术中心关于采购生产网杀毒软件续期授权的请示.docx" "格式化后-请示.docx" petition
```

### 示例2：格式化报价函

```bash
python scripts/format_doc.py "沈阳机场停车场系统服务器升级项目报价函.docx" "格式化后-报价函.docx" quotation
```

### 示例3：批量处理

```bash
# Windows PowerShell
Get-ChildItem *.docx | ForEach-Object {
    python scripts/format_doc.py $_.Name "formatted_$($_.Name)"
}

# Linux/Mac
for file in *.docx; do
    python scripts/format_doc.py "$file" "formatted_$file"
done
```

## ⚠️ 注意事项

1. **备份原文件** - 格式化前务必备份原始文档
2. **人工检查** - 自动化后务必人工审核关键内容
3. **表格重建** - 复杂表格可能需要手动调整
4. **字体安装** - 确保系统安装了微软雅黑字体
5. **特殊元素** - 图片、公式、图表需单独处理

## 🔧 自定义配置

如需调整格式标准，编辑 `scripts/format_doc.py` 中的以下部分：

```python
# 修改字号
size_map = {
    'heading1': 22,    # 改为其他字号
    'heading2': 16,
    'normal': 12,
}

# 修改字体
self.chinese_font = 'Microsoft YaHei'  # 改为其他字体
```

## 📝 技能集成

这个工具可以作为 Lingma skill 使用：

1. 将整个 `word-document-formatter` 文件夹复制到：
   - 个人：`~/.lingma/skills/word-document-formatter/`
   - 项目：`.lingma/skills/word-document-formatter/`

2. AI 会自动识别并应用此 skill

## 🎯 适用场景

- ✓ 政府机关公文格式化
- ✓ 企事业单位正式文档
- ✓ 请示报告规范化
- ✓ 报价函标准化
- ✓ 清单表格重建
- ✓ 批量文档处理

## 📞 技术支持

如有问题或需要定制功能，请提供：
1. 原始文档示例
2. 期望的格式要求
3. 特殊需求说明

---

**版本**: 1.0  
**更新日期**: 2025年
