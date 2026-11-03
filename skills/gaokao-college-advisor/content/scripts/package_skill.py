#!/usr/bin/env python3
"""
高考志愿填报技能打包脚本
将技能打包为可发布的 .skill 文件
"""

import os
import json
import shutil
import zipfile
from datetime import datetime

def get_skill_info(skill_dir):
    """获取技能元信息"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def package_skill(skill_dir, output_dir='.'):
    """打包技能为 .skill 文件"""
    meta = get_skill_info(skill_dir)
    skill_name = os.path.basename(skill_dir)
    version = meta.get('version', '1.0.0')

    output_file = os.path.join(output_dir, f"{skill_name}-{version}.skill")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return output_file

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    package_skill(skill_dir)
