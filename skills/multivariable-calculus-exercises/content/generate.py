#!/usr/bin/env python3
"""
多元微积分习题课 PDF 生成器
Multivariable Calculus Exercises PDF Generator

支持 LaTeX 排版，一键生成 Article 或 Beamer 演示文稿。
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class MultivariableCalculusPDFGenerator:
    """多元微积分习题课 PDF 生成器"""

    # 配色方案
    TEMPLATES = {
        "glassmorphism": {
            "name": "玻璃拟态",
            "primary": "#1E3A5F",
            "accent": "#3498DB",
            "secondary": "#2ECC71",
            "background": "#F8FAFC",
            "text": "#2C3E50",
            "light_bg": "rgba(255,255,255,0.7)",
            "frosted": "rgba(255,255,255,0.25)",
        },
        "flat": {
            "name": "扁平化",
            "primary": "#2C3E50",
            "accent": "#E74C3C",
            "secondary": "#9B59B6",
            "background": "#FFFFFF",
            "text": "#34495E",
            "light_bg": "#ECF0F1",
            "frosted": "#BDC3C7",
        },
        "academic": {
            "name": "学术风格",
            "primary": "#1A365D",
            "accent": "#2B6CB0",
            "secondary": "#38A169",
            "background": "#FFFBF0",
            "text": "#1A202C",
            "light_bg": "#F7FAFC",
            "frosted": "#E2E8F0",
        },
    }

    # 经典反例库
    COUNTEREXAMPLES = {
        "partial_not_continuous": {
            "title": "偏导存在 ≠ 连续",
            "description": "偏导数存在但函数在该点不连续",
            "function": r"f(x,y) = \begin{cases} \frac{xy}{x^2+y^2}, & (x,y) \neq (0,0) \\ 0, & (x,y) = (0,0) \end{cases}",
            "analysis": "在 (0,0) 点处，$f_x(0,0)=0$, $f_y(0,0)=0$，但沿路径 $y=x$ 趋近时，极限值为 $\\frac{1}{2} \\neq f(0,0)$，故不连续。",
            "key_point": "偏导数存在仅是局部可导的必要条件，不能保证连续性。",
        },
        "differentiable_partial_not_continuous": {
            "title": "可微 ≠ 偏导连续",
            "description": "函数可微但偏导数在该点不连续",
            "function": r"f(x,y) = \begin{cases} (x^2+y^2)\sin\left(\frac{1}{\sqrt{x^2+y^2}}\right), & (x,y) \neq (0,0) \\ 0, & (x,y) = (0,0) \end{cases}",
            "analysis": "该函数在 (0,0) 处可微，但偏导数 $f_x$ 和 $f_y$ 在 (0,0) 处不连续。",
            "key_point": "可微仅要求偏导数存在且线性逼近有效，不要求偏导数连续。",
        },
        "directional_not_differentiable": {
            "title": "方向导数存在 ≠ 可微",
            "description": "沿所有方向的方向导数存在但函数不可微",
            "function": r"f(x,y) = \begin{cases} \frac{x^2y}{x^4+y^2}, & (x,y) \neq (0,0) \\ 0, & (x,y) = (0,0) \end{cases}",
            "analysis": "在 (0,0) 点处，所有方向的方向导数都存在，但函数在 (0,0) 处不可微。",
            "key_point": r"需要用可微的严格定义 $f(x,y) - f(0,0) = A\Delta x + B\Delta y + o(\rho)$ 来验证。",
        },
        "partial_continuous_not_differentiable": {
            "title": "偏导连续 ≠ 可微",
            "description": "两个偏导数都连续但函数在该点不可微（仅对单变量成立）",
            "function": r"f(x,y) = |x| + |y|",
            "analysis": "偏导数在原点邻域内不处处存在（虽然有偏导数存在的方向），但在原点不可微。",
            "key_point": "在一元函数中，可导等价于可微；在多元函数中，偏导数连续是充分条件而非必要条件。",
        },
    }

    def __init__(self, output_dir=".", template="glassmorphism"):
        self.output_dir = Path(output_dir)
        self.template = template
        self.template_config = self.TEMPLATES.get(template, self.TEMPLATES["glassmorphism"])
        self.content = {}
        self.latex_content = ""

    def generate_article(self, title, subtitle="", author="", institution="", date="", chapters=None):
        """生成 Article 格式 PDF"""
        if date == "":
            date = datetime.now().strftime("%Y年%m月%d日")

        self.latex_content = self._generate_article_latex(title, subtitle, author, institution, date, chapters)
        return self.latex_content

    def generate_beamer(self, title, subtitle="", author="", institution="", date="", chapters=None):
        """生成 Beamer 演示文稿 PDF"""
        if date == "":
            date = datetime.now().strftime("%Y年%m月")

        self.latex_content = self._generate_beamer_latex(title, subtitle, author, institution, date, chapters)
        return self.latex_content

    def _generate_article_latex(self, title, subtitle, author, institution, date, chapters):
        """生成 Article 格式 LaTeX 代码"""
        colors = self.template_config
        chapters = chapters or self._get_default_chapters()

        latex = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[xetex]{{fontspec}}
\\usepackage{{xeCJK}}
\\setCJKmainfont{{[SimSun.ttf]}}{{SimSun}}
\\setCJKsansfont{{[SimHei.ttf]}}{{SimHei}}

% 数学包
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsthm}}
\\usepackage{{mathtools}}

% 图形包
\\usepackage{{tikz}}
\\usetikzlibrary{{positioning,arrows.meta,calc,decorations.pathreplacing}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepackage{{tcolorbox}}
\\tcbuselibrary{{theorems,skins}}

% 页面设置
\\usepackage[top=2.5cm,bottom=2.5cm,left=3cm,right=2.5cm]{{geometry}}
\\usepackage{{fancyhdr}}

% 颜色定义
\\definecolor{{primary}}{{HTML}}{{{colors['primary'].replace('#', '')}}}
\\definecolor{{accent}}{{HTML}}{{{colors['accent'].replace('#', '')}}}
\\definecolor{{secondary}}{{HTML}}{{{colors['secondary'].replace('#', '')}}}
\\definecolor{{bg}}{{HTML}}{{{colors['background'].replace('#', '')}}}

% 定理环境
\\tcbset{{
    theorem style/definition={{
        before={{\\par\\nopagebreak\\small\\，天津大学数学科学学院}},
        fonttitle={{\\bfseries\\sffamily}},
        fontupper={{\\rmfamily}},
        boxrule=0.5pt,
        colback={colors['light_bg']},
        colframe=accent,
    }},
    definition style={{
        boxrule=0.5pt,
        colback={colors['light_bg']},
        colframe=primary,
    }},
}}

\\newtheorem*{{definition}}{{\\heiti 定义}}
\\newtheorem*{{theorem}}{{\\heiti 定理}}
\\newtheorem*{{lemma}}{{\\heiti 引理}}
\\newtheorem*{{corollary}}{{\\heiti 推论}}
\\newtheorem*{{example}}{{\\heiti 例题}}
\\newtheorem*{{exercise}}{{\\heiti 练习}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[C]{{\\color{{primary}}\\small{{{title}}}}}
\\fancyfoot[C]{{\\thepage}}
\\fancyfoot[R]{{\\color{{accent}}\\small{{{author}}}}}
\\renewcommand{{\\headrulewidth}}{{1pt}}
\\renewcommand{{\\footrulewidth}}{{0.5pt}}

\\begin{{document}}

% 封面
\\thispagestyle{{empty}}
\\begin{{center}}
\\vspace*{{2cm}}
\\parbox{{0.9\\textwidth}}{{
\\centering
\\rule{{\\textwidth}}{{3pt}}\\\\[0.5cm]
{{\\Huge\\bfseries\\sffamily\\color{{primary}}{title}}}\\\\[0.8cm]
\\ifdefined\\{{{subtitle}}}\\\\
{{\\Large\\color{{accent}}\\subtitle}}\\\\
\\fi
\\rule{{\\textwidth}}{{1pt}}\\\\[2cm]
{{\\large\\bfseries{author}}}\\\\[0.3cm]
{{\\large{institution}}}\\\\[1cm]
{{\\large\\color{{secondary}}{date}}}
}}
\\end{{center}}
\\newpage

% 目录
\\tableofcontents
\\newpage

% 正文
"""

        for chapter in chapters:
            latex += self._chapter_to_latex(chapter)

        latex += """\\end{document}"""
        return latex

    def _generate_beamer_latex(self, title, subtitle, author, institution, date, chapters):
        """生成 Beamer 演示文稿 LaTeX 代码"""
        colors = self.template_config
        chapters = chapters or self._get_default_chapters()

        latex = f"""\\documentclass[aspectratio=169]{{beamer}}
\\usepackage{{xeCJK}}
\\setCJKmainfont{{[SimSun.ttf]}}{{SimSun}}
\\setCJKsansfont{{[SimHei.ttf]}}{{SimHei}}

% 主题设置
\\usetheme{{Madrid}}
\\usecolortheme{{whlwhole}}
\\usepackage{{tikz}}
\\usetikzlibrary{{positioning,arrows.meta,calc}}

% 颜色定义
\\definecolor{{primary}}{{HTML}}{{{colors['primary'].replace('#', '')}}}
\\definecolor{{accent}}{{HTML}}{{{colors['accent'].replace('#', '')}}}
\\definecolor{{secondary}}{{HTML}}{{{colors['secondary'].replace('#', '')}}}

\\setbeamercolor*{{palette primary}}{{use={{heading}},bg={{primary}}}}
\\setbeamercolor*{{palette secondary}}{{use={{heading}},bg={{accent}}}}
\\setbeamercolor*{{normal text}}{{bg={{colors['background']}},fg={{colors['text']}}}}

\\setbeamertemplate{{caption}}{{\\raggedright\\insertcaption\\par}}
\\setbeamertemplate{{bibliography item}}{{[\\theenumiv]}}

\\usepackage{{amsmath}}
\\usepackage{{amsthm}}
\\usepackage{{mathtools}}
\\usepackage{{tfrupee}}

\\title{{{title}}}
\\subtitle{{{subtitle}}}
\\author{{{author}}}
\\institute{{{institution}}}
\\date{{{date}}}

\\begin{{document}}

% 封面
\\begin{{frame}}
\\titlepage
\\end{{frame}}

% 目录
\\begin{{frame}}{{目录}}
\\tableofcontents
\\end{{frame}}

"""

        for chapter in chapters:
            latex += self._chapter_to_beamer(chapter)

        latex += """\\end{document}"""
        return latex

    def _chapter_to_latex(self, chapter):
        """将章节转换为 Article 格式 LaTeX"""
        latex = f"\n\\section{{{chapter.get('title', 'Section')}}}\n"

        for section in chapter.get('sections', []):
            latex += f"\\subsection{{{section.get('title', 'Subsection')}}}\n"

            for block in section.get('content', []):
                latex += self._block_to_latex(block)

        # 处理经典反例
        if chapter.get('type') == 'counterexample':
            latex += self._counterexamples_section(chapter.get('cases', []))

        return latex

    def _chapter_to_beamer(self, chapter):
        """将章节转换为 Beamer 格式 LaTeX"""
        latex = f"""
\\begin{{section}}{{{chapter.get('title', 'Section')}}}
\\end{{section}}
"""

        for section in chapter.get('sections', []):
            latex += f"""
\\begin{{frame}}{{{section.get('title', '')}}}
"""
            for block in section.get('content', []):
                latex += self._block_to_beamer(block)
            latex += "\\end{frame}\n"

        return latex

    def _block_to_latex(self, block):
        """将内容块转换为 Article LaTeX"""
        block_type = block.get('type', 'body')

        if block_type == 'definition':
            return f"""\\begin{{definition}}{block.get('content', '')}\\end{{definition}}\\nopagebreak\\\\
"""
        elif block_type == 'theorem':
            return f"""\\begin{{theorem}}{block.get('content', '')}\\end{{theorem}}\\nopagebreak\\\\
"""
        elif block_type == 'example':
            return f"""\\begin{{example}}{block.get('content', '')}\\end{{example}}\\nopagebreak\\\\
"""
        elif block_type == 'math':
            return f"""\\[ {block.get('content', '')} \\]\n"""
        elif block_type == 'tikz':
            return f"""
\\begin{{tikzpicture}}[scale={block.get('scale', 1)}]
{block.get('content', '')}
\\end{{tikzpicture}}
"""
        elif block_type == 'callout':
            return f"""\\begin{{tcolorbox}}[title={{\\textbf{{{block.get('title', '提示')}}}}},
    colback={self.template_config['light_bg']},
    coltitle={self.template_config['primary']},
    colframe={self.template_config['accent']}]
{block.get('content', '')}
\\end{{tcolorbox}}\\\\
"""
        else:
            return f"{block.get('content', '')}\\\\"

    def _block_to_beamer(self, block):
        """将内容块转换为 Beamer LaTeX"""
        block_type = block.get('type', 'body')

        if block_type == 'math':
            return f"\\[ {block.get('content', '')} \\]\n"
        elif block_type == 'bullet':
            items = '\n\\'.join([f"\\item {item}" for item in block.get('items', [])])
            return f"\\begin{{itemize}}\n{items}\n\\end{{itemize}}\n"
        elif block_type == 'columns':
            return f"""
\\begin{{columns}}
{block.get('content', '')}
\\end{{columns}}
"""
        else:
            return f"{block.get('content', '')}\n"

    def _counterexamples_section(self, cases):
        """生成经典反例章节"""
        latex = "\n\\section*{经典反例}\n\\addcontentsline{{toc}}{{section}}{{经典反例}}\n"

        for case_key in cases:
            if case_key in self.COUNTEREXAMPLES:
                ce = self.COUNTEREXAMPLES[case_key]
                latex += f"""
\\begin{{tcolorbox}}[title={{\\textbf{{【反例】{ce['title']}}}}},
    colback=white,
    coltitle={self.template_config['accent']},
    colframe={self.template_config['accent']},
    fonttitle={{\\bfseries}},
    sharp corners=rounded,
    rounded corners={{at={{(0,0)}}}},
    width={{\\textwidth}}]

\\textbf{{函数定义：}}\\\\
${ce['function']}$

\\vspace{{0.3cm}}
\\textbf{{分析：}}\\\\
{ce['analysis']}

\\vspace{{0.3cm}}
\\colorbox{{{self.template_config['light_bg']}}}{{\\parbox{{0.95\\textwidth}}{{
\\textbf{{关键结论：}}{ce['key_point']}
}}}}
\\end{{tcolorbox}}\\\\
\\vspace{{0.5cm}}
"""
            else:
                # 自定义反例
                latex += f"""
\\begin{{tcolorbox}}[title={{\\textbf{{【反例】{case_key.get('title', '')}}}}},
    colback=white,
    coltitle={self.template_config['accent']},
    colframe={self.template_config['accent']},
    fonttitle={{\\bfseries}},
    sharp corners=rounded,
    rounded corners={{at={{(0,0)}}}},
    width={{\\textwidth}}]

{case_key.get('content', '')}
\\end{{tcolorbox}}\\\\
\\vspace{{0.5cm}}
"""

        return latex

    def _get_default_chapters(self):
        """获取默认章节内容"""
        return [
            {
                "title": "第一章  多元函数基础",
                "sections": [
                    {
                        "title": "1.1 概念判定方法",
                        "content": [
                            {"type": "definition", "content": "设函数 $f(x,y)$ 在点 $P_0(x_0,y_0)$ 的某去心邻域内有定义，如果对于任意 $\\varepsilon>0$，存在 $\\delta>0$，使得当 $0<\\sqrt{(x-x_0)^2+(y-y_0)^2}<\\delta$ 时，有 $|f(x,y)-A|<\\varepsilon$，则称 $A$ 为函数 $f(x,y)$ 当 $(x,y)\\to(x_0,y_0)$ 时的极限，记作 $\\lim_{(x,y)\\to(x_0,y_0)}f(x,y)=A$。"},
                            {"type": "theorem", "content": "（夹逼定理）设函数 $f(x,y)$、$g(x,y)$、$h(x,y)$ 在点 $P_0$ 的去心邻域内有定义，且满足 $g(x,y)\\leq f(x,y)\\leq h(x,y)$，若 $\\lim_{(x,y)\\to P_0}g(x,y)=\\lim_{(x,y)\\to P_0}h(x,y)=A$，则 $\\lim_{(x,y)\\to P_0}f(x,y)=A$。"},
                            {"type": "example", "content": "求 $\\lim_{(x,y)\\to(0,0)}\\frac{x^2y}{x^2+y^2}$。解：利用极坐标变换 $x=r\\cos\\theta$，$y=r\\sin\\theta$，得 $\\left|\\frac{x^2y}{x^2+y^2}\\right|=\\frac{r^3|\\cos^2\\theta\\sin\\theta|}{r^2}=r|\\cos^2\\theta\\sin\\theta|\\leq r\\to0$，故极限为 $0$。"},
                        ]
                    },
                    {
                        "title": "1.2 关系图谱",
                        "content": [
                            {"type": "callout", "title": "概念关系图", "content": "多元函数分析中的核心概念蕴含关系：\\begin{center}\\begin{tikzpicture}[node distance=2cm]\n\\node (limit) {极限存在};\n\\node (cont) [right=of limit] {连续};\n\\node (partial) [right=of cont] {偏导存在};\n\\node (diff) [right=of partial] {可微};\n\\node (partialcont) [below=of diff] {偏导连续};\n\\draw[->,>=Stealth] (limit) -- (cont);\n\\draw[->,>=Stealth] (cont) -- (partial);\n\\draw[->,>=Stealth] (partial) -- (diff);\n\\draw[->,>=Stealth] (diff) -- (partialcont);\n\\end{tikzpicture}\\end{center}"},
                        ]
                    },
                ]
            },
            {
                "title": "第二章  偏导数与全微分",
                "sections": [
                    {
                        "title": "2.1 偏导数定义",
                        "content": [
                            {"type": "definition", "content": "设函数 $z=f(x,y)$ 在点 $(x_0,y_0)$ 的某邻域内有定义，若极限 $\\lim_{\\Delta x\\to0}\\frac{f(x_0+\\Delta x,y_0)-f(x_0,y_0)}{\\Delta x}$ 存在，则称此极限为函数 $f$ 在点 $(x_0,y_0)$ 处对 $x$ 的偏导数，记作 $f_x(x_0,y_0)$ 或 $\\frac{\\partial f}{\\partial x}\\bigg|_{(x_0,y_0)}$。"},
                        ]
                    },
                    {
                        "title": "2.2 全微分",
                        "content": [
                            {"type": "definition", "content": "设函数 $z=f(x,y)$ 在点 $(x_0,y_0)$ 的某邻域内有定义，如果函数在该点的全增量 $\\Delta z=f(x_0+\\Delta x,y_0+\\Delta y)-f(x_0,y_0)$ 可以表示为 $\\Delta z=A\\Delta x+B\\Delta y+o(\\rho)$，其中 $\\rho=\\sqrt{(\\Delta x)^2+(\\Delta y)^2}$，$A,B$ 为常数，则称函数在点 $(x_0,y_0)$ 处可微，并称 $A\\Delta x+B\\Delta y$ 为函数在点 $(x_0,y_0)$ 处的全微分，记作 $dz=A\\Delta x+B\\Delta y$。"},
                        ]
                    },
                ]
            },
            {
                "title": "第三章  经典反例分析",
                "type": "counterexample",
                "cases": ["partial_not_continuous", "differentiable_partial_not_continuous"]
            },
            {
                "title": "第四章  考研真题解析",
                "sections": [
                    {
                        "title": "4.1 极限计算题型",
                        "content": [
                            {"type": "example", "content": "【2024年真题】求 $\\lim_{(x,y)\\to(0,0)}\\frac{1-\\cos(x^2+y^2)}{x^2+y^2}$。解：利用等价无穷小 $1-\\cos t\\sim\\frac{t^2}{2}$，得原式 $=\\lim_{(x,y)\\to(0,0)}\\frac{\\frac{1}{2}(x^2+y^2)^2}{x^2+y^2}=\\lim_{(x,y)\\to(0,0)}\\frac{1}{2}(x^2+y^2)=0$。"},
                        ]
                    },
                    {
                        "title": "4.2 偏导数计算题型",
                        "content": [
                            {"type": "example", "content": "【2023年真题】设 $z=f(x,y)$ 由方程 $e^z+xyz=0$ 确定，求 $\\frac{\\partial z}{\\partial x}$。解：对方程两边关于 $x$ 求偏导：$e^z\\frac{\\partial z}{\\partial x}+yz+xy\\frac{\\partial z}{\\partial x}=0$，整理得 $\\frac{\\partial z}{\\partial x}=-\\frac{yz}{e^z+xy}$。"},
                        ]
                    },
                ]
            },
        ]

    def save_latex(self, filename="multivariable_calculus.tex"):
        """保存 LaTeX 文件"""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.latex_content)
        return output_path

    def compile_pdf(self, filename="multivariable_calculus.tex", output_name=None):
        """编译 PDF（需要 XeLaTeX）"""
        if output_name is None:
            output_name = filename.replace('.tex', '.pdf')

        import subprocess

        # 尝试使用 xelatex 编译
        try:
            result = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', '-halt-on-error', filename],
                cwd=self.output_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return self.output_dir / output_name
            else:
                print(f"LaTeX 编译失败: {result.stderr}", file=sys.stderr)
                return None
        except FileNotFoundError:
            print("警告: 未找到 xelatex 编译器，保存 LaTeX 文件以供手动编译。", file=sys.stderr)
            return self.save_latex(filename)
        except Exception as e:
            print(f"编译出错: {e}", file=sys.stderr)
            return self.save_latex(filename)


