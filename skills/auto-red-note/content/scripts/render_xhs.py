#!/usr/bin/env python3
"""
Auto-RedNote 小红书图文笔记渲染脚本

将 Markdown 文件渲染为小红书风格的 HD 图片（1080x1440）
支持多种主题风格和分页模式
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import markdown
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请安装依赖：pip install markdown playwright && playwright install chromium")
    sys.exit(1)


# 主题样式配置
THEME_STYLES = {
    "default": {
        "name": "默认简约",
        "background": "linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%)",
        "card_bg": "#ffffff",
        "border": "#d1d5db",
        "heading": "#1f2937",
        "text": "#374151",
        "accent": "#6b7280",
    },
    "playful-geometric": {
        "name": "趣味几何",
        "background": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "card_bg": "#ffffff",
        "border": "#ff9a9e",
        "heading": "#e63946",
        "text": "#2d3436",
        "accent": "#ff6b6b",
        "shapes": True,
    },
    "neo-brutalism": {
        "name": "新丑风格",
        "background": "#ffeb3b",
        "card_bg": "#ffffff",
        "border": "#000000",
        "heading": "#000000",
        "text": "#000000",
        "accent": "#ff00ff",
        "shadow": "4px 4px 0px #000000",
    },
    "botanical": {
        "name": "植物园风",
        "background": "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)",
        "card_bg": "#f1f8e9",
        "border": "#81c784",
        "heading": "#2e7d32",
        "text": "#388e3c",
        "accent": "#4caf50",
    },
    "professional": {
        "name": "专业商务",
        "background": "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)",
        "card_bg": "#ffffff",
        "border": "#e3f2fd",
        "heading": "#1565c0",
        "text": "#0d47a1",
        "accent": "#1976d2",
    },
    "retro": {
        "name": "复古怀旧",
        "background": "linear-gradient(135deg, #f5f5dc 0%, #deb887 100%)",
        "card_bg": "#fffaf0",
        "border": "#d2691e",
        "heading": "#8b4513",
        "text": "#654321",
        "accent": "#cd853f",
    },
    "terminal": {
        "name": "终端命令行",
        "background": "#1e1e1e",
        "card_bg": "#252526",
        "border": "#3c3c3c",
        "heading": "#4ec9b0",
        "text": "#d4d4d4",
        "accent": "#569cd6",
        "font": "Consolas, 'Courier New', monospace",
    },
    "sketch": {
        "name": "手绘素描",
        "background": "#fefefe",
        "card_bg": "#fafafa",
        "border": "#424242",
        "heading": "#212121",
        "text": "#616161",
        "accent": "#9e9e9e",
        "sketch_style": True,
    },
}


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """解析 Markdown 文件的 YAML frontmatter"""
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_section = parts[1]
            body = parts[2].strip()

            for line in yaml_section.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, body


def parse_markdown(content: str) -> List[Dict]:
    """解析 Markdown 内容为结构化数据"""
    sections = []
    current_section = {"type": "cover", "content": ""}

    lines = content.split("\n")
    in_code_block = False

    for line in lines:
        # 处理代码块
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            current_section["content"] += line + "\n"
            continue

        if in_code_block:
            current_section["content"] += line + "\n"
            continue

        # 处理分隔符
        if line.strip() == "---":
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {"type": "card", "content": ""}
            continue

        # 处理标题
        if line.startswith("# "):
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {"type": "card", "heading": line[2:].strip(), "content": ""}
            continue

        current_section["content"] += line + "\n"

    if current_section["content"].strip():
        sections.append(current_section)

    return sections


def get_cover_html(frontmatter: Dict, theme: str) -> str:
    """生成封面 HTML"""
    style = THEME_STYLES.get(theme, THEME_STYLES["default"])

    emoji = frontmatter.get("emoji", "")
    title = frontmatter.get("title", "")
    subtitle = frontmatter.get("subtitle", "")

    bg_style = f"background: {style['background']}"
    heading_color = style["heading"]
    text_color = style["text"]

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1440">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: 1080px;
            height: 1440px;
            {bg_style};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}
        .container {{
            width: 920px;
            height: 1200px;
            background: {style['card_bg']};
            border-radius: 40px;
            border: 4px solid {style['border']};
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }}
        .emoji {{
            font-size: 180px;
            margin-bottom: 40px;
            animation: bounce 2s ease-in-out infinite;
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-20px); }}
        }}
        .title {{
            font-size: 96px;
            font-weight: 800;
            color: {heading_color};
            text-align: center;
            line-height: 1.2;
            margin-bottom: 30px;
        }}
        .subtitle {{
            font-size: 48px;
            color: {text_color};
            text-align: center;
            font-weight: 400;
        }}
        .decoration {{
            position: absolute;
            font-size: 60px;
            opacity: 0.3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">{emoji}</div>
        <div class="title">{title}</div>
        <div class="subtitle">{subtitle}</div>
    </div>
</body>
</html>"""


