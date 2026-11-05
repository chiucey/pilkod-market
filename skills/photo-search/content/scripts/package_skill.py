#!/usr/bin/env python3
"""
Photo Search Skill - Package Script
打包技能为.skill文件
"""

import os
import zipfile
import json
import sys
from datetime import datetime

def package_skill(skill_path: str, output_path: str = None) -> bool:
    """打包技能为.skill文件"""
    try:
        skill_name = os.path.basename(skill_path.rstrip('/'))

        # 默认输出路径
        if output_path is None:
            output_path = f"{skill_path}.skill"

        print(f"\n{'='*50}")
        print(f"Packaging skill: {skill_name}")
        print(f"{'='*50}")

        # 打包文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_path):
                # 跳过临时文件和隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue

                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ Packaged to: {output_path}")
        return True

    except Exception as e:
        print(f"\n❌ Packaging failed: {e}")
        return False

if __name__ == '__main__':
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    package_skill(skill_path)