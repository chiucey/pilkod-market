#!/usr/bin/env python3
"""
从 JSON 配置文件生成多元微积分 PDF
"""

import json
import sys
import os
from pathlib import Path
from generate import MultivariableCalculusPDFGenerator


def load_config(config_path):
    """加载 JSON 配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_from_config(config_path, output_dir='.', save_latex=True):
    """根据配置文件生成 PDF"""
    config = load_config(config_path)

    # 创建生成器
    generator = MultivariableCalculusPDFGenerator(
        output_dir=output_dir,
        template=config.get('template', 'glassmorphism')
    )

    # 生成文档
    if config.get('type', 'article') == 'article':
        latex_content = generator.generate_article(
            title=config.get('title', '多元微积分'),
            subtitle=config.get('subtitle', ''),
            author=config.get('author', ''),
            institution=config.get('institution', ''),
            date=config.get('date', ''),
            chapters=config.get('chapters')
        )
    else:
        latex_content = generator.generate_beamer(
            title=config.get('title', '多元微积分'),
            subtitle=config.get('subtitle', ''),
            author=config.get('author', ''),
            institution=config.get('institution', ''),
            date=config.get('date', ''),
            chapters=config.get('chapters')
        )

    # 保存 LaTeX 文件
    output_name = config.get('title', 'multivariable_calculus').replace(' ', '_')
    tex_file = f"{output_name}.tex"
    tex_path = generator.save_latex(tex_file)

    print(f"LaTeX 文件已生成: {tex_path}")

    if save_latex:
        print("请使用 xelatex 编译以生成 PDF:")
        print(f"  xelatex {tex_file}")
        print(f"  xelatex {tex_file}  # 运行两次以生成目录")

    return tex_path


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_from_json.py <config.json> [output_dir]")
        print("\n示例:")
        print("  python3 generate_from_json.py examples/chapter2_partial_derivatives.json")
        print("  python3 generate_from_json.py examples/beamer_slides.json ./output")
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在: {config_path}")
        sys.exit(1)

    try:
        generate_from_config(config_path, output_dir)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
