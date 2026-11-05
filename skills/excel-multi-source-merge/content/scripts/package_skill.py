#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path
import shutil


def get_skill_meta(skill_path: str) -> dict:
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_skill_name(skill_path: str) -> str:
    """获取技能名称（从目录名）"""
    return os.path.basename(skill_path)


def collect_skill_files(skill_path: str) -> list:
    """收集技能的所有文件"""
    files = []

    for root, dirs, filenames in os.walk(skill_path):
        # 排除隐藏目录和特殊目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for filename in filenames:
            if filename.startswith('.'):
                continue

            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, skill_path)
            files.append((file_path, rel_path))

    return files


def check_safe_structure(skill_path: str) -> tuple[bool, str]:
    """检查文件结构安全性"""
    skill_name = get_skill_name(skill_path)

    # 检查是否包含符号链接
    for root, dirs, files in os.walk(skill_path, followlinks=False):
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.islink(file_path):
                return False, f"禁止符号链接: {file_path}"

    # 检查是否包含敏感文件
    sensitive_patterns = ['.env', 'secrets.json', 'credentials', 'id_rsa', '.pem']
    for root, dirs, files in os.walk(skill_path):
        for name in files:
            for pattern in sensitive_patterns:
                if pattern in name:
                    return False, f"禁止敏感文件: {name}"

    return True, ""


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能"""

    skill_name = get_skill_name(skill_path)
    meta = get_skill_meta(skill_path)

    # 安全检查
    safe, msg = check_safe_structure(skill_path)
    if not safe:
        raise ValueError(f"打包失败: {msg}")

    # 确定输出路径
    if output_dir is None:
        output_dir = os.path.dirname(skill_path) or '.'

    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 收集文件
    files = collect_skill_files(skill_path)

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, rel_path in files:
            zf.write(file_path, arcname=rel_path)

    print(f"技能已打包: {output_file}")
    print(f"版本: {meta.get('version', 'unknown')}")
    print(f"包含文件数: {len(files)}")

    return output_file


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        package_skill(skill_path, output_dir)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
