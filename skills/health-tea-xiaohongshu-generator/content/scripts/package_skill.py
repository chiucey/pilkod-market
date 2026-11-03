#!/usr/bin/env python3
"""
技能打包脚本
将技能文件夹打包为 .skill 文件
"""

import os
import shutil
import zipfile
from datetime import datetime

def get_skill_dir():
    """获取技能目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_skill_name():
    """获取技能名称"""
    skill_md = os.path.join(get_skill_dir(), 'SKILL.md')
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "unknown-skill"

def get_version():
    """获取技能版本"""
    meta_path = os.path.join(get_skill_dir(), '_meta.json')
    if os.path.exists(meta_path):
        import json
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        return meta.get('version', '1.0.0')
    return '1.0.0'

def package_skill():
    """打包技能"""
    skill_dir = get_skill_dir()
    skill_name = get_skill_name()
    version = get_version()

    output_name = f"{skill_name}-{version}.skill"
    output_path = os.path.join(get_skill_dir(), output_name)

    # 如果已存在同名文件，先删除
    if os.path.exists(output_path):
        os.remove(output_path)

    # 创建 zip 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除 __pycache__ 等
            dirs[:] = [d for d in dirs if not d.startswith('__')]

            for file in files:
                if file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, get_skill_dir())
                zipf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_name}")
    print(f"📦 路径: {output_path}")
    return output_path

if __name__ == '__main__':
    package_skill()
