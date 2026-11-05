#!/usr/bin/env python3
"""
打包技能为.skill文件
将技能目录打包为可分发的.skill归档文件
"""

import os
import json
import shutil
from pathlib import Path
import zipfile

def validate_skill(skill_path: str) -> bool:
    """验证技能结构是否完整"""
    required_files = ["SKILL.md", "_meta.json"]
    required_dirs = []

    path = Path(skill_path)

    # 检查必需文件
    for file in required_files:
        file_path = path / file
        if not file_path.exists():
            print(f"❌ 缺少必需文件: {file}")
            return False

    # 检查_meta.json内容
    meta_path = path / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if "id" not in meta or "version" not in meta:
        print("❌ _meta.json缺少id或version字段")
        return False

    # 检查SKILL.md的frontmatter
    skill_path_file = path / "SKILL.md"
    with open(skill_path_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        print("❌ SKILL.md必须以frontmatter开头")
        return False

    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        print("❌ SKILL.md的frontmatter格式错误")
        return False

    frontmatter = content[3:frontmatter_end]
    if 'name:' not in frontmatter or 'description:' not in frontmatter:
        print("❌ SKILL.md的frontmatter缺少name或description")
        return False

    print("✅ 技能结构验证通过")
    return True


def package_skill(skill_path: str, output_path: str = None):
    """打包技能为.skill文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    if output_path is None:
        output_path = Path(skill_path.parent) / f"{skill_name}.skill"
    else:
        output_path = Path(output_path)

    # 验证技能结构
    if not validate_skill(str(skill_path)):
        print("技能验证失败，无法打包")
        return False

    # 创建临时目录
    temp_dir = Path("/tmp/skill_package")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    # 复制文件到临时目录
    for item in skill_path.rglob('*'):
        if item.is_file():
            rel_path = item.relative_to(skill_path)
            dest = temp_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    # 创建zip文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(temp_dir)
                zipf.write(file, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"✅ 技能已打包: {output_path}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_path]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_path, output_path)
