---
name: latex-lab-report
description: 生成符合标准 LaTeX 格式的实验报告。当用户要求写实验报告、生成 .tex 文件、撰写实验报告、或提供实验数据/题目要求时使用。
---

# LaTeX 实验报告生成器

根据用户提供的实验题目、数据或要求，生成符合标准 LaTeX 格式的 .tex 实验报告文件。

## 工作流程

### 1. 需求收集

当用户提供实验报告需求时，收集以下信息（如未提供则询问）：

- **实验标题**：报告标题
- **作者姓名**：如未提供，使用占位符 `[作者姓名]`
- **实验题目/内容**：具体的问题或实验描述
- **数据/结果**：实验数据、计算结果、图像路径（如有）
- **代码实现**：如需要包含代码（如 MATLAB、Python 等）
- **分析要求**：需要分析的结论或对比

### 2. 内容生成

根据实验内容，按以下标准结构组织报告：


**数学公式**使用 `equation` 或 `align` 环境：
```latex
\begin{equation}
    E = \sum_{n=0}^{N} |x(n)|^2
\end{equation}
```

**代码块**使用 `lstlisting` 环境：
```latex
\begin{lstlisting}[language=Matlab]
    % MATLAB 代码
    x = 0:0.1:10;
\end{lstlisting}
```

**图像**使用 `figure` 环境：
```latex
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figure1.jpg}
    \caption{结果图}
\end{figure}
```

**列表**使用 `enumerate` 环境：
```latex
\begin{enumerate}
    \item 第一个要点
    \item 第二个要点
\end{enumerate}
```

### 3. LaTeX 模板结构

生成的 .tex 文件必须包含以下标准 preamble：

```latex
\documentclass[12pt, a4paper]{article}

% --- 导入宏包 ---
\usepackage{ctex}     % 支持中文
\usepackage{amsmath}  % 数学公式
\usepackage{amssymb}  % 数学符号
\usepackage{graphicx} % 插入图片
\usepackage{geometry} % 页面布局
\usepackage{listings} % 代码高亮
\usepackage{xcolor}   % 颜色支持
\usepackage{hyperref} % 超链接
\usepackage{float}    % 图片浮动控制
\usepackage{cite}     % 参考文献引用
\usepackage{setspace}

% --- 页面设置 ---
\geometry{left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm}
\setstretch{1.25}

% --- 代码样式设置 ---
\lstset{
    backgroundcolor=\color{backcolour},
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breaklines=true,
    numbers=left,
    numbersep=5pt,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=2,
    language=Matlab,
    frame=single,
    xleftmargin=2em,
    xrightmargin=2em,
    aboveskip=1em,
    belowskip=1em
}

\title{实验报告标题}
\author{作者姓名}
\date{}
```

### 4. 输出规范

1. **文件命名**：`实验报告_标题.tex` 或用户指定名称
2. **保存路径**：默认保存到用户当前工作目录
3. **图像占位符**：如用户提供图像，使用实际路径；如未提供，使用占位符如 `figure1.jpg`
4. **中文支持**：所有内容使用中文，包括标题、说明、公式注释

### 5. 示例输出

输入示例：
> 写一个实验报告：第一题是验证采样定理，第二题是离散信号能量计算

输出：生成完整的 .tex 文件，包含：
- 标准 preamble
- 标题和作者信息
- 各题目的详细解答结构
- 数学公式环境
- 代码高亮块（如有）
- 图像占位符（如有）

## 注意事项

- 所有数学公式必须使用 LaTeX 语法
- 代码块必须指定语言类型
- 图片使用 `[H]` 强制当前位置
- 列表项可使用 `\textbf{}` 强调关键内容
- 生成的 .tex 文件必须能够直接编译通过，无需额外修改
- 无需参考文献部分，除非用户特别要求

