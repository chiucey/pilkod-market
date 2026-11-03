#!/usr/bin/env python3
"""
技能打包脚本
将技能打包为.skill文件用于分发
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def get_skill_info(skill_dir: str) -> dict:
    """读取技能元信息"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            return json.load(f)
    return {}

def get_skill_name(skill_dir: str) -> str:
    """获取技能名称"""
    return os.path.basename(skill_dir)

def collect_skill_files(skill_dir: str) -> list:
    """收集技能所有文件"""
    files = []
    for root, dirs, filenames in os.walk(skill_dir):
        # 排除隐藏文件和目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for filename in filenames:
            if not filename.startswith('.') and not filename.endswith('.pyc'):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, skill_dir)
                files.append(rel_path)
    return sorted(files)

def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """打包技能"""
    skill_name = get_skill_name(skill_dir)
    skill_info = get_skill_info(skill_dir)

    version = skill_info.get('version', '1.0.0')
    skill_id = skill_info.get('id', 'unknown')

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{skill_name}_{version}_{timestamp}.skill"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = output_filename

    # 创建ZIP包
    files = collect_skill_files(skill_dir)

    print(f"打包技能: {skill_name}")
    print(f"版本: {version}")
    print(f"ID: {skill_id}")
    print(f"文件数量: {len(files)}")
    print(f"输出文件: {output_path}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = os.path.join(skill_dir, file_path)
            zf.write(full_path, file_path)
            print(f"  + {file_path}")

    # 验证打包
    with zipfile.ZipFile(output_path, 'r') as zf:
        file_list = zf.namelist()
        print(f"\n打包完成，包含 {len(file_list)} 个文件")

        # 检查必需文件
        required = ['SKILL.md', '_meta.json']
        for req in required:
            if req not in file_list:
                print(f"  ⚠ 警告: 缺少必需文件 {req}")

    print(f"\n✓ 技能包已生成: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认打包当前技能
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(skill_dir), 'output')
    os.makedirs(output_dir, exist_ok=True)

    package_skill(skill_dir, output_dir)