def main():
    parser = argparse.ArgumentParser(description='多元微积分习题课 PDF 生成器')
    parser.add_argument('--type', choices=['article', 'beamer'], default='article',
                        help='输出格式: article 或 beamer')
    parser.add_argument('--title', default='微积分习题课 · 多元微积分',
                        help='文档标题')
    parser.add_argument('--subtitle', default='第二章  偏导数与全微分',
                        help='副标题')
    parser.add_argument('--author', default='张明 教授',
                        help='作者姓名')
    parser.add_argument('--institution', default='数学科学学院',
                        help='学院/学校')
    parser.add_argument('--date', default='',
                        help='日期（留空则自动生成）')
    parser.add_argument('--template', choices=['glassmorphism', 'flat', 'academic'],
                        default='glassmorphism',
                        help='视觉模板')
    parser.add_argument('--output', default='.',
                        help='输出目录')
    parser.add_argument('--save-latex', action='store_true',
                        help='仅保存 LaTeX 文件')

    args = parser.parse_args()

    # 创建生成器
    generator = MultivariableCalculusPDFGenerator(
        output_dir=args.output,
        template=args.template
    )

    # 生成文档
    if args.type == 'article':
        generator.generate_article(
            title=args.title,
            subtitle=args.subtitle,
            author=args.author,
            institution=args.institution,
            date=args.date
        )
    else:
        generator.generate_beamer(
            title=args.title,
            subtitle=args.subtitle,
            author=args.author,
            institution=args.institution,
            date=args.date
        )

    # 保存/编译
    if args.save_latex:
        path = generator.save_latex()
        print(f"LaTeX 文件已保存: {path}")
    else:
        tex_file = "multivariable_calculus.tex"
        path = generator.compile_pdf(tex_file)
        if path:
            print(f"PDF 已生成: {path}")
        else:
            print("LaTeX 文件已保存，可手动编译。")


if __name__ == '__main__':
    main()
