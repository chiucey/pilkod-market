#!/usr/bin/env python3
"""
NLP语料生成器技能打包脚本
生成可分发的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_skill_metadata(skill_path):
    """获取技能元数据"""
    meta_file = Path(skill_path) / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def package_skill(skill_path, output_dir=None):
    """打包技能为.skill文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 获取元数据
    meta = get_skill_metadata(skill_path)
    version = meta.get('version', '1.0.0')

    # 创建输出目录
    if output_dir is None:
        output_dir = Path(skill_path).parent / "dist"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}_{version}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除dist目录
            if 'dist' in dirs:
                dirs.remove('dist')
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"技能已打包: {output_file}")
    return str(output_file)

def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n打包成功: {output_file}")
    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()