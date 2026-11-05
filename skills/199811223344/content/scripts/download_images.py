#!/usr/bin/env python3
"""
口播文案配图批量下载脚本
- 支持多备选图片下载
- 自动跳过失败图片
- 生成统计报告
"""

import os
import urllib.request
import zipfile
import sys
import json
from datetime import datetime

def download_images(image_list, output_dir, zip_name):
    """
    批量下载图片

    Args:
        image_list: List of tuples (url, filename)
        output_dir: Output directory path
        zip_name: Name of the zip file to create
    """
    os.makedirs(output_dir, exist_ok=True)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    success_count = 0
    fail_count = 0
    failed_images = []

    print(f"开始下载 {len(image_list)} 张图片...")
    print("=" * 50)

    for i, (url, filename) in enumerate(image_list, 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(f"{output_dir}/{filename}", 'wb') as f:
                    f.write(response.read())
            print(f"[{i}/{len(image_list)}] ✓ {filename}")
            success_count += 1
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"[{i}/{len(image_list)}] ✗ {filename} - {error_msg}...")
            fail_count += 1
            failed_images.append((filename, error_msg))

    # Create ZIP package
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in sorted(os.listdir(output_dir)):
            zipf.write(f"{output_dir}/{filename}", filename)

    # Print summary
    print("\n" + "=" * 50)
    print("下载完成!")
    print(f"成功: {success_count}/{len(image_list)}")
    print(f"失败: {fail_count}/{len(image_list)}")
    print(f"压缩包: {zip_name}")

    if failed_images:
        print("\n失败图片:")
        for filename, error in failed_images:
            print(f"  - {filename}")

    return success_count, fail_count

def main():
    if len(sys.argv) < 2:
        print("用法: python download_images.py <json_file>")
        print("示例: python download_images.py images.json")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"错误: 文件不存在 {json_file}")
        sys.exit(1)

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    image_list = [(item['url'], item['filename']) for item in data['images']]
    output_dir = data.get('output_dir', '配图')
    zip_name = data.get('zip_name', '配图.zip')

    download_images(image_list, output_dir, zip_name)

if __name__ == "__main__":
    main()
