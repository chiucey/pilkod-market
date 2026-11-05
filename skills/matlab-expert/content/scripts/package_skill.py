#!/usr/bin/env python3
"""
MATLAB技能打包脚本
生成.skill归档文件用于分发
"""

import os
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能到.skill文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 创建.zip归档
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和__pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            files = [f for f in files if not f.startswith('.') and f.endswith(('.md', '.json', '.py', '.txt', '.yaml', '.yml'))]

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"✓ 技能打包成功: {output_file}")
    except Exception as e:
        print(f"✗ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
