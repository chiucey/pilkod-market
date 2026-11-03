#!/usr/bin/env python3
"""
Viral Script Creator - Skill Packager
将技能打包为 .skill 文件
"""

import os
import json
import zipfile
from pathlib import Path
import sys


def package_skill(skill_path: Path, output_path: Path = None) -> tuple[bool, str]:
    """打包技能为 .skill 文件"""
    if not skill_path.exists():
        return False, f"Skill path not found: {skill_path}"

    if output_path is None:
        output_path = skill_path.parent / f"{skill_path.name}.skill"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_path)
                zf.write(file_path, arc_name)

    # 验证打包内容
    with zipfile.ZipFile(output_path, 'r') as zf:
        file_list = zf.namelist()
        has_skill_md = any('SKILL.md' in f for f in file_list)
        has_meta = any('_meta.json' in f for f in file_list)
        if not has_skill_md:
            return False, "Package missing SKILL.md"
        if not has_meta:
            return False, "Package missing _meta.json"

    return True, str(output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_path]")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    print("-" * 50)

    passed, result = package_skill(skill_path, output_path)

    if passed:
        print(f"✓ Skill packaged successfully!")
        print(f"  Output: {result}")
        with zipfile.ZipFile(result, 'r') as zf:
            print("\nPackage contents:")
            for name in sorted(zf.namelist()):
                info = zf.getinfo(name)
                print(f"  - {name} ({info.file_size} bytes)")
    else:
        print(f"✗ Packaging failed: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
