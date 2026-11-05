#!/usr/bin/env python3
"""技能打包脚本"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def package_skill(skill_path):
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 输出路径
    output_dir = skill_path.parent / 'dist'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{skill_name}.skill"

    # 清理旧文件
    if output_file.exists():
        output_file.unlink()

    # 打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file() and not str(file_path).startswith(str(skill_path / 'dist')):
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ 技能已打包: {output_file}")
    return output_file

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"打包技能: {skill_path}")
    print("-" * 40)
    output = package_skill(skill_path)
    print("-" * 40)
    print(f"输出文件: {output.absolute()}")

if __name__ == '__main__':
    main()
