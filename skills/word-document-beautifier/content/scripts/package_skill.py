#!/usr/bin/env python3
"""
打包技能为.skill文件
"""
import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_excluded_patterns():
    """获取应排除的文件模式"""
    return {
        '__pycache__',
        '.DS_Store',
        '.git',
        '.gitignore',
        '*.pyc',
        '*.pyo',
        '.pytest_cache',
        'node_modules',
        '.venv',
        'venv',
    }

def should_exclude(path, excluded_patterns):
    """检查路径是否应被排除"""
    path_str = str(path)
    name = os.path.basename(path_str)

    for pattern in excluded_patterns:
        if pattern in path_str or name == pattern:
            return True
    return False

def package_skill(skill_dir, output_dir=None):
    """打包技能目录"""
    skill_dir = Path(skill_dir).resolve()

    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        return False

    # 获取技能名称和版本
    meta_path = skill_dir / '_meta.json'
    if not meta_path.exists():
        print(f"Error: _meta.json not found in {skill_dir}")
        return False

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')

    # 创建输出目录
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path('/workspace/temp-skills')

    output_path.mkdir(parents=True, exist_ok=True)

    # 创建打包文件
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_path / f"skill_{skill_name}_v{skill_version}_{timestamp}.skill"

    # 收集所有文件
    files_to_package = []
    excluded = get_excluded_patterns()

    for root, dirs, files in os.walk(skill_dir):
        # 排除目录
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), excluded)]

        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude(file_path, excluded):
                rel_path = os.path.relpath(file_path, skill_dir)
                files_to_package.append((file_path, rel_path))

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for abs_path, rel_path in files_to_package:
            zf.write(abs_path, rel_path)

    print(f"Skill packaged successfully!")
    print(f"Output: {output_file}")
    print(f"Files included: {len(files_to_package)}")

    return str(output_file)

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else None

    if not skill_dir:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = package_skill(skill_dir, output_dir)

    if result:
        print(f"\nPackage created at: {result}")
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
