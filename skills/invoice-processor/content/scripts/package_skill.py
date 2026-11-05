#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能打包脚本
将技能目录打包成 .skill 文件
"""
import os
import zipfile
import json
from pathlib import Path


def package_skill(skill_dir: str, output_path: str = None):
    """
    打包技能目录

    Args:
        skill_dir: 技能目录路径
        output_path: 输出文件路径（可选）
    """
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        print(f"错误: 技能目录不存在 - {skill_dir}")
        return False

    # 读取meta信息
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        print(f"错误: 缺少 _meta.json 文件")
        return False

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = meta.get('name', skill_dir.name)
    version = meta.get('version', '1.0.0')

    # 确定输出路径
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_name}.skill"
    else:
        output_path = Path(output_path)

    # 创建zip文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir.parent)
                zipf.write(file_path, arcname)

    print(f"✅ 技能包已创建: {output_path}")
    print(f"   技能名称: {skill_name}")
    print(f"   版本: {version}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir> [output_path]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_dir, output_path)
