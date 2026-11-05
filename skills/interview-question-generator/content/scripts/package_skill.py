#!/usr/bin/env python3
"""
Skill打包脚本
将skill目录打包成.skill文件
"""

import os
import tarfile
import json
import sys
from pathlib import Path
import re


def package_skill(skill_dir: Path, output_path: Path = None) -> bool:
    """
    打包skill目录为.skill文件

    Args:
        skill_dir: skill目录路径
        output_path: 输出文件路径（可选）

    Returns:
        打包是否成功
    """

    skill_dir = skill_dir.resolve()

    if not skill_dir.exists():
        print(f"❌ 错误：目录不存在 {skill_dir}")
        return False

    # 读取meta信息
    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        print(f"❌ 错误：缺少_meta.json")
        return False

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 确定输出文件名
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_dir.name}.skill"

    # 创建.tar.gz包
    try:
        with tarfile.open(output_path, "w:gz") as tar:
            # 添加skill目录下的所有文件
            for root, dirs, files in os.walk(skill_dir):
                # 跳过隐藏文件和目录
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for file in files:
                    if file.startswith("."):
                        continue
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(skill_dir)
                    tar.add(file_path, arcname=arcname)

        print(f"✅ Skill打包成功: {output_path}")
        print(f"   技能ID: {meta.get('id', 'N/A')}")
        print(f"   版本: {meta.get('version', 'N/A')}")
        print(f"   文件数: {len(tar.getnames())}")
        return True

    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="打包Skill")
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill目录路径")
    parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    output_path = Path(args.output) if args.output else None

    # 默认输出到skill同级目录
    if output_path is None:
        output_path = Path("/workspace/temp-skills") / f"{skill_dir.name}.skill"

    if package_skill(skill_dir, output_path):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
