#!/usr/bin/env python3
"""
订阅号图片文字叠加工具
支持在图片上添加中文字体、阴影、描边等效果
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import argparse
import textwrap

# 默认字体路径（根据系统调整）
DEFAULT_FONTS = {
    'windows': 'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
    'darwin': '/System/Library/Fonts/PingFang.ttc',  # 苹方
    'linux': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'  # 文泉驿
}

def get_default_font():
    """获取系统默认字体"""
    import platform
    system = platform.system().lower()
    return DEFAULT_FONTS.get(system, DEFAULT_FONTS['linux'])

def add_text_to_image(image_path, output_path, text, position=(0.5, 0.5), 
                     font_size=40, font_color=(255, 255, 255), 
                     font_path=None, align='center', max_width=None,
                     shadow=True, shadow_offset=(2, 2), shadow_color=(0, 0, 0),
                     stroke=False, stroke_width=2, stroke_color=(0, 0, 0),
                     background=None, background_opacity=128):
    """
    在图片上添加文字
    
    Args:
        image_path: 背景图片路径
        output_path: 输出图片路径
        text: 要添加的文字
        position: 位置 (x, y) 比例，0-1之间
        font_size: 字体大小
        font_color: 字体颜色 (R,G,B)
        font_path: 字体文件路径
        align: 对齐方式 ('left', 'center', 'right')
        max_width: 最大宽度（像素），超出自动换行
        shadow: 是否添加阴影
        shadow_offset: 阴影偏移 (dx, dy)
        shadow_color: 阴影颜色
        stroke: 是否添加描边
        stroke_width: 描边宽度
        stroke_color: 描边颜色
        background: 文字背景颜色，None表示无背景
        background_opacity: 背景透明度 0-255
    """
    try:
        # 打开图片
        img = Image.open(image_path).convert('RGBA')
        img_width, img_height = img.size
        
        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        if font_path is None:
            font_path = get_default_font()
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            print(f"无法加载字体: {font_path}，使用默认字体")
            font = ImageFont.load_default()
        
        # 处理文字换行
        if max_width:
            # 计算每行最大字符数
            avg_char_width = font_size * 0.5  # 中文字符平均宽度
            chars_per_line = int(max_width / avg_char_width)
            lines = textwrap.wrap(text, width=chars_per_line)
        else:
            lines = [text]
        
        # 计算文字区域
        line_heights = []
        line_widths = []
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            line_widths.append(line_width)
            line_heights.append(line_height)
        
        total_height = sum(line_heights) + (len(lines) - 1) * font_size * 0.2
        max_line_width = max(line_widths)
        
        # 计算文字位置
        pos_x = int(position[0] * img_width)
        pos_y = int(position[1] * img_height)
        
        # 对齐调整
        if align == 'center':
            pos_x -= max_line_width // 2
        elif align == 'right':
            pos_x -= max_line_width
        
        # 垂直居中调整
        pos_y -= total_height // 2
        
        # 添加文字背景（如果需要）
        if background:
            padding = font_size // 4
            bg_x1 = pos_x - padding
            bg_y1 = pos_y - padding
            bg_x2 = pos_x + max_line_width + padding
            bg_y2 = pos_y + total_height + padding
            
            # 创建背景矩形
            bg_color = background + (background_opacity,)
            draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=bg_color)
        
        # 逐行绘制文字
        current_y = pos_y
        
        for i, line in enumerate(lines):
            line_x = pos_x
            
            # 行内对齐
            if align == 'center':
                line_x = pos_x + (max_line_width - line_widths[i]) // 2
            elif align == 'right':
                line_x = pos_x + (max_line_width - line_widths[i])
            
            # 绘制阴影（如果需要）
            if shadow:
                shadow_x = line_x + shadow_offset[0]
                shadow_y = current_y + shadow_offset[1]
                draw.text((shadow_x, shadow_y), line, font=font, 
                         fill=shadow_color)
            
            # 绘制描边（如果需要）
            if stroke:
                # 绘制多个方向的描边
                for dx in [-stroke_width, 0, stroke_width]:
                    for dy in [-stroke_width, 0, stroke_width]:
                        if dx == 0 and dy == 0:
                            continue
                        draw.text((line_x + dx, current_y + dy), line, 
                                 font=font, fill=stroke_color)
            
            # 绘制主文字
            draw.text((line_x, current_y), line, font=font, fill=font_color)
            
            # 更新Y位置
            current_y += line_heights[i] + font_size * 0.2
        
        # 保存图片
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=90, optimize=True)
        else:
            img.save(output_path, optimize=True)
        
        print(f"文字已添加到图片")
        print(f"文字: {text}")
        print(f"位置: {position}")
        print(f"保存到: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"添加文字时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_multiple_texts(image_path, output_path, text_configs):
    """
    添加多个文字元素
    
    Args:
        image_path: 背景图片路径
        output_path: 输出图片路径
        text_configs: 文字配置列表，每个元素是一个字典
    """
    try:
        img = Image.open(image_path).convert('RGBA')
        
        for config in text_configs:
            # 调用单文字添加函数
            success = add_text_to_image(
                image_path=image_path,
                output_path=output_path,  # 临时保存，最后会覆盖
                **config
            )
            
            if not success:
                print(f"添加文字失败: {config.get('text', '未知')}")
        
        # 最终保存
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=90, optimize=True)
        else:
            img.save(output_path, optimize=True)
        
        print(f"所有文字已添加，保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"添加多个文字时出错: {e}")
        return False

def create_wechat_cover_template():
    """创建微信公众号封面模板"""
    parser = argparse.ArgumentParser(description='订阅号图片文字添加工具')
    parser.add_argument('image', help='背景图片路径')
    parser.add_argument('--output', default='./output.jpg', 
                       help='输出图片路径 (默认: ./output.jpg)')
    parser.add_argument('--text', required=True, help='要添加的文字')
    parser.add_argument('--position-x', type=float, default=0.5,
                       help='X位置比例 (0-1, 默认: 0.5)')
    parser.add_argument('--position-y', type=float, default=0.3,
                       help='Y位置比例 (0-1, 默认: 0.3)')
    parser.add_argument('--font-size', type=int, default=60,
                       help='字体大小 (默认: 60)')
    parser.add_argument('--font-color', default='255,255,255',
                       help='字体颜色 R,G,B (默认: 255,255,255)')
    parser.add_argument('--font-path', help='字体文件路径')
    parser.add_argument('--align', choices=['left', 'center', 'right'],
                       default='center', help='对齐方式 (默认: center)')
    parser.add_argument('--max-width', type=int, 
                       help='最大宽度（像素），超出自动换行')
    parser.add_argument('--no-shadow', action='store_true',
                       help='不添加阴影')
    parser.add_argument('--stroke', action='store_true',
                       help='添加描边')
    parser.add_argument('--background', help='背景颜色 R,G,B')
    parser.add_argument('--background-opacity', type=int, default=128,
                       help='背景透明度 0-255 (默认: 128)')
    
    args = parser.parse_args()
    
    # 解析颜色
    font_color = tuple(map(int, args.font_color.split(',')))
    background = None
    if args.background:
        background = tuple(map(int, args.background.split(',')))
    
    # 调用添加文字函数
    success = add_text_to_image(
        image_path=args.image,
        output_path=args.output,
        text=args.text,
        position=(args.position_x, args.position_y),
        font_size=args.font_size,
        font_color=font_color,
        font_path=args.font_path,
        align=args.align,
        max_width=args.max_width,
        shadow=not args.no_shadow,
        stroke=args.stroke,
        background=background,
        background_opacity=args.background_opacity
    )
    
    if success:
        print("文字添加成功！")
    else:
        print("文字添加失败！")

if __name__ == '__main__':
    create_wechat_cover_template()