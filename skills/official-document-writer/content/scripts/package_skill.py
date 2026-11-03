#!/usr/bin/env python3
"""
公文写作技能打包脚本
将技能文件夹打包为 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    skill_dir = Path(skill_path)

    # 检查必填文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = skill_dir / file
        if not file_path.exists():
            print(f"错误：缺少必填文件 {file}")
            return False

    # 验证 _meta.json
    with open(skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            print("错误：_meta.json 必须包含 id 和 version 字段")
            return False

    # 验证 SKILL.md frontmatter
    with open(skill_dir / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            print("错误：SKILL.md 必须以 frontmatter (---) 开头")
            return False
        if 'name:' not in content[:500]:
            print("错误：SKILL.md frontmatter 必须包含 name 字段")
            return False
        if 'description:' not in content[:500]:
            print("错误：SKILL.md frontmatter 必须包含 description 字段")
            return False

    return True

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    # 验证技能结构
    if not validate_skill(skill_path):
        raise ValueError("技能结构验证失败")

    # 确定输出路径
    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_file = Path(output_dir) / f"{skill_name}.skill"

    # 创建压缩文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    return str(output_file)

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法：python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"打包成功：{output_file}")
    except Exception as e:
        print(f"打包失败：{e}")
        sys.exit(1)
