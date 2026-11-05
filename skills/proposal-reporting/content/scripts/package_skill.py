#!/usr/bin/env python3
"""技能打包脚本 - 生成 .skill 归档文件"""

import json
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_dir.parent
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_path / f"{skill_name}_{timestamp}.skill"

    # 读取 meta 信息
    with open(skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 创建 zip 包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 添加所有文件
        for root, dirs, files in os.walk(skill_dir):
            # 跳过 __pycache__ 等
            dirs[:] = [d for d in dirs if not d.startswith('__')]

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\n🎉 技能包已生成: {output_file}")
    print(f"   ID: {meta['id']}")
    print(f"   Version: {meta['version']}")

    return str(output_file)


if __name__ == '__main__':
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    package_skill(skill_path)
