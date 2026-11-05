#!/usr/bin/env python3
"""
Package Skill Script
将技能打包为可分发的 .skill 文件
"""

import os
import json
import zipfile
from datetime import datetime

def validate_skill(skill_path):
    """验证技能结构"""
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        fpath = os.path.join(skill_path, f)
        if not os.path.exists(fpath):
            return False, f"Missing required file: {f}"

    # 验证_meta.json
    with open(os.path.join(skill_path, '_meta.json'), 'r') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            return False, "Missing id or version in _meta.json"

    return True, "Validation passed"

def package_skill(skill_path, output_dir=None):
    """打包技能"""
    skill_name = os.path.basename(skill_path)

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # 验证
    valid, msg = validate_skill(skill_path)
    if not valid:
        print(f"Validation failed: {msg}")
        return False

    # 创建输出文件
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 创建zip包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除scripts目录（仅保留源码）
            if 'scripts' in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)

    print(f"Skill packaged successfully: {output_file}")
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    package_skill(skill_path)