def get_card_html(section: Dict, theme: str, index: int) -> str:
    """生成内容卡片 HTML"""
    style = THEME_STYLES.get(theme, THEME_STYLES["default"])

    # 处理 Markdown 内容
    content = section.get("content", "")
    heading = section.get("heading", "")

    # 简单的 Markdown 转 HTML
    html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])

    bg_style = f"background: {style['background']}"
    heading_color = style["heading"]
    text_color = style["text"]
    accent_color = style["accent"]

    # 检查是否有特殊样式
    extra_styles = ""
    if style.get("shadow"):
        extra_styles = f"box-shadow: {style['shadow']};"
    if style.get("shapes"):
        extra_styles += "position: relative;"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1440">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: 1080px;
            min-height: 1440px;
            {bg_style};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            padding: 40px;
            overflow: hidden;
        }}
        .container {{
            width: 1000px;
            min-height: 1360px;
            background: {style['card_bg']};
            border-radius: 32px;
            border: 4px solid {style['border']};
            padding: 50px;
            {extra_styles}
        }}
        .heading {{
            font-size: 72px;
            font-weight: 700;
            color: {heading_color};
            margin-bottom: 40px;
            line-height: 1.3;
        }}
        .content {{
            font-size: 42px;
            color: {text_color};
            line-height: 1.8;
        }}
        .content h1, .content h2, .content h3 {{
            color: {heading_color};
            margin: 30px 0 20px 0;
        }}
        .content h1 {{ font-size: 60px; }}
        .content h2 {{ font-size: 52px; }}
        .content h3 {{ font-size: 48px; }}
        .content p {{ margin: 20px 0; }}
        .content ul, .content ol {{
            margin: 20px 0;
            padding-left: 40px;
        }}
        .content li {{
            margin: 15px 0;
        }}
        .content blockquote {{
            border-left: 6px solid {accent_color};
            padding-left: 30px;
            margin: 30px 0;
            font-style: italic;
            color: {accent_color};
        }}
        .content code {{
            background: {style['background']};
            padding: 4px 12px;
            border-radius: 8px;
            font-family: 'SF Mono', Consolas, monospace;
        }}
        .content pre {{
            background: {style['background']};
            padding: 30px;
            border-radius: 16px;
            overflow-x: auto;
        }}
        .content pre code {{
            background: none;
            padding: 0;
        }}
        .card-number {{
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 36px;
            color: {accent_color};
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        {f'<div class="heading">{heading}</div>' if heading else ''}
        <div class="content">{html_content}</div>
    </div>
</body>
</html>"""


def render_html_to_image(html: str, output_path: str, width: int = 1080, height: int = 1440):
    """使用 Playwright 将 HTML 渲染为图片"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html)
        page.wait_for_timeout(1000)  # 等待渲染完成
        page.screenshot(path=output_path, type="png")
        browser.close()


def auto_split_sections(sections: List[Dict], max_height: int = 1440) -> List[Dict]:
    """自动分割内容以适应高度"""
    split_sections = []
    current_height = 0

    for section in sections:
        estimated_height = len(section.get("content", "")) // 5 + 800

        if current_height + estimated_height > max_height:
            split_sections.append({"type": "new-page", "content": ""})
            current_height = 0

        split_sections.append(section)
        current_height += estimated_height

    return split_sections


def render_markdown(
    input_file: str,
    output_dir: str = ".",
    theme: str = "default",
    mode: str = "separator",
    width: int = 1080,
    height: int = 1440,
    max_height: int = 4320,
    dpr: int = 2,
):
    """渲染 Markdown 文件为图片"""
    # 读取文件
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析 frontmatter
    frontmatter, body = parse_frontmatter(content)

    # 解析内容
    sections = parse_markdown(body)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 渲染封面
    if sections and sections[0].get("type") == "cover":
        cover_html = get_cover_html(frontmatter, theme)
        cover_path = os.path.join(output_dir, "cover.png")
        render_html_to_image(cover_html, cover_path, width, height)
        print(f"封面已生成: {cover_path}")
        sections = sections[1:]
    else:
        # 使用 frontmatter 生成封面
        cover_html = get_cover_html(frontmatter, theme)
        cover_path = os.path.join(output_dir, "cover.png")
        render_html_to_image(cover_html, cover_path, width, height)
        print(f"封面已生成: {cover_path}")

    # 根据模式处理分页
    if mode == "auto-split":
        sections = auto_split_sections(sections, max_height)

    # 渲染内容卡片
    card_count = 0
    current_height = 0

    for section in sections:
        if section.get("type") == "new-page":
            current_height = 0
            continue

        card_html = get_card_html(section, theme, card_count)
        card_path = os.path.join(output_dir, f"card_{card_count + 1}.png")

        # 动态高度模式
        if mode == "dynamic":
            section_height = min(len(section.get("content", "")) // 3 + 1440, max_height)
        else:
            section_height = height

        render_html_to_image(card_html, card_path, width, section_height)
        print(f"内容卡片 {card_count + 1} 已生成: {card_path}")
        card_count += 1

    print(f"\n渲染完成！共生成 {card_count + 1} 张图片")
    return True


def main():
    parser = argparse.ArgumentParser(description="Auto-RedNote 小红书图文笔记渲染脚本")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("-o", "--output-dir", default=".", help="输出目录")
    parser.add_argument("-t", "--theme", default="default",
                        choices=list(THEME_STYLES.keys()), help="布局主题")
    parser.add_argument("-m", "--mode", default="separator",
                        choices=["separator", "auto-fit", "auto-split", "dynamic"],
                        help="分页模式")
    parser.add_argument("-w", "--width", type=int, default=1080, help="图片宽度")
    parser.add_argument("--height", type=int, default=1440, help="图片高度")
    parser.add_argument("--max-height", type=int, default=4320, help="dynamic模式最大高度")
    parser.add_argument("--dpr", type=int, default=2, help="设备像素比")

    args = parser.parse_args()

    # 显示主题信息
    theme_info = THEME_STYLES.get(args.theme, THEME_STYLES["default"])
    print(f"主题: {theme_info['name']}")
    print(f"模式: {args.mode}")

    # 渲染
    render_markdown(
        args.input,
        args.output_dir,
        args.theme,
        args.mode,
        args.width,
        args.height,
        args.max_height,
        args.dpr,
    )


if __name__ == "__main__":
    main()
