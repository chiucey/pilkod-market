#!/usr/bin/env python3
"""
教学论文写作助手 - 技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import zipfile
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_package(skill_dir, output_dir=None):
    """创建技能包"""
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        print(f"错误：技能目录不存在：{skill_dir}")
        return False

    if not skill_dir.is_dir():
        print(f"错误：{skill_dir} 不是目录")
        return False

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取技能信息
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_name = meta.get('id', skill_dir.name)
        skill_version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_dir.name
        skill_version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f"{skill_name}_{skill_version}_{timestamp}.skill"
    output_path = output_dir / output_filename

    # 创建压缩包
    print(f"正在打包技能：{skill_dir.name}")
    print(f"输出文件：{output_path}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除隐藏文件和临时文件
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)

                # 验证文件安全性（防止符号链接逃逸）
                if '..' in str(arcname):
                    print(f"警告：跳过不安全的文件路径：{arcname}")
                    continue

                zipf.write(file_path, arcname)
                print(f"  添加：{arcname}")

    print(f"\n✓ 打包完成！")
    print(f"  文件路径：{output_path}")
    print(f"  文件大小：{output_path.stat().st_size / 1024:.2f} KB")

    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description='打包技能为 .skill 文件')
    parser.add_argument('skill_path', nargs='?', default=None,
                        help='技能目录路径（默认为当前脚本所在目录）')
    parser.add_argument('-o', '--output', dest='output_dir', default=None,
                        help='输出目录')

    args = parser.parse_args()

    if args.skill_path:
        skill_dir = Path(args.skill_path)
    else:
        # 默认使用脚本所在目录的父目录（即技能目录）
        script_dir = Path(__file__).parent
        skill_dir = script_dir.parent

    success = create_package(skill_dir, args.output_dir)

    if not success:
        import sys
        sys.exit(1)

if __name__ == '__main__':
    main()
