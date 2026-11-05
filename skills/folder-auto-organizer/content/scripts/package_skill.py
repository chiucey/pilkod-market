#!/usr/bin/env python3
"""
技能打包脚本 - 将技能文件夹打包为 .skill 文件
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime


def get_skill_meta(skill_dir: str) -> dict:
    """读取技能的 _meta.json"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_skill_info(skill_dir: str) -> dict:
    """从 SKILL.md 提取技能信息"""
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_md_path):
        raise FileNotFoundError("SKILL.md not found")

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 frontmatter
    lines = content.split('\n')
    info = {}

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()

    return info


def create_skill_package(skill_dir: str, output_dir: str = None) -> str:
    """创建技能包"""
    skill_name = Path(skill_dir).name
    meta = get_skill_meta(skill_dir)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    version = meta.get('version', '1.0.0').replace('.', '_')
    output_filename = f"{skill_name}_v{version}_{timestamp}.skill"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = output_filename

    # 收集要打包的文件
    files_to_package = []
    excluded_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        '.DS_Store',
        '*.log',
    ]

    for root, dirs, files in os.walk(skill_dir):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]

        for file in files:
            # 跳过不需要的文件
            if file.startswith('.') or file.endswith('.pyc'):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, skill_dir)
            files_to_package.append((full_path, rel_path))

    # 创建 zip 包
    print(f"打包技能: {skill_name}")
    print(f"版本: {meta.get('version')}")
    print(f"文件数量: {len(files_to_package)}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for full_path, rel_path in files_to_package:
            zipf.write(full_path, rel_path)
            print(f"  + {rel_path}")

    print(f"\n✓ 技能包已创建: {output_path}")

    # 验证包内容
    print("\n验证包内容...")
    with zipfile.ZipFile(output_path, 'r') as zipf:
        file_list = zipf.namelist()
        required = ['SKILL.md', '_meta.json']
        for req in required:
            if req not in file_list:
                raise Exception(f"打包验证失败: 缺少 {req}")

    print("✓ 包内容验证通过")

    return output_path


def main():
    if len(sys.argv) < 2:
        # 尝试当前目录
        skill_dir = os.getcwd()
    else:
        skill_dir = sys.argv[1]

    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        output_dir = os.path.join(os.path.dirname(skill_dir), 'dist')

    try:
        output_path = create_skill_package(skill_dir, output_dir)
        print(f"\n技能包路径: {output_path}")
        return 0
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
