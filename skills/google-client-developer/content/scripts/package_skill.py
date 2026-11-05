#!/usr/bin/env python3
"""打包技能为.skill文件"""

import json
import os
import shutil
import sys
from pathlib import Path


def load_meta(skill_path: Path) -> dict:
    """加载_meta.json"""
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_skill_md(skill_path: Path) -> str:
    """加载SKILL.md"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError("SKILL.md not found")
    with open(skill_md, 'r', encoding='utf-8') as f:
        return f.read()


def validate_frontmatter(content: str) -> bool:
    """验证frontmatter格式"""
    lines = content.strip().split('\n')
    if not lines or lines[0] != '---':
        print("ERROR: SKILL.md must start with ---")
        return False

    # 找到第二个---
    try:
        end_idx = lines.index('---', 1)
    except ValueError:
        print("ERROR: Missing closing --- in frontmatter")
        return False

    # 解析frontmatter
    frontmatter = {}
    for line in lines[1:end_idx]:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    required = ['name', 'description']
    for field in required:
        if field not in frontmatter:
            print(f"ERROR: Missing required field '{field}' in frontmatter")
            return False

    return True


def package_skill(skill_path: str) -> str:
    """打包技能"""
    skill_path = Path(skill_path)

    # 验证结构
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    skill_name = skill_path.name

    # 加载验证
    meta = load_meta(skill_path)
    content = load_skill_md(skill_path)

    if not validate_frontmatter(content):
        raise ValueError("SKILL.md frontmatter validation failed")

    # 创建打包目录
    output_dir = Path("/workspace/temp-skills/packages")
    output_dir.mkdir(exist_ok=True)

    # 创建输出文件
    output_file = output_dir / f"{skill_name}.skill"

    # 打包（复制所有文件）
    if output_file.exists():
        output_file.unlink()

    # 创建tar.gz压缩包
    import tarfile
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(skill_path, arcname=skill_name)

    return str(output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path>")
        sys.exit(1)

    try:
        output = package_skill(sys.argv[1])
        print(f"SUCCESS: Skill packaged to {output}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
