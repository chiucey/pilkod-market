#!/usr/bin/env python3
"""
图片分辨率验证脚本
检查故事插画是否符合指定的分辨率要求

分辨率标准：
- 宽高比: 9:16 (如 1080x1920)
- 可接受误差: 宽高比误差 ≤ 5%
- 最小分辨率: 宽或高 >= 800px
"""

import sys
import os
import json
from pathlib import Path
from PIL import Image
import argparse


def load_config():
    """加载分辨率配置"""
    return {
        "target_aspect_ratio": 9 / 16,  # 0.5625
        "aspect_ratio_tolerance": 0.05,  # 5% 容差
        "min_dimension": 800,            # 最小宽或高
        "target_width": 1080,
        "target_height": 1920,
        "valid_extensions": [".jpg", ".jpeg", ".png", ".webp"]
    }


def check_image_resolution(image_path: str, config: dict) -> dict:
    """
    检查单张图片分辨率

    返回:
        dict: {
            "valid": bool,
            "width": int,
            "height": int,
            "aspect_ratio": float,
            "error": str or None,
            "needs_processing": bool
        }
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size

        actual_ratio = width / height
        target_ratio = config["target_aspect_ratio"]
        tolerance = config["aspect_ratio_tolerance"]

        # 检查分辨率是否足够
        min_dim = min(width, height)
        too_small = min_dim < config["min_dimension"]

        # 检查宽高比
        ratio_diff = abs(actual_ratio - target_ratio) / target_ratio
        wrong_ratio = ratio_diff > tolerance

        result = {
            "valid": not too_small and not wrong_ratio,
            "width": width,
            "height": height,
            "aspect_ratio": round(actual_ratio, 4),
            "error": None,
            "needs_processing": wrong_ratio or too_small
        }

        if too_small:
            result["error"] = f"分辨率太小 (最小需要 {config['min_dimension']}px)"
            result["needs_processing"] = True

        if wrong_ratio:
            result["error"] = f"宽高比不正确 (期望 9:16, 实际 {width}:{height})"
            result["needs_processing"] = True

        return result

    except Exception as e:
        return {
            "valid": False,
            "width": 0,
            "height": 0,
            "aspect_ratio": 0,
            "error": str(e),
            "needs_processing": True
        }


def scan_directory(directory: str, config: dict) -> dict:
    """
    扫描目录下的所有图片

    返回:
        dict: {
            "summary": {...},
            "images": [...]
        }
    """
    dir_path = Path(directory)
    results = {
        "summary": {
            "total": 0,
            "valid": 0,
            "needs_processing": 0,
            "errors": 0
        },
        "images": []
    }

    # 扫描 frames 和 characters 目录
    for subdir in ["frames", "characters"]:
        subdir_path = dir_path / subdir
        if not subdir_path.exists():
            continue

        for ext in config["valid_extensions"]:
            for image_path in subdir_path.glob(f"*{ext}"):
                results["summary"]["total"] += 1

                check_result = check_image_resolution(str(image_path), config)
                check_result["relative_path"] = str(image_path.relative_to(dir_path))

                results["images"].append(check_result)

                if check_result["valid"]:
                    results["summary"]["valid"] += 1
                elif check_result["error"]:
                    results["summary"]["errors"] += 1
                if check_result["needs_processing"]:
                    results["summary"]["needs_processing"] += 1

    return results


def print_report(results: dict, verbose: bool = False):
    """打印检查报告"""
    print("\n" + "=" * 60)
    print("📊 图片分辨率检查报告")
    print("=" * 60)

    summary = results["summary"]
    print(f"\n📈 统计:")
    print(f"   总图片数: {summary['total']}")
    print(f"   ✅ 符合要求: {summary['valid']}")
    print(f"   ⚠️ 需要处理: {summary['needs_processing']}")
    print(f"   ❌ 错误: {summary['errors']}")

    if verbose:
        print(f"\n📋 详细结果:")
        for img in results["images"]:
            status = "✅" if img["valid"] else ("⚠️" if img["needs_processing"] else "❌")
            print(f"   {status} {img['relative_path']}")
            print(f"       分辨率: {img['width']}x{img['height']}, 宽高比: {img['aspect_ratio']:.4f}")
            if img["error"]:
                print(f"       错误: {img['error']}")

    return summary["needs_processing"] > 0


def main():
    parser = argparse.ArgumentParser(description="检查故事插画分辨率")
    parser.add_argument("directory", help="故事图片目录路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细结果")
    parser.add_argument("-j", "--json", help="输出 JSON 报告文件路径")
    parser.add_argument("--strict", action="store_true", help="严格模式: 只要有需要处理的图片就返回失败")

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"❌ 错误: 目录不存在: {args.directory}")
        sys.exit(1)

    config = load_config()
    results = scan_directory(args.directory, config)
    needs_processing = print_report(results, args.verbose)

    # 输出 JSON 报告
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 JSON 报告已保存: {args.json}")

    # 返回状态码
    if needs_processing and args.strict:
        print("\n❌ 检查失败: 存在需要处理的图片")
        sys.exit(1)
    elif results["summary"]["errors"] > 0:
        print("\n❌ 检查失败: 存在错误")
        sys.exit(1)
    else:
        print("\n✅ 检查通过")
        sys.exit(0)


if __name__ == "__main__":
    main()