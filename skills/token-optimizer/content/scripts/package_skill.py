#!/usr/bin/env python3
"""
TOKEN优化器技能打包脚本
将技能打包为 .skill 文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_skill_meta(skill_dir):
    """读取技能元数据"""
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_skill_package(skill_dir, output_dir):
    """创建技能包"""
    skill_name = skill_dir.name
    meta = get_skill_meta(skill_dir)

    # 生成文件名: skill-name_version.skill
    output_file = output_dir / f"{skill_name}_{meta['version']}.skill"

    # 创建 zip 包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除 __pycache__ 等
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

            for file in files:
                # 排除 Python 缓存文件
                if file.endswith('.pyc') or file.endswith('.pyo'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zipf.write(file_path, arcname)

    return output_file

def main():
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    output_dir = script_dir / 'dist'

    print("=== TOKEN优化器技能打包 ===")
    print(f"技能目录: {skill_dir}")
    print(f"输出目录: {output_dir}")
    print()

    # 创建输出目录
    output_dir.mkdir(exist_ok=True)

    # 生成包
    print("正在打包...")
    output_file = create_skill_package(skill_dir, output_dir)
    print(f"\n✅ 打包完成!")
    print(f"输出文件: {output_file}")
    print(f"文件大小: {output_file.stat().st_size:,} bytes")

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
