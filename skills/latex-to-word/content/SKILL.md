---
name: latex-to-word
description: LaTeX 到 Word 文档转换。当用户上传 .tex 文件并要求转换为 .docx 格式，或询问如何将 LaTeX 公式导入 Word、解决 Word 中复杂数学公式显示问题时使用。
---

# LaTeX 到 Word 文档转换技能

## 技能目标

帮助用户将 LaTeX 文档 (.tex) 转换为 Microsoft Word 格式 (.docx)，并提供 LaTeX 数学公式在 Word 中正确显示的解决方案。

## 核心功能

### 1. LaTeX 到 Word 文档转换

提供多种转换方法，根据用户场景选择最适合的方案：

#### 方法一：Pandoc 转换（推荐）

Pandoc 是最常用的文档转换工具，支持 LaTeX 到 Word 的高质量转换。

**使用步骤：**
1. 首先安装 Pandoc（如果未安装）
2. 执行转换命令

```bash
pandoc input.tex -o output.docx
```

**高级选项：**
```bash
# 保留目录结构
pandoc input.tex -o output.docx --toc

# 保留交叉引用
pandoc input.tex -o output.docx --resource-path=.

# 使用参考文档控制样式
pandoc input.tex --reference-doc=template.docx -o output.docx
```

#### 方法二：在线转换工具

适合临时转换需求，无需安装软件：
- **Cocconvert**: https://coconvert.com/latex-to-word
- **Online LaTeX Editor**: https://www.overleaf.com
- **Mathpix**: https://mathpix.com（支持公式截图识别）

#### 方法三：LaTeX2e → PDF → Word

适用于 Pandoc 转换效果不理想时：
1. 编译 LaTeX 为 PDF
2. 使用 Adobe Acrobat 或 Word 直接打开 PDF 导入

### 2. LaTeX 公式到 Word 转换

#### 方案一：Word 原生公式编辑器

Word 2016+ 支持 LaTeX 语法输入：
1. 插入 → 公式
2. 选择"线性"或使用 LaTeX 模式
3. 直接输入 LaTeX 代码

#### 方案二：MathType 插件

MathType 是专业的公式编辑器，完整支持 LaTeX：
1. 下载安装 MathType
2. 在 Word 中打开 MathType
3. 粘贴或输入 LaTeX 代码，自动转换为 Word 公式

#### 方案三：Unicode Math

Word 支持的 Unicode Math 符号，部分兼容 LaTeX 语法。

### 3. 常见问题解决

| 问题 | 解决方案 |
|------|----------|
| 公式显示为纯文本 | 使用 MathType 或 Word 原生公式 |
| 中文字体丢失 | 添加 `-C` 参数或使用中文字体包 |
| 表格格式错乱 | 手动调整或使用专业 LaTeX 编辑器 |
| 图片无法显示 | 确保图片路径正确，使用相对路径 |

## 工作流程

```
用户上传 .tex 文件
    ↓
分析文件内容
    ↓
选择转换方案
    ├── 简单文档 → Pandoc 直接转换
    ├── 复杂公式 → MathType 辅助
    └── 保留样式 → 参考文档模板
    ↓
执行转换
    ↓
提供输出和后续建议
```

## 输出格式

技能提供以下输出：
1. **转换后的 .docx 文件**：直接可用的 Word 文档
2. **转换报告**：包含转换过程中的警告和建议
3. **后续优化建议**：如需进一步调整的步骤

## 使用示例

### 示例 1：完整文档转换
```
用户：帮我把这个 .tex 文件转换成 Word 格式
技能：
1. 读取用户上传的 .tex 文件
2. 分析文档结构（章节、公式、表格、图片）
3. 使用 Pandoc 执行转换
4. 如有复杂公式，提供 MathType 处理建议
5. 返回 .docx 文件
```

### 示例 2：LaTeX 公式导入 Word
```
用户：怎么把 LaTeX 公式复制到 Word 里？
技能：
1. 提供三种方法：Word 原生公式、MathType、在线转换
2. 推荐最适合用户场景的方案
3. 提供详细步骤指导
```

## 限制与注意事项

1. **样式限制**：LaTeX 的高级排版功能可能在 Word 中无法完美呈现
2. **宏包依赖**：部分自定义宏可能需要手动转换
3. **中文支持**：确保使用兼容的中文字体和编码设置
4. **公式复杂性**：非常复杂的 LaTeX 公式可能需要手动调整

## 参考资源

- Pandoc 官方文档：https://pandoc.org
- MathType 官网：https://www.writemath.com
- LaTeX 公式参考：https://latex.codecogs.com
