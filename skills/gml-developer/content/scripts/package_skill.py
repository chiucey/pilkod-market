#!/usr/bin/env python3
"""
打包技能脚本
将技能文件夹打包为.skill文件
"""

import os
import zipfile
import datetime

def package_skill(skill_path, output_path=None):
    """打包技能文件夹"""
    skill_name = os.path.basename(skill_path)

    if output_path is None:
        output_path = f"/workspace/temp-skills/{skill_name}.skill"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n打包完成: {output_path}")
    return output_path

if __name__ == "__main__":
    skill_path = "/workspace/temp-skills/gml-developer"
    package_skill(skill_path)