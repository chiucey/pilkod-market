#!/usr/bin/env python3
"""
技能打包脚本 - 生成 .skill 文件用于分发
"""

import os
import sys
import json
import zipfile
import datetime
import re

def sanitize_path(path):
    """确保路径安全，不允许逃逸到上级目录"""
    return os.path.normpath(path).startswith(os.getcwd())

def get_skill_info(skill_dir):
    """读取技能信息"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')

    if not os.path.exists(meta_path):
        raise ValueError(f"缺少 _meta.json 文件: {meta_path}")

    if not os.path.exists(skill_md_path):
        raise ValueError(f"缺少 SKILL.md 文件: {skill_md_path}")

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 提取 name
    name = os.path.basename(skill_dir)

    return {
        'name': name,
        'id': meta.get('id'),
        'version': meta.get('version', '1.0.0')
    }

def collect_files(skill_dir):
    """收集技能目录下的所有文件"""
    allowed_extensions = {'.md', '.json', '.py', '.txt', '.yaml', '.yml'}
    files_to_include = []

    for root, dirs, files in os.walk(skill_dir):
        # 排除隐藏目录和 __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.startswith('.') or file.startswith('__'):
                continue

            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            if ext in allowed_extensions or file in ['_meta.json']:
                rel_path = os.path.relpath(file_path, skill_dir)
                files_to_include.append({
                    'full_path': file_path,
                    'rel_path': rel_path
                })

    return files_to_include

def create_skill_package(skill_dir, output_path=None):
    """创建技能包"""
    skill_info = get_skill_info(skill_dir)

    if output_path is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        output_path = os.path.join(
            os.path.dirname(skill_dir),
            f"{skill_info['name']}_{skill_info['version']}_{timestamp}.skill"
        )

    files = collect_files(skill_dir)

    if not files:
        raise ValueError("没有找到要打包的文件")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_info in files:
            zf.write(
                file_info['full_path'],
                file_info['rel_path']
            )
            print(f"  + {file_info['rel_path']}")

    print(f"\n✅ 技能包已创建: {output_path}")
    print(f"   技能名称: {skill_info['name']}")
    print(f"   技能ID: {skill_info['id']}")
    print(f"   版本: {skill_info['version']}")
    print(f"   文件数: {len(files)}")

    return output_path

def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_directory> [output_path]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.isdir(skill_dir):
        print(f"❌ 错误: 目录不存在: {skill_dir}")
        sys.exit(1)

    abs_skill_dir = os.path.abspath(skill_dir)
    print(f"正在打包技能: {abs_skill_dir}")
    print("-" * 50)

    try:
        output = create_skill_package(abs_skill_dir, output_path)
        print("-" * 50)
        print(f"打包完成!")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
