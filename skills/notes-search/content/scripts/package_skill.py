# -*- coding: utf-8 -*-
"""
技能打包脚本 - 生成可发布的.skill文件
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime


def package_skill(skill_dir: str, output_dir: str = None):
    """
    打包技能为.skill文件

    Args:
        skill_dir: 技能目录路径
        output_dir: 输出目录，默认与技能目录同级的dist目录
    """
    skill_dir = os.path.abspath(skill_dir)
    skill_name = os.path.basename(skill_dir)

    # 默认输出目录
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(skill_dir), "dist")
    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 创建zip文件
    print(f"正在打包技能: {skill_name}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除某些目录
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'dist', 'data', '.pytest_cache']]

            for file in files:
                # 排除.pyc文件
                if file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ 技能已打包: {output_file}")
    return output_file


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)

    output_file = package_skill(skill_dir, output_dir)
    print(f"\n打包完成，可发布文件: {output_file}")


if __name__ == "__main__":
    main()