#!/usr/bin/env python3
"""
技能打包脚本 - 生成.skill文件
"""
import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_skill_package(skill_dir, output_dir=None):
    """创建技能包"""

    skill_name = os.path.basename(skill_dir)

    # 读取元数据
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)
    else:
        os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"{skill_name}_{skill_id}_{skill_version}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建临时目录
    temp_dir = os.path.join(output_dir, '.temp_package')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制文件（排除临时文件和隐藏文件）
    for root, dirs, files in os.walk(skill_dir):
        # 过滤隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # 计算相对路径
        rel_path = os.path.relpath(root, skill_dir)
        if rel_path == '.':
            target_dir = temp_dir
        else:
            target_dir = os.path.join(temp_dir, rel_path)

        os.makedirs(target_dir, exist_ok=True)

        # 复制文件
        for file in files:
            if file.startswith('.') or file.endswith('.pyc'):
                continue

            src = os.path.join(root, file)
            dst = os.path.join(target_dir, file)
            shutil.copy2(src, dst)

    # 创建包文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arc_name)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    # 生成包信息
    package_info = {
        'name': skill_name,
        'id': skill_id,
        'version': skill_version,
        'path': output_path,
        'size_bytes': os.path.getsize(output_path),
        'created_at': timestamp
    }

    print(f"技能包已创建: {output_path}")
    print(f"  名称: {skill_name}")
    print(f"  ID: {skill_id}")
    print(f"  版本: {skill_version}")
    print(f"  大小: {package_info['size_bytes']} bytes")

    return package_info

def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            print(f"错误: 必需文件缺失: {file}")
            sys.exit(1)

    try:
        package_info = create_skill_package(skill_dir, output_dir)
        print("\n打包成功!")
    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
