#!/usr/bin/env python3
"""
电商美工技能打包脚本
将技能打包为 .skill 文件以便分发
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def scan_directory(path, exclude_patterns=None):
    """扫描目录生成文件列表"""
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            '*.log',
            'node_modules'
        ]

    files = []
    for root, dirs, filenames in os.walk(path):
        # 排除指定目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns]

        for filename in filenames:
            # 排除指定文件模式
            if any(pattern in filename for pattern in exclude_patterns):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, path)
            files.append(rel_path)

    return files

def create_skill_package(skill_path, output_path=None):
    """创建技能包"""

    # 获取技能名称
    skill_name = os.path.basename(skill_path)

    # 默认输出路径
    if output_path is None:
        output_path = os.path.join(os.path.dirname(skill_path), f"{skill_name}.skill")

    # 读取 meta.json 获取版本信息
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    version = meta.get('version', '1.0.0')

    # 创建临时打包目录
    temp_dir = os.path.join(os.path.dirname(skill_path), f"_temp_{skill_name}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    # 复制文件到临时目录
    shutil.copytree(skill_path, temp_dir)

    # 创建 manifest
    manifest = {
        "name": skill_name,
        "version": version,
        "created_at": datetime.now().isoformat(),
        "files": scan_directory(temp_dir)
    }

    with open(os.path.join(temp_dir, "_manifest.json"), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # 创建 zip 包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    return output_path

def extract_skill_package(skill_package_path, extract_to=None):
    """解压技能包"""

    if extract_to is None:
        extract_to = os.path.dirname(skill_package_path)

    with zipfile.ZipFile(skill_package_path, 'r') as zipf:
        zipf.extractall(extract_to)

    return extract_to

def package_skill(skill_path):
    """打包技能的主要函数"""
    print("=" * 50)
    print("电商美工技能打包工具")
    print("=" * 50)

    # 检查技能目录
    if not os.path.exists(skill_path):
        print(f"✗ 技能目录不存在: {skill_path}")
        return 1

    skill_name = os.path.basename(skill_path)
    print(f"技能名称: {skill_name}")

    # 扫描文件
    files = scan_directory(skill_path)
    print(f"文件数量: {len(files)}")
    print("\n文件列表:")
    for f in sorted(files):
        print(f"  - {f}")

    # 创建包
    output_path = create_skill_package(skill_path)
    print(f"\n✓ 技能包已创建: {output_path}")

    # 显示包大小
    size = os.path.getsize(output_path)
    print(f"包大小: {size / 1024:.2f} KB")

    print("=" * 50)
    return 0

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    exit_code = package_skill(skill_path)
    sys.exit(exit_code)
