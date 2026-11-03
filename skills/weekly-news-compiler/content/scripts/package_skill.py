#!/usr/bin/env python3
"""
Package skill for distribution
Creates a .skill archive for the weekly-news-compiler skill
"""
import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_root():
    """Get skill root directory"""
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    return Path(__file__).parent.parent


def validate_skill_structure(root: Path) -> tuple[bool, list[str]]:
    """Validate skill structure"""
    errors = []

    # Check required files
    required = ['SKILL.md', '_meta.json']
    for f in required:
        if not (root / f).exists():
            errors.append(f"Missing required file: {f}")

    # Validate SKILL.md frontmatter
    skill_md = root / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            errors.append("SKILL.md must start with frontmatter")
        if 'name:' not in content:
            errors.append("SKILL.md missing 'name' field")
        if 'description:' not in content:
            errors.append("SKILL.md missing 'description' field")

    # Validate _meta.json
    meta_json = root / '_meta.json'
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id'")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version'")
        except json.JSONDecodeError:
            errors.append("_meta.json is invalid JSON")

    return len(errors) == 0, errors


def package_skill(root: Path, output_dir: Path = None) -> str:
    """Package skill into .skill archive"""
    if output_dir is None:
        output_dir = root.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get skill name from folder
    skill_name = root.name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and .pyc files
                if '__pycache__' in str(file_path) or file_path.suffix == '.pyc':
                    continue
                arcname = file_path.relative_to(root)
                zf.write(file_path, arcname)

    return str(output_file)


def main():
    root = get_skill_root()

    print(f"Packaging skill: {root}")
    print("-" * 50)

    # Validate
    valid, errors = validate_skill_structure(root)
    if not valid:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("✓ Structure validation passed")

    # Package
    output_file = package_skill(root)
    print(f"✓ Packaged to: {output_file}")

    # Show contents
    print("\nArchive contents:")
    with zipfile.ZipFile(output_file, 'r') as zf:
        for name in sorted(zf.namelist()):
            print(f"  {name}")

    print(f"\n✓ Done! Skill file: {output_file}")


if __name__ == "__main__":
    main()
