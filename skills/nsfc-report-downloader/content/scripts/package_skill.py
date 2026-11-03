#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path


def validate_skill(skill_dir: Path) -> bool:
    """验证技能结构"""
    required_files = ['SKILL.md', '_meta.json']

    for filename in required_files:
        filepath = skill_dir / filename
        if not filepath.exists():
            print(f"❌ 缺少必填文件: {filename}")
            return False

    # 验证 _meta.json
    with open(skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            print("❌ _meta.json 必须包含 id 和 version 字段")
            return False

    # 验证 SKILL.md frontmatter
    with open(skill_dir / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            print("❌ SKILL.md 必须以 frontmatter --- 开头")
            return False

    return True


def package_skill(skill_dir: Path, output_dir: Path = None) -> str:
    """打包技能为 .skill 文件"""
    skill_name = skill_dir.name

    if output_dir is None:
        output_dir = skill_dir.parent

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{skill_name}.skill"

    # 安全检查 - 禁止符号链接逃逸
    def is_safe_path(path: Path) -> bool:
        resolved = path.resolve()
        skill_dir_resolved = skill_dir.resolve()
        return str(resolved).startswith(str(skill_dir_resolved))

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in skill_dir.rglob('*'):
            if item.is_file():
                if not is_safe_path(item):
                    print(f"⚠️ 跳过不安全的路径: {item}")
                    continue

                arcname = item.relative_to(skill_dir)
                zf.write(item, arcname)
                print(f"  添加: {arcname}")

    print(f"\n✅ 技能打包完成: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")
    return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"❌ 技能目录不存在: {skill_dir}")
        sys.exit(1)

    print(f"📦 正在打包技能: {skill_dir.name}")
    print()

    if not validate_skill(skill_dir):
        print("\n❌ 验证失败，无法打包")
        sys.exit(1)

    print()
    output_path = package_skill(skill_dir, output_dir)
    print()
    print(f"📤 输出文件: {output_path}")


if __name__ == "__main__":
    main()
