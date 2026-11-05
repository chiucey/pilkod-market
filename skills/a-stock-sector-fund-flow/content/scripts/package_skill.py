#!/usr/bin/env python3
"""
A股板块资金流向技能打包脚本
将技能打包为可发布的.skill文件
"""

import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为.skill文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能路径不存在: {skill_path}")

    # 获取技能名称和版本
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json不存在")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    skill_name = skill_path.name
    version = meta.get("version", "1.0.0")

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = Path(output_dir) / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建临时打包目录（排除临时文件）
    temp_dir = Path(output_dir) / f".temp_{skill_name}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    # 复制文件到临时目录
    shutil.copytree(skill_path, temp_dir, ignore=shutil.ignore_patterns(
        '__pycache__',
        '*.pyc',
        '.DS_Store',
        '*.log'
    ))

    # 创建tar.gz归档
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(temp_dir, arcname=skill_name)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"技能打包成功: {output_file}")
    return str(output_file)


def extract_skill(skill_file: str, output_dir: str = None) -> str:
    """解压.skill文件"""
    skill_file = Path(skill_file)

    if not skill_file.exists():
        raise FileNotFoundError(f"技能文件不存在: {skill_file}")

    if output_dir is None:
        output_dir = skill_file.parent

    with tarfile.open(skill_file, "r:gz") as tar:
        tar.extractall(output_dir)

    print(f"技能解压成功: {output_dir}")
    return str(output_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  打包: python package_skill.py <skill_path> [output_dir]")
        print("  解压: python package_skill.py --extract <skill_file> [output_dir]")
        sys.exit(1)

    if sys.argv[1] == "--extract":
        if len(sys.argv) < 3:
            print("错误: 请指定要解压的.skill文件")
            sys.exit(1)
        extract_skill(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        skill_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        package_skill(skill_path, output_dir)
