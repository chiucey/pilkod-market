#!/usr/bin/env python3
"""
打包脚本 - 将技能打包为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def get_skill_info(skill_dir):
    """从 _meta.json 获取技能信息"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_skill_name(skill_dir):
    """从 SKILL.md 获取技能名称"""
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        import yaml
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        return frontmatter.get('name', os.path.basename(skill_dir))
    return os.path.basename(skill_dir)

def collect_skill_files(skill_dir):
    """收集技能文件（排除临时文件和隐藏文件）"""
    files = []
    excluded_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
    excluded_files = {'.DS_Store', 'Thumbs.db'}

    for root, dirs, filenames in os.walk(skill_dir):
        # 排除不需要的目录
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for filename in filenames:
            # 排除不需要的文件
            if filename in excluded_files or filename.startswith('.'):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, skill_dir)
            files.append(rel_path)

    return sorted(files)

def create_skill_archive(skill_dir, output_dir=None):
    """创建技能归档文件"""
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    # 获取技能信息
    skill_name = get_skill_name(skill_dir)
    meta = get_skill_info(skill_dir)
    version = meta.get('version', '1.0.0')

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_name = f"{skill_name}-{version}.skill"
    output_path = os.path.join(output_dir, output_name)

    # 收集文件
    files = collect_skill_files(skill_dir)

    # 创建 ZIP 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = os.path.join(skill_dir, file_path)
            zf.write(full_path, file_path)

    print(f"Skill packaged successfully!")
    print(f"  Name: {skill_name}")
    print(f"  Version: {version}")
    print(f"  Files: {len(files)}")
    print(f"  Output: {output_path}")

    return output_path

def verify_archive(archive_path):
    """验证归档文件"""
    print("\nVerifying archive...")

    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            files = zf.namelist()

            # 检查必填文件
            required = ['SKILL.md', '_meta.json']
            missing = [f for f in required if f not in files]

            if missing:
                print(f"  ✗ Missing required files: {missing}")
                return False

            # 检查安全
            for file in files:
                if file.startswith('/') or '..' in file:
                    print(f"  ✗ Unsafe file path: {file}")
                    return False

            print(f"  ✓ All required files present")
            print(f"  ✓ No unsafe paths detected")
            print(f"  ✓ Archive is valid")

            return True

    except zipfile.BadZipFile:
        print(f"  ✗ Invalid ZIP file")
        return False

def main():
    # 获取技能目录路径
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Packaging skill at: {skill_dir}")
    print("=" * 50)

    # 创建归档
    archive_path = create_skill_archive(skill_dir)

    # 验证归档
    if verify_archive(archive_path):
        print("\n✓ Packaging completed successfully!")
        return 0
    else:
        print("\n✗ Packaging failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
