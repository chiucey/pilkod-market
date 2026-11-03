#!/usr/bin/env python3
"""
漫画面板合成脚本
将多张面板图片合成为一张完整漫画页面
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont


def compose_comic(panels, titles, output, cols=2, rows=2,
                  panel_gap=10, title_height=50, font_path=None):
    """
    合成漫画页面

    Args:
        panels: 面板图片路径列表
        titles: 每个面板的标题/旁白列表
        output: 输出文件路径
        cols: 列数
        rows: 行数
        panel_gap: 面板间距（像素）
        title_height: 标题区域高度（像素）
        font_path: 字体文件路径（None为自动检测）
    """
    # 面板数量校验
    expected = cols * rows
    actual = len(panels)
    if actual < expected:
        print(f"警告：面板数量 ({actual}) 少于布局容量 ({expected})，将留空")
        # 填充空位
        for i in range(expected - actual):
            panels.append(None)
    elif actual > expected:
        print(f"警告：面板数量 ({actual}) 超过布局容量 ({expected})，将截断")
        panels = panels[:expected]
        titles = titles[:expected]

    # 加载所有面板图片
    images = []
    panel_width = 0
    panel_height = 0

    for path in panels:
        if path is None:
            images.append(None)
            continue
        try:
            img = Image.open(path).convert("RGB")
            images.append(img)
            # 统一调整尺寸
            if panel_width == 0:
                panel_width = img.width
                panel_height = img.height
            else:
                img = img.resize((panel_width, panel_height), Image.LANCZOS)
                images[-1] = img
        except Exception as e:
            print(f"错误：无法读取图片 {path}: {e}")
            images.append(None)

    # 计算画布大小
    canvas_width = cols * panel_width + (cols - 1) * panel_gap
    canvas_height = rows * (panel_height + title_height) + (rows - 1) * panel_gap

    # 创建画布（白色背景）
    canvas = Image.new("RGB", (canvas_width, canvas_height), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 尝试加载字体
    font = None
    if font_path and os.path.exists(font_path):
        try:
            font = ImageFont.truetype(font_path, size=24)
        except Exception:
            pass

    if font is None:
        # 尝试系统字体
        system_fonts = [
            "C:/Windows/Fonts/simhei.ttf",   # Windows 黑体
            "C:/Windows/Fonts/msyh.ttc",     # Windows 雅黑
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
            "/System/Library/Fonts/PingFang.ttc",  # macOS
        ]
        for fp in system_fonts:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, size=24)
                    break
                except Exception:
                    pass

    if font is None:
        font = ImageFont.load_default()

    # 粘贴面板和标题
    for idx in range(len(images)):
        row = idx // cols
        col = idx % cols

        x = col * (panel_width + panel_gap)
        y = row * (panel_height + title_height + panel_gap)

        # 绘制标题区域
        title_y = y
        draw.rectangle(
            [x, title_y, x + panel_width, title_y + title_height],
            fill=(245, 245, 245)
        )
        # 绘制标题文字
        if idx < len(titles) and titles[idx]:
            # 文字自动换行
            title_text = titles[idx]
            text_bbox = draw.textbbox((0, 0), title_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (panel_width - text_width) // 2
            text_y = title_y + (title_height - 24) // 2
            draw.text((text_x, text_y), title_text, fill=(0, 0, 0), font=font)

        # 粘贴面板图片
        if images[idx] is not None:
            panel_y = y + title_height
            canvas.paste(images[idx], (x, panel_y))

    # 保存
    canvas.save(output, "PNG", quality=95)
    print(f"✓ 漫画已保存到：{output}")
    return output


def main():
    import argparse

    parser = argparse.ArgumentParser(description="漫画面板合成工具")
    parser.add_argument("--panels", nargs="+", required=True, help="面板图片路径列表")
    parser.add_argument("--titles", nargs="+", required=True, help="每个面板的标题/旁白")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--cols", type=int, default=2, help="列数（默认2）")
    parser.add_argument("--rows", type=int, default=2, help="行数（默认2）")
    parser.add_argument("--panel-gap", type=int, default=10, help="面板间距（像素，默认10）")
    parser.add_argument("--title-height", type=int, default=50, help="标题区域高度（像素，默认50）")
    parser.add_argument("--title-font", default=None, help="标题字体路径（自动检测若未指定）")

    args = parser.parse_args()

    # 参数校验
    if len(args.panels) != len(args.titles):
        print("错误：--panels 和 --titles 的数量必须相同")
        sys.exit(1)

    compose_comic(
        panels=args.panels,
        titles=args.titles,
        output=args.output,
        cols=args.cols,
        rows=args.rows,
        panel_gap=args.panel_gap,
        title_height=args.title_height,
        font_path=args.title_font
    )


if __name__ == "__main__":
    main()
