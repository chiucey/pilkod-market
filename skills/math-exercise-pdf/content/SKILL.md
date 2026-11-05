---
name: math-exercise-pdf
description: 考研数学练习题PDF生成器。当用户需要创建数学练习题、考试试卷、数学作业集等PDF文档时使用此技能。支持LaTeX数学公式排版、封面设计、分类章节结构。
---

# 考研数学做题模板 - PDF生成器

生成专业排版的数学练习题PDF文档，支持完整的LaTeX数学公式渲染。

## 输出格式选择

1. **HTML方式**（推荐）- 使用HTML+KaTeX，通过Edge浏览器生成PDF，无需LaTeX环境
2. **LaTeX方式** - 生成.tex文件后用xelatex编译，公式渲染最精致

## 工作流程

### 步骤1：收集题目信息

向用户确认以下信息：
- 标题（如"数学练习题"、"考研数学强化训练"等）
- 副标题（如知识点范围）
- 年份/系列信息
- 题目内容（按章节/分类组织）

### 步骤2：选择输出格式

```
如果 用户需要高质量PDF且本地有LaTeX环境 → 使用LaTeX模板
如果 用户需要快速预览或无LaTeX环境 → 使用HTML模板
```

### 步骤3：生成文档

**HTML方式（推荐）：**
1. 复制 `assets/math_template.html` 作为基础
2. 替换封面信息（标题、副标题、年份）
3. 按章节添加题目内容
4. 保存为 .html 文件
5. 运行 `python scripts/html_to_pdf.py <文件名>.html` 生成PDF
6. 若脚本提示“未放在数学定界符中的LaTeX命令”，先修复再导出

**LaTeX方式：**
1. 复制 `assets/math_template.tex` 作为基础
2. 替换封面信息（标题、副标题、年份）
3. 按章节添加题目内容
4. 保存为 .tex 文件
5. 使用 `xelatex` 编译生成PDF

## 文件结构

```
math-exercise-pdf/
├── SKILL.md                    # 技能说明文档
├── assets/
│   ├── math_template.html      # HTML模板（推荐）
│   └── math_template.tex       # LaTeX模板
└── scripts/
    ├── html_to_pdf.py          # HTML转PDF脚本
    └── README.md               # 脚本使用说明
```

## 题目格式规范

### 数学公式语法

行内公式：`$公式$`
块级公式：`$$公式$$` 或 `\[公式\]`

### 公式渲染防错规则（关键）

1. 所有 LaTeX 命令（如 `\frac`、`\sum`、`\lim`、`\epsilon`、`\underline`）必须写在数学定界符中（`$...$` 或 `$$...$$`）。
2. 填空线请写为 `$\\underline{\\qquad\\qquad}$`，不要在普通文本里裸写 `\underline{...}`。
3. 不要覆盖 KaTeX 内部分式布局相关样式（如 `.katex .mfrac` 的 `display:flex`），否则会导致分子分母错位或缺失。
4. 数学定界符内部若出现不等号，优先使用 `\lt` / `\gt`（或 `&lt;` / `&gt;`），避免裸 `<` / `>` 被 HTML 误解析导致公式截断。
5. PDF 导出统一使用 `scripts/html_to_pdf.py`；脚本会先做语法检查，并自动修复数学区裸 `<` / `>` 后再导出。
6. 如需跳过语法检查，可使用 `--force`，但只建议在确认无误时使用。

### 章节结构模板

```
## 第X部分 章节名称

### 题 N
题目内容，支持数学公式 $x^2 + y^2 = r^2$

### 题 N+1
下一题内容...
```

### 常用LaTeX数学命令

| 符号 | 代码 | 符号 | 代码 |
|------|------|------|------|
| 分数 | `\dfrac{a}{b}` | 根号 | `\sqrt{x}` |
| 求和 | `\sum_{i=1}^{n}` | 积分 | `\int_a^b` |
| 极限 | `\lim_{x \to 0}` | 偏导 | `\frac{\partial f}{\partial x}` |
| 向量 | `\vec{a}` | 矩阵 | `\begin{pmatrix}...\end{pmatrix}` |

## 示例输出

### HTML模板渲染效果

```
第一部分 高等数学

题 1
设函数 $f(x)$ 在 $[0,1]$ 上连续，证明：
$$\int_0^1 f(x)dx = f(\xi), \quad \xi \in [0,1]$$

题 2
求极限：$\displaystyle\lim_{x\to 0}\frac{\sin x}{x}$
```

## 依赖要求

- HTML转PDF: Microsoft Edge浏览器（Windows自带）
- LaTeX转PDF: TeX Live 或 MiKTeX 发行版
