#!/usr/bin/env python3
"""
PDF转图片转换器
将PDF文件的每一页转换为高质量图片

依赖: pip install pdf2image Pillow
Linux额外依赖: apt-get install poppler-utils
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    print("错误: 请先安装 pdf2image 库")
    print("运行: pip install pdf2image Pillow")
    sys.exit(1)


def pdf_to_images(
    pdf_path: str,
    output_dir: str = None,
    output_format: str = "png",
    dpi: int = 300,
    first_page: int = None,
    last_page: int = None,
) -> list:
    """
    将PDF转换为图片

    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录，默认与PDF同目录
        output_format: 输出格式，png 或 jpeg
        dpi: 图片分辨率，默认300
        first_page: 起始页（可选）
        last_page: 结束页（可选）

    Returns:
        生成的图片文件路径列表
    """
    # 验证输入文件
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("输入文件必须是PDF格式")

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path) or "."

    os.makedirs(output_dir, exist_ok=True)

    # 确定输出格式
    fmt = output_format.lower()
    if fmt not in ["png", "jpeg", "jpg"]:
        fmt = "png"

    # 构建输出文件名模板
    pdf_name = Path(pdf_path).stem
    output_template = os.path.join(output_dir, f"{pdf_name}_page_%03d.{fmt}")

    # 转换参数
    convert_kwargs = {
        "dpi": dpi,
        "output_folder": output_dir,
        "output_file": f"{pdf_name}_page_%03d",
        "fmt": fmt,
        "thread_count": 4,
    }

    if first_page is not None:
        convert_kwargs["first_page"] = first_page
    if last_page is not None:
        convert_kwargs["last_page"] = last_page

    # 执行转换
    print(f"正在转换 PDF: {pdf_path}")
    print(f"输出目录: {output_dir}")
    print(f"图片格式: {fmt.upper()}, DPI: {dpi}")

    images = convert_from_path(pdf_path, **convert_kwargs)

    # 保存图片
    output_files = []
    for i, image in enumerate(images, start=1):
        if first_page is not None:
            page_num = first_page + i - 1
        else:
            page_num = i

        output_path = os.path.join(
            output_dir, f"{pdf_name}_page_{page_num:03d}.{fmt}"
        )
        image.save(output_path, fmt.upper())
        output_files.append(output_path)
        print(f"  已保存: {output_path}")

    print(f"\n转换完成! 共生成 {len(output_files)} 张图片")
    return output_files


def main():
    parser = argparse.ArgumentParser(
        description="将PDF转换为图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python pdf_to_images.py input.pdf
  python pdf_to_images.py input.pdf --format jpeg --dpi 150
  python pdf_to_images.py input.pdf --output-dir ./images --dpi 300
  python pdf_to_images.py input.pdf --first-page 1 --last-page 5
        """,
    )

    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument(
        "--output-dir", "-o", default=None, help="输出目录（默认与PDF同目录）"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["png", "jpeg", "jpg"],
        default="png",
        help="输出格式（默认png）",
    )
    parser.add_argument(
        "--dpi", "-d", type=int, default=300, help="图片分辨率 DPI（默认300）"
    )
    parser.add_argument(
        "--first-page", type=int, help="起始页码（可选）"
    )
    parser.add_argument(
        "--last-page", type=int, help="结束页码（可选）"
    )

    args = parser.parse_args()

    try:
        output_files = pdf_to_images(
            pdf_path=args.pdf_path,
            output_dir=args.output_dir,
            output_format=args.format,
            dpi=args.dpi,
            first_page=args.first_page,
            last_page=args.last_page,
        )
        print("\n生成的文件:")
        for f in output_files:
            print(f"  {f}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
