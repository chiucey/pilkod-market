#!/usr/bin/env python3
"""
Sudoku Skill Packager
将数独技能打包为可分发的 .skill 文件
"""

import os
import zipfile
import sys

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_name = os.path.basename(skill_path)

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 创建打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和不必要的目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arcname)

    print(f"✅ Skill packaged: {output_file}")
    return output_file

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/sudoku"
    output_file = package_skill(skill_path)
    print(f"Output: {output_file}")