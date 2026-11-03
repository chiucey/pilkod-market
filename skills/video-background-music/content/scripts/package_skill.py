#!/usr/bin/env python3
"""
技能打包脚本
将技能文件夹打包为 .skill 文件
"""

import os
import shutil
import json
from pathlib import Path


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """
    打包技能为 .skill 文件

    Args:
        skill_dir: 技能目录路径
        output_dir: 输出目录，默认与技能目录同级的 dist

    Returns:
        打包后的 .skill 文件路径
    """
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_dir}")

    # 读取 meta 信息
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_name = skill_dir.name
    else:
        raise ValueError("_meta.json 不存在")

    # 设置输出目录
    if output_dir is None:
        output_dir = skill_dir.parent / "dist"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建打包文件
    output_file = output_dir / f"{skill_name}.skill"

    # 打包（使用 shutil.make_archive）
    shutil.make_archive(
        str(output_file.with_suffix('')),  # 不带后缀
        'zip',
        root_dir=skill_dir.parent,
        base_dir=skill_name
    )

    # 重命名为 .skill
    zip_file = output_file.with_suffix('.zip')
    if output_file.exists():
        output_file.unlink()
    shutil.move(str(zip_file), str(output_file))

    print(f"技能打包完成: {output_file}")
    return str(output_file)


if __name__ == "__main__":
    import sys

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_dir, output_dir)
