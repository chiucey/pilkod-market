# Content Extraction Guide - 多格式内容提取

本指南说明如何从不同格式的文件中提取核心内容，为PPT生成提供素材。

---

## 支持的文件格式

| 格式 | 工具/方法 | 说明 |
|------|----------|------|
| 纯文字 | 直接分析对话内容 | 用户输入的描述或文本 |
| Word (.docx) | `python -m markitdown` | 文本提取，保留结构 |
| PPT (.pptx) | `python -m markitdown` | 文本提取，识别页面 |
| Excel (.xlsx) | openpyxl | 数据表格读取 |
| PDF (.pdf) | `mcp__matrix__extract_pdfs_full_content` | 完整内容提取 |

---

## 模板风格提取

### 关键原则

> **禁止忽略用户传入的模板。必须提取模板配色后再生成PPT。**

### 提取步骤

**第一步：解压PPTX文件**
```bash
unzip -o "模板.pptx" -d temp_template_extracted/
```

**第二步：读取主题配色方案**
读取 `ppt/theme/theme1.xml`，解析 `<a:clrScheme>` 标签获取标准配色。

**颜色映射规则**：
| XML标签 | 颜色用途 | 映射到主题键 |
|---------|----------|-------------|
| `dk2` | 深色（标题） | `primary` |
| `lt2` | 浅色（背景） | `bg` |
| `accent1` | 强调色1 | `accent` |

**第三步：读取实际幻灯片配色**
读取 `ppt/slides/slide*.xml`，提取 `a:srgbClr val="XXXXXX"` 中的颜色值。

**第四步：映射到主题键**
```javascript
const theme = {
  primary: extractedPrimary,
  secondary: extractedSecondary,
  accent: extractedAccent,
  light: extractedLight,
  bg: extractedBg
};
```

---

## 常见问题

**Q: 提取的颜色太多怎么办？**
A: 优先使用 `theme1.xml` 中的标准配色，这是模板作者定义的品牌色。

**Q: 如何判断哪个是主色调？**
A: 通常 `dk2` 或 `accent1` 是主色调。

**Q: 深色模板如何处理？**
A: 交换映射：`bg` = 深色，`primary` = 浅色。
