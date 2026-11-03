#!/usr/bin/env python3
"""
漂流瓶技能打包脚本
将技能文件夹打包为 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path

def package_skill(skill_dir: str, output_path: str = None):
    """打包技能文件夹"""
    skill_path = Path(skill_dir)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_dir}")

    # 获取技能名称
    skill_name = skill_path.name

    # 默认输出路径
    if output_path is None:
        output_path = f"{skill_name}.skill"

    # 验证必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = skill_path / file
        if not file_path.exists():
            raise FileNotFoundError(f"缺少必需文件: {file}")

    # 读取元数据验证
    with open(skill_path / '_meta.json', 'r') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            raise ValueError("_meta.json 必须包含 'id' 和 'version' 字段")

    # 创建打包文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  添加: {arcname}")

    print(f"\n打包完成: {output_path}")
    print(f"技能名称: {skill_name}")
    print(f"技能版本: {meta['version']}")
    print(f"技能ID: {meta['id']}")

    return output_path

if __name__ == "__main__":
    import sys

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    try:
        output = package_skill(skill_dir)
        print(f"\n成功生成技能文件: {output}")
    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)
