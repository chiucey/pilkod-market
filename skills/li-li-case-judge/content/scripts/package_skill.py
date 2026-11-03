#!/usr/bin/env python3
"""
离谱Case判定技能 - 打包脚本
将技能打包为 .skill 文件
"""

import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def read_meta(skill_path: str) -> dict:
    """读取 _meta.json"""
    meta_path = Path(skill_path) / "_meta.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_archive(skill_path: str, output_dir: str) -> str:
    """创建技能归档文件"""
    skill_name = Path(skill_path).name
    meta = read_meta(skill_path)

    # 生成输出文件名: skill_name-version.skill
    output_file = Path(output_dir) / f"{skill_name}-{meta['version']}.skill"

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                # 跳过隐藏文件和临时文件
                if file.startswith(".") or file.endswith(".pyc"):
                    continue

                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_path)
                zf.write(file_path, arc_name)

    return str(output_file)


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    skill_path = Path(skill_path).resolve()
    output_dir = Path(output_dir).resolve()

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"打包技能: {skill_path}")
    print("=" * 50)

    # 读取元数据
    meta = read_meta(str(skill_path))
    print(f"技能ID: {meta['id']}")
    print(f"版本: {meta['version']}")

    # 创建归档
    output_file = create_archive(str(skill_path), str(output_dir))
    print(f"\n✓ 打包完成: {output_file}")

    # 显示归档内容
    print("\n归档内容:")
    with zipfile.ZipFile(output_file, "r") as zf:
        for name in sorted(zf.namelist()):
            info = zf.getinfo(name)
            print(f"  - {name} ({info.file_size} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
