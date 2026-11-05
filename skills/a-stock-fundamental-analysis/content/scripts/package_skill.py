#!/usr/bin/env python3
"""
Package A-Stock Fundamental Analysis Skill
打包A股基本面分析技能
"""

import json
import os
import shutil
from pathlib import Path


def load_meta(skill_path: Path) -> dict:
    """Load skill metadata from _meta.json"""
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing _meta.json at {meta_path}")
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill(skill_path: Path) -> bool:
    """Validate skill structure"""
    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        if not (skill_path / fname).exists():
            print(f"Missing required file: {fname}")
            return False

    # Check SKILL.md frontmatter
    with open(skill_path / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            print("SKILL.md must start with YAML frontmatter")
            return False
        if 'name:' not in content or 'description:' not in content:
            print("SKILL.md must have name and description in frontmatter")
            return False

    return True


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """Package skill into .skill file"""
    if not validate_skill(skill_path):
        raise ValueError("Skill validation failed")

    meta = load_meta(skill_path)
    skill_name = skill_path.name
    version = meta.get('version', '1.0.0')
    output_file = output_dir / f"{skill_name}_{version}.skill"

    # Create .skill file (zip format)
    shutil.make_archive(
        str(output_file.with_suffix('')),
        'zip',
        root_dir=skill_path.parent,
        base_dir=skill_name
    )

    # Rename .zip to .skill
    zip_file = output_file.with_suffix('.zip')
    if output_file.exists():
        output_file.unlink()
    shutil.move(str(zip_file), str(output_file))

    return output_file


def main():
    skill_path = Path(__file__).parent.parent
    output_dir = Path('/workspace/temp-skills')
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Packaging skill: {skill_path.name}")
    output_file = package_skill(skill_path, output_dir)
    print(f"Package created: {output_file}")
    print(f"Size: {output_file.stat().st_size} bytes")


if __name__ == '__main__':
    main()
