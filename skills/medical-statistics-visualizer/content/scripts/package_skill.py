#!/usr/bin/env python3
"""
Medical Statistics Visualizer - 技能打包脚本
"""

import os
import shutil
import zipfile
from pathlib import Path

SKILL_DIR = Path('/workspace/temp-skills/medical-statistics-visualizer')
OUTPUT_DIR = Path('/workspace/temp-skills/output')
OUTPUT_DIR.mkdir(exist_ok=True)

def package_skill():
    """打包技能为 .skill 文件"""
    skill_name = 'medical-statistics-visualizer'
    output_file = OUTPUT_DIR / f'{skill_name}.skill'

    # 创建ZIP文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in SKILL_DIR.rglob('*'):
            if file_path.is_file():
                # 排除临时文件和 __pycache__
                if '__pycache__' in str(file_path) or '.pyc' in str(file_path):
                    continue
                arcname = file_path.relative_to(SKILL_DIR)
                zf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"\nPackage created: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")
    return output_file

if __name__ == '__main__':
    package_skill()
