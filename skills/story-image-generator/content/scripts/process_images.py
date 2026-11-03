#!/usr/bin/env python3
"""
图片分辨率处理脚本
将不符合 9:16 比例的图片调整为标准比例

处理方式：
1. 如果图片偏宽（横向），在两侧填充黑色边缘
2. 如果图片偏窄（纵向），在上下填充黑色边缘
3. 输出分辨率: 1080x1920 (2K: 2160x3840)
"""

import sys
import os
import json
from pathlib import Path
from PIL import Image
import argparse


# 默认配置
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
ASPECT_RATIO = 9 / 16  # 0.5625


def process_image(image_path: str, output_path: str, target_width: int = TARGET_WIDTH, target_height: int = TARGET_HEIGHT, high_quality: bool = False) -> bool:
    """
    处理单张图片，调整为 9:16 比例

    处理策略：
    - 计算目标比例
    - 缩放图片使其覆盖目标尺寸
    - 居中裁剪到目标尺寸

    Args:
        image_path: 输入图片路径
        output_path: 输出图片路径
        target_width: 目标宽度
        target_height: 目标高度
        high_quality: 是否使用高质量模式 (2K)

    Returns:
        bool: 处理是否成功
    """
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size

        # 计算目标比例
        target_ratio = target_width / target_height  # 0.5625

        # 计算原始比例
        original_ratio = original_width / original_height

        # 计算缩放后的尺寸（覆盖目标尺寸）
        if original_ratio > target_ratio:
            # 图片偏宽，需要裁剪左右
            new_height = target_height
            new_width = int(target_height * original_ratio)
        else:
            # 图片偏窄，需要裁剪上下
            new_width = target_width
            new_height = int(target_width / original_ratio)

        # 缩放图片
        with Image.open(image_path) as img:
            # 确保是 RGB 模式（处理 PNG 透明背景等）
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # 缩放
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS if high_quality else Image.Resampling.BILINEAR)

            # 计算居中裁剪的起始位置
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height

            # 裁剪
            cropped = resized.crop((left, top, right, bottom))

            # 保存
            cropped.save(output_path, "JPEG", quality=95 if high_quality else 85)

        print(f"✅ 已处理: {Path(image_path).name} -> {target_width}x{target_height}")
        return True

    except Exception as e:
        print(f"❌ 处理失败: {Path(image_path).name} - {str(e)}")
        return False


def process_directory(directory: str, dry_run: bool = False, high_quality: bool = False, backup: bool = True) -> dict:
    """
    处理目录下所有图片

    Args:
        directory: 图片目录路径
        dry_run: 是否只报告不处理
        high_quality: 是否使用 2K 分辨率
        backup: 是否备份原始图片

    Returns:
        dict: 处理结果统计
    """
    dir_path = Path(directory)
    results = {
        "total": 0,
        "processed": 0,
        "failed": 0,
        "skipped": 0,
        "backup_dir": None
    }

    # 目标分辨率
    target_width = 2160 if high_quality else 1080
    target_height = 3840 if high_quality else 1920

    # 创建备份目录
    if backup and not dry_run:
        backup_dir = dir_path / "_original_backup"
        backup_dir.mkdir(exist_ok=True)
        results["backup_dir"] = str(backup_dir)

    # 扫描图片
    valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    for subdir in ["frames", "characters"]:
        subdir_path = dir_path / subdir
        if not subdir_path.exists():
            continue

        for ext in valid_extensions:
            for image_path in subdir_path.glob(f"*{ext}"):
                results["total"] += 1

                # 检查是否需要处理
                with Image.open(image_path) as img:
                    width, height = img.size

                actual_ratio = width / height
                target_ratio = target_width / target_height
                ratio_diff = abs(actual_ratio - target_ratio) / target_ratio

                # 如果比例正确且分辨率足够，跳过
                if ratio_diff <= 0.01 and width >= target_width * 0.9:
                    results["skipped"] += 1
                    print(f"⏭️  跳过（已符合要求）: {image_path.name}")
                    continue

                if dry_run:
                    print(f"🔧 需要处理: {image_path.name} ({width}x{height} -> {target_width}x{target_height})")
                    continue

                # 备份原始图片
                if backup:
                    backup_path = backup_dir / image_path.name
                    with Image.open(image_path) as img:
                        img.save(backup_path)

                # 处理图片
                output_path = image_path.with_suffix(".jpg")  # 统一输出为 JPEG
                if process_image(str(image_path), str(output_path), target_width, target_height, high_quality):
                    results["processed"] += 1

                    # 如果原文件不是 jpg，删除原文件
                    if image_path.suffix.lower() != ".jpg":
                        image_path.unlink()
                else:
                    results["failed"] += 1

    return results


def print_process_report(results: dict, dry_run: bool = False):
    """打印处理报告"""
    print("\n" + "=" * 60)
    print("🖼️ 图片分辨率处理报告")
    print("=" * 60)

    mode = "[干运行模式]" if dry_run else ""
    print(f"\n📈 统计 {mode}:")
    print(f"   总图片数: {results['total']}")
    print(f"   ✅ 已处理: {results['processed']}")
    print(f"   ⏭️  已跳过: {results['skipped']}")
    print(f"   ❌ 失败: {results['failed']}")

    if results["backup_dir"]:
        print(f"   📁 备份目录: {results['backup_dir']}")

    if dry_run:
        print("\n💡 提示: 移除 --dry-run 参数以实际处理图片")


def main():
    parser = argparse.ArgumentParser(description="处理故事插画分辨率")
    parser.add_argument("directory", help="故事图片目录路径")
    parser.add_argument("--dry-run", action="store_true", help="只报告不处理")
    parser.add_argument("--2k", action="store_true", dest="high_quality", help="使用 2K 分辨率 (2160x3840)")
    parser.add_argument("--no-backup", action="store_true", help="不备份原始图片")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"❌ 错误: 目录不存在: {args.directory}")
        sys.exit(1)

    results = process_directory(
        args.directory,
        dry_run=args.dry_run,
        high_quality=args.high_quality,
        backup=not args.no_backup
    )

    print_process_report(results, args.dry_run)

    # 返回状态码
    if results["failed"] > 0:
        print("\n❌ 处理失败: 存在错误")
        sys.exit(1)
    else:
        print("\n✅ 处理完成")
        sys.exit(0)


if __name__ == "__main__":
    main()