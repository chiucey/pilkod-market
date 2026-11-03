#!/usr/bin/env python3
"""
Skill Packager — creates a distributable .skill file from a skill directory.

Usage:
    python package_skill.py <skill-directory> [output-directory]

Example:
    python package_skill.py /home/claude/generated-skills/my-skill /mnt/user-data/outputs
"""

import fnmatch
import json
import sys
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
ROOT_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def validate_skill(skill_path: Path):
    """Minimal inline validation."""
    import re
    import yaml

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith('---'):
        return False, "No YAML frontmatter"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        fm = yaml.safe_load(match.group(1))
    except Exception as e:
        return False, f"Invalid YAML: {e}"

    if not isinstance(fm, dict):
        return False, "Frontmatter must be a dict"
    if 'name' not in fm or 'description' not in fm:
        return False, "Missing name or description"

    name = str(fm['name']).strip()
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name must be kebab-case: {name}"

    return True, f"Skill '{name}' is valid"


def package_skill(skill_path, output_dir=None):
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"❌ Skill directory not found: {skill_path}")
        return None

    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        return None
    print(f"   {message}\n")

    skill_name = skill_path.name
    out_dir = Path(output_dir).resolve() if output_dir else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{skill_name}.skill"

    try:
        with zipfile.ZipFile(out_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob('*'):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    continue
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")

        print(f"\n✅ Packaged: {out_file}")
        return out_file
    except Exception as e:
        print(f"❌ Packaging failed: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill-directory> [output-directory]")
        sys.exit(1)

    result = package_skill(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
