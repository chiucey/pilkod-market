# 多元微积分习题课 PDF 生成器

专为多元微积分教学设计的高质量 PDF 生成工具，支持 LaTeX 排版、一键生成 Article 或 Beamer 演示文稿。

## 功能特点

- **LaTeX 排版**：专业的数学公式渲染，支持 TikZ 图形和 tcolorbox 定理环境
- **双格式输出**：支持 Article 讲义和 Beamer 演示文稿
- **智能封面**：自动构建包含教师、学院、日期的专业封面
- **章节结构**：预置多元函数极限、偏导数、全微分等完整章节
- **经典反例**：内置偏导存在≠连续、可微≠偏导连续等经典反例
- **考研真题**：收录近年考研数学真题及详细解析
- **视觉模板**：玻璃拟态(Glassmorphism)和扁平化(Flat Design)两种风格

## 安装

```bash
# 确保已安装 Python 3.9+
python3 --version

# LaTeX 环境 (可选，用于编译 PDF)
# Ubuntu/Debian:
sudo apt install texlive-xetex texlive-latex-extra

# macOS:
# 安装 MacTeX: https://tug.org/mactex/

# Windows:
# 安装 TeX Live: https://tug.org/texlive/
```

## 快速开始

### 命令行使用

```bash
# 生成默认 Article 讲义
python3 generate.py --save-latex

# 生成 Beamer 演示文稿
python3 generate.py --type beamer --save-latex

# 自定义封面信息
python3 generate.py \
  --title "多元函数极限与连续" \
  --subtitle "第二章  偏导数" \
  --author "张明" \
  --institution "数学科学学院" \
  --save-latex

# 指定视觉模板
python3 generate.py --template flat --save-latex
```

### 从 JSON 配置生成

```bash
# 生成 Article 讲义
python3 generate_from_json.py examples/chapter2_partial_derivatives.json

# 生成 Beamer 演示文稿
python3 generate_from_json.py examples/beamer_slides.json
```

### 编译 PDF

```bash
# 使用 XeLaTeX 编译（需要运行两次以生成目录）
xelatex multivariable_calculus.tex
xelatex multivariable_calculus.tex

# 或使用 LuaLaTeX
lualatex multivariable_calculus.tex
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--type` | 文档类型 | `article` |
| `--title` | 文档标题 | `微积分习题课 · 多元微积分` |
| `--subtitle` | 副标题 | `第二章  偏导数与全微分` |
| `--author` | 作者姓名 | `张明 教授` |
| `--institution` | 学院/学校 | `数学科学学院` |
| `--date` | 日期 | 自动生成 |
| `--template` | 视觉模板 | `glassmorphism` |
| `--output` | 输出目录 | `.` |
| `--save-latex` | 仅保存 LaTeX | False |

## 模板选项

- `glassmorphism`：玻璃拟态风格，半透明背景层
- `flat`：扁平化风格，简洁几何形状
- `academic`：学术风格，暖色调

## 经典反例库

内置以下经典反例，支持可视化展示：

1. **偏导存在 ≠ 连续**：$f(x,y) = \frac{xy}{x^2+y^2}$
2. **可微 ≠ 偏导连续**：$(x^2+y^2)\sin(\frac{1}{\sqrt{x^2+y^2}})$
3. **方向导数存在 ≠ 可微**：$\frac{x^2y}{x^4+y^2}$

## 文件结构

```
multivariable-calculus-exercises/
├── SKILL.md                    # 技能定义文件
├── README.md                   # 本文件
├── generate.py                 # 主生成器脚本
├── generate_from_json.py       # JSON 配置生成器
├── multivariable_calculus.tex  # 生成的示例文件
└── examples/                   # 示例配置
    ├── chapter2_partial_derivatives.json
    └── beamer_slides.json
```

## 示例输出

### Article 封面

```
╔══════════════════════════════════════════════════╗
║                                                    ║
║         ═══════════════════════════════════        ║
║                                                    ║
║              多元函数极限与连续                     ║
║                                                    ║
║              第二章  偏导数与全微分                  ║
║                                                    ║
║         ═══════════════════════════════════        ║
║                                                    ║
║                   张明 教授                         ║
║                                                    ║
║                 数学科学学院                        ║
║                                                    ║
║                2026年03月26日                      ║
║                                                    ║
╚══════════════════════════════════════════════════╝
```

### Beamer 演示文稿

16:9 宽屏格式，适合课堂投影，包含动画效果和分栏布局。

## 技术栈

- Python 3.9+
- LaTeX (XeLaTeX/LuaLaTeX)
- tcolorbox (定理环境)
- TikZ + PGFPlots (图形绘制)
- xeCJK (中文排版)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
