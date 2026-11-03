# 模板资源

## math_template.html

HTML模板，使用KaTeX进行数学公式渲染。

### 特点
- 无需LaTeX环境，Windows自带Edge即可生成PDF
- 支持KaTeX实时渲染数学公式
- 专业的封面设计和打印样式

### 使用方法
1. 复制此文件作为基础
2. 修改 `<title>` 和封面内容
3. 添加题目章节（LaTeX命令必须放在 `$...$` 或 `$$...$$` 中）
4. 使用 `python scripts/html_to_pdf.py` 生成PDF

### 公式书写规范（HTML模板）
- 行内公式：`$...$`
- 块级公式：`$$...$$`
- 填空线写法：`$\\underline{\\qquad\\qquad}$`
- 不要在普通文本里直接写 `\frac`、`\underline` 等命令

## math_template.tex

LaTeX模板，需要安装TeX Live或MiKTeX。

### 特点
- 最高质量的数学公式排版
- 支持复杂的数学结构
- 适合正式出版

### 使用方法
1. 复制此文件作为基础
2. 修改文档标题信息
3. 添加题目内容
4. 使用 `xelatex` 编译生成PDF
