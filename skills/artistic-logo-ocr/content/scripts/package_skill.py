#!/usr/bin/env python3
"""
艺术字Logo OCR Skill 打包脚本
Package script for Artistic Logo OCR Skill
"""

import os
import json
import shutil
import zipfile
import sys
from datetime import datetime


def get_skill_info(skill_path: str) -> dict:
    """读取skill元信息"""
    meta_path = os.path.join(skill_path, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_package(skill_path: str, output_dir: str = '.') -> str:
    """创建.skill包"""
    # 读取元信息
    meta = get_skill_info(skill_path)

    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{meta['name']}_{meta['version']}_{timestamp}.skill"
    output_path = os.path.join(output_dir, package_name)

    # 创建ZIP包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除__pycache__等
            dirs[:] = [d for d in dirs if not d.startswith('__')]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)

                # 跳过临时文件
                if file.endswith('.pyc') or file.startswith('.'):
                    continue

                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\nPackage created: {output_path}")
    return output_path


def main():
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = '.'

    # 确保路径是绝对路径
    skill_path = os.path.abspath(skill_path)

    print(f"Packaging skill from: {skill_path}")
    print("-" * 50)

    try:
        output_path = create_package(skill_path)
        print("-" * 50)
        print("Success!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
