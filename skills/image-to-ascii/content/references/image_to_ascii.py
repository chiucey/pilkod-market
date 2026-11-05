#!/usr/bin/env python3
"""
图片转ASCII艺术转换器
Image to ASCII Art Converter

使用方法：
python image_to_ascii.py <image_path> [--width 120] [--invert] [--output output.txt]
"""

import sys
from PIL import Image
import argparse


def load_image(image_path):
    """加载图片文件"""
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        print(f"错误：无法加载图片 {image_path}: {e}")
        sys.exit(1)


def resize_image(img, width=120):
    """调整图片大小以适应ASCII输出"""
    # 字符的高宽比约为 2:1（字符高度约为宽度的2倍）
    aspect_ratio = 2.0
    new_height = int(width / aspect_ratio * (img.height / img.width))
    resized = img.resize((width, new_height))
    return resized


def grayscale(img):
    """将图片转换为灰度图"""
    return img.convert('L')


def get_ascii_chars(invert=False):
    """获取ASCII字符序列"""
    # 从暗到亮的字符序列
    chars = '@%#*+=-:. '
    if invert:
        chars = chars[::-1]  # 反转
    return chars


def pixel_to_ascii(pixel_value, chars):
    """将像素灰度值转换为ASCII字符"""
    # 将0-255的灰度值映射到字符序列
    index = int(pixel_value / 256 * len(chars))
    # 确保索引在有效范围内
    index = max(0, min(index, len(chars) - 1))
    return chars[index]


def image_to_ascii(img, width=120, invert=False):
    """将图片转换为ASCII艺术"""
    # 调整大小
    img = resize_image(img, width)

    # 转换为灰度图
    img = grayscale(img)

    # 获取ASCII字符
    chars = get_ascii_chars(invert)

    # 转换为ASCII
    ascii_art = []
    pixels = img.getdata()

    for i, pixel in enumerate(pixels):
        char = pixel_to_ascii(pixel, chars)
        ascii_art.append(char)

        # 每行结束添加换行符
        if (i + 1) % width == 0:
            ascii_art.append('\n')

    return ''.join(ascii_art)


def save_to_file(ascii_art, output_path):
    """将ASCII艺术保存到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ascii_art)
    print(f"ASCII艺术已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='将图片转换为ASCII艺术')
    parser.add_argument('image_path', help='输入图片路径')
    parser.add_argument('--width', type=int, default=120, help='ASCII输出的字符宽度（默认120）')
    parser.add_argument('--invert', action='store_true', help='反转字符映射')
    parser.add_argument('--output', '-o', help='输出文件路径（可选）')

    args = parser.parse_args()

    # 加载图片
    img = load_image(args.image_path)

    # 转换为ASCII艺术
    ascii_art = image_to_ascii(img, width=args.width, invert=args.invert)

    # 输出结果
    if args.output:
        save_to_file(ascii_art, args.output)
    else:
        print(ascii_art)


if __name__ == '__main__':
    main()
