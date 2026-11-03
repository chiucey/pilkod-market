#!/usr/bin/env python3
"""
dxf_to_png.py v1.0 - DXF → PNG 黑色背景预览图生成器 (v8.0 Skill companion)

将 DXF 文件渲染为黑色背景的 PNG 预览图片。
使用 ezdxf 的 matplotlib 渲染器或 Pillow 直接绘制。

Usage:
    python dxf_to_png.py <input.dxf> -o <output.png> [--bg black] [--width 1920] [--height 1080]
"""

import argparse
import sys
from pathlib import Path

try:
    import ezdxf
except ImportError:
    print("[ERROR] ezdxf not installed. Run: pip install ezdxf", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[ERROR] Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def dxf_to_png_matplotlib(dxf_path: str, output_path: str, bg_color: str = "black",
                           width: int = 1920, height: int = 1080, dpi: int = 150):
    """
    使用 matplotlib 渲染 DXF 为 PNG（推荐方式，质量最高）。
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # 非交互式后端
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    except ImportError as e:
        print(f"[WARN] matplotlib rendering not available: {e}", file=sys.stderr)
        print("[INFO] Falling back to Pillow rendering...", file=sys.stderr)
        return False

    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        # 创建 matplotlib 图形
        fig, ax = plt.subplots(1, 1, figsize=(width / dpi, height / dpi), dpi=dpi)
        
        # 设置背景色
        if bg_color.lower() == "black":
            fig.patch.set_facecolor('#000000')
            ax.set_facecolor('#000000')
        elif bg_color.lower() == "white":
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#FFFFFF')
        else:
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

        # 使用 ezdxf 的 matplotlib 渲染器
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp)

        # 移除坐标轴
        ax.set_axis_off()
        
        # 自适应缩放
        ax.autoscale_view()
        
        # 保存
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1,
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        print(f"[OK] PNG saved: {output_path} ({width}x{height}, bg={bg_color})")
        return True

    except Exception as e:
        print(f"[WARN] matplotlib rendering failed: {e}", file=sys.stderr)
        print("[INFO] Falling back to Pillow rendering...", file=sys.stderr)
        return False


def dxf_to_png_pillow(dxf_path: str, output_path: str, bg_color: str = "black",
                       width: int = 1920, height: int = 1080):
    """
    使用 Pillow 直接绘制 DXF 实体到 PNG（备用方式，质量较低）。
    仅绘制基本的线段、圆、弧和文字。
    """
    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
    except Exception as e:
        print(f"[ERROR] Cannot read DXF: {e}", file=sys.stderr)
        return False

    # 计算所有实体的包围盒
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for entity in msp:
        try:
            if hasattr(entity, 'dxf') and hasattr(entity.dxf, 'start'):
                sx, sy = entity.dxf.start.x, entity.dxf.start.y
                ex, ey = entity.dxf.end.x, entity.dxf.end.y
                min_x = min(min_x, sx, ex)
                min_y = min(min_y, sy, ey)
                max_x = max(max_x, sx, ex)
                max_y = max(max_y, sy, ey)
            elif hasattr(entity, 'dxf') and hasattr(entity.dxf, 'center'):
                cx, cy = entity.dxf.center.x, entity.dxf.center.y
                r = entity.dxf.radius if hasattr(entity.dxf, 'radius') else 0
                min_x = min(min_x, cx - r)
                min_y = min(min_y, cy - r)
                max_x = max(max_x, cx + r)
                max_y = max(max_y, cy + r)
        except Exception:
            pass

    if min_x == float('inf'):
        min_x, min_y = 0, 0
        max_x, max_y = 420, 297  # 默认 A3

    # 添加边距
    margin = 20
    dx = max_x - min_x
    dy = max_y - min_y
    
    if dx < 1 or dy < 1:
        dx, dy = 420, 297
        min_x, min_y = 0, 0

    # 计算缩放比例
    scale_x = (width - 2 * margin) / dx
    scale_y = (height - 2 * margin) / dy
    scale = min(scale_x, scale_y)

    # 偏移量
    offset_x = margin + (width - 2 * margin - dx * scale) / 2
    offset_y = margin + (height - 2 * margin - dy * scale) / 2

    def transform(x, y):
        """将 DXF 坐标转换为图片像素坐标（Y 轴翻转）"""
        px = int((x - min_x) * scale + offset_x)
        py = int(height - ((y - min_y) * scale + offset_y))  # 翻转 Y 轴
        return px, py

    # 创建图片
    if bg_color.lower() == "black":
        img = Image.new('RGB', (width, height), (0, 0, 0))
        line_color = (0, 255, 0)  # 绿色线条（黑色背景更清晰）
    elif bg_color.lower() == "white":
        img = Image.new('RGB', (width, height), (255, 255, 255))
        line_color = (0, 0, 0)  # 黑色线条
    else:
        img = Image.new('RGB', (width, height), (0, 0, 0))
        line_color = (0, 255, 0)

    draw = ImageDraw.Draw(img)

    # 图层颜色映射
    layer_colors = {
        "OUTLINE": (255, 255, 255),    # 白色
        "HIDDEN": (0, 120, 255),        # 蓝色
        "CENTER": (255, 60, 60),        # 红色
        "DIM": (0, 255, 0),             # 绿色
        "TEXT": (255, 255, 0),           # 黄色
        "HATCH": (0, 255, 255),         # 青色
        "BORDER": (255, 255, 255),      # 白色
        "SECTION": (255, 0, 255),       # 品红
        "PHANTOM": (255, 0, 255),       # 品红
        "SURFACE": (0, 255, 0),        # 绿色
        "TOLERANCE": (0, 255, 0),      # 绿色
    }

    # 遍历实体并绘制
    for entity in msp:
        try:
            layer_name = entity.dxf.layer if hasattr(entity.dxf, 'layer') else "0"
            color = layer_colors.get(layer_name, line_color)
            
            # 计算线宽（OUTLINE 和 BORDER 用 2px，其余用 1px）
            lw = 2 if layer_name in ("OUTLINE", "BORDER", "SECTION") else 1

            etype = entity.dxftype()

            if etype == "LINE":
                sx, sy = transform(entity.dxf.start.x, entity.dxf.start.y)
                ex, ey = transform(entity.dxf.end.x, entity.dxf.end.y)
                draw.line([(sx, sy), (ex, ey)], fill=color, width=lw)

            elif etype == "CIRCLE":
                cx, cy = transform(entity.dxf.center.x, entity.dxf.center.y)
                r = int(entity.dxf.radius * scale)
                if r > 0:
                    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=color, width=lw)

            elif etype == "ARC":
                cx, cy = transform(entity.dxf.center.x, entity.dxf.center.y)
                r = int(entity.dxf.radius * scale)
                if r > 2:
                    import math
                    sa = math.radians(entity.dxf.start_angle)
                    ea = math.radians(entity.dxf.end_angle)
                    # 绘制弧线（用短线段近似）
                    n_steps = max(20, int(abs(ea - sa) * r / 5))
                    pts = []
                    for i in range(n_steps + 1):
                        angle = sa + (ea - sa) * i / n_steps
                        px = cx + int(r * math.cos(angle))
                        py = cy - int(r * math.sin(angle))
                        pts.append((px, py))
                    if len(pts) >= 2:
                        draw.line(pts, fill=color, width=lw)

            elif etype == "LWPOLYLINE":
                pts = []
                with entity.get_points('xy') as points:
                    for px, py in points:
                        pts.append(transform(px, py))
                if len(pts) >= 2:
                    draw.line(pts, fill=color, width=lw)

            elif etype == "TEXT" or etype == "MTEXT":
                # 文字简化绘制（仅标注点）
                if hasattr(entity.dxf, 'insert'):
                    tx, ty = transform(entity.dxf.insert.x, entity.dxf.insert.y)
                elif hasattr(entity.dxf, 'location'):
                    tx, ty = transform(entity.dxf.location.x, entity.dxf.location.y)
                else:
                    continue
                # 绘制文字标记（小十字）
                s = 3
                draw.line([(tx - s, ty), (tx + s, ty)], fill=color, width=1)
                draw.line([(tx, ty - s), (tx, ty + s)], fill=color, width=1)

        except Exception:
            pass  # 跳过无法渲染的实体

    img.save(output_path, "PNG")
    print(f"[OK] PNG saved (Pillow): {output_path} ({width}x{height}, bg={bg_color})")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate PNG preview from DXF file (black background)")
    parser.add_argument("dxf", help="Path to input DXF file")
    parser.add_argument("--output", "-o", default="preview.png",
                        help="Output PNG file path")
    parser.add_argument("--bg", default="black",
                        help="Background color: black (default), white, or hex color")
    parser.add_argument("--width", type=int, default=1920,
                        help="Output image width in pixels")
    parser.add_argument("--height", type=int, default=1080,
                        help="Output image height in pixels")
    parser.add_argument("--dpi", type=int, default=150,
                        help="DPI for matplotlib rendering")
    parser.add_argument("--fallback", action="store_true",
                        help="Force Pillow rendering (skip matplotlib)")
    args = parser.parse_args()

    dxf_path = Path(args.dxf)
    if not dxf_path.exists():
        print(f"[ERROR] DXF file not found: {dxf_path}", file=sys.stderr)
        sys.exit(1)

    # 优先使用 matplotlib 渲染（质量更高），回退到 Pillow
    if not args.fallback:
        success = dxf_to_png_matplotlib(
            str(dxf_path), args.output, args.bg,
            args.width, args.height, args.dpi
        )
        if success:
            return

    # Pillow 回退
    dxf_to_png_pillow(
        str(dxf_path), args.output, args.bg,
        args.width, args.height
    )


if __name__ == "__main__":
    main()
