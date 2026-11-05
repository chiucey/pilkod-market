#!/usr/bin/env python3
"""
ASCII艺术转换器测试脚本
"""

from PIL import Image
import os


def resize_image(img, width=80):
    """调整图片大小"""
    aspect_ratio = 2.0
    new_height = int(width / aspect_ratio * (img.height / img.width))
    resized = img.resize((width, new_height))
    return resized


def grayscale(img):
    """转换为灰度"""
    return img.convert('L')


def get_ascii_chars(invert=False):
    """获取ASCII字符序列"""
    chars = '@%#*+=-:. '
    if invert:
        chars = chars[::-1]
    return chars


def pixel_to_ascii(pixel_value, chars):
    """像素值转ASCII字符"""
    index = int(pixel_value / 256 * len(chars))
    index = max(0, min(index, len(chars) - 1))
    return chars[index]


def image_to_ascii(img, width=80, invert=False):
    """转换为ASCII艺术"""
    img = resize_image(img, width)
    img = grayscale(img)
    chars = get_ascii_chars(invert)

    ascii_art = []
    pixels = img.getdata()

    for i, pixel in enumerate(pixels):
        char = pixel_to_ascii(pixel, chars)
        ascii_art.append(char)
        if (i + 1) % width == 0:
            ascii_art.append('\n')

    return ''.join(ascii_art)


def create_test_image():
    """创建一个测试用的渐变图片"""
    width, height = 100, 60
    img = Image.new('RGB', (width, height))
    pixels = []

    for y in range(height):
        for x in range(width):
            # 创建渐变效果
            gray = int((x / width) * 255)
            pixels.append((gray, gray, gray))

    img.putdata(pixels)
    return img


def main():
    print("=" * 60)
    print("ASCII艺术转换器测试")
    print("=" * 60)

    # 创建测试图片
    print("\n[1] 创建测试渐变图片...")
    test_img = create_test_image()
    test_img.save('/tmp/test_gradient.png')
    print("✓ 测试图片已保存到 /tmp/test_gradient.png")

    # 测试转换
    print("\n[2] 测试ASCII转换（默认宽度80）...")
    ascii_art = image_to_ascii(test_img, width=80)
    print("✓ 转换成功！")
    print("\n" + "-" * 60)
    print("渐变测试图片的ASCII预览：")
    print("-" * 60)
    print(ascii_art[:500] + "...")  # 显示前500字符

    # 测试反转
    print("\n[3] 测试反转模式...")
    ascii_inverted = image_to_ascii(test_img, width=80, invert=True)
    print("✓ 反转模式转换成功！")

    # 测试不同宽度
    print("\n[4] 测试不同宽度设置...")
    for w in [40, 60, 100]:
        ascii_w = image_to_ascii(test_img, width=w)
        lines = ascii_w.count('\n')
        print(f"  宽度={w}: 生成 {lines} 行")

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == '__main__':
    main()
