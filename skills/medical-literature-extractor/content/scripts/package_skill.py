#!/usr/bin/env python3
"""
医学文献提取器 - 技能打包脚本
将技能打包为可分发的.skill文件
"""

import json
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_meta(skill_dir: Path) -> dict:
    """读取元数据"""
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """打包技能为.skill文件"""
    if output_dir is None:
        output_dir = skill_dir.parent

    meta = get_meta(skill_dir)
    skill_name = skill_dir.name

    # 输出文件名: skill_name-id-version.skill
    output_file = output_dir / f"{skill_name}-{meta['id']}-{meta['version']}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # 避免包含__pycache__等
                if '__pycache__' in str(file_path):
                    continue
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return output_file


def main():
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    output_file = package_skill(skill_dir)

    print(f"\n打包摘要:")
    print(f"  - 技能名称: {skill_dir.name}")
    print(f"  - 技能ID: {get_meta(skill_dir)['id']}")
    print(f"  - 版本: {get_meta(skill_dir)['version']}")
    print(f"  - 输出路径: {output_file}")


if __name__ == '__main__':
    main()
