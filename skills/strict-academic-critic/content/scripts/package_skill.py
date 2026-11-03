#!/usr/bin/env python3
"""
Package skill to .skill file for distribution.
Creates a zip archive with SKILL.md and _meta.json.
"""

import sys
import zipfile
from pathlib import Path


def package_skill(skill_dir: Path, output_path: Path = None):
    """Package skill directory into a .skill archive."""
    skill_dir = Path(skill_dir)

    # Find SKILL.md and _meta.json
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'

    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found in {skill_dir}")
        sys.exit(1)

    if not meta_json.exists():
        print(f"ERROR: _meta.json not found in {skill_dir}")
        sys.exit(1)

    # Determine output path
    if output_path is None:
        skill_name = skill_dir.name
        output_path = Path(f"{skill_name}.skill")
    else:
        output_path = Path(output_path)

    # Create zip archive
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add SKILL.md
        zf.write(skill_md, arcname='SKILL.md')
        print(f"  Added: SKILL.md")

        # Add _meta.json
        zf.write(meta_json, arcname='_meta.json')
        print(f"  Added: _meta.json")

        # Add scripts/ if exists
        scripts_dir = skill_dir / 'scripts'
        if scripts_dir.exists():
            for script in scripts_dir.glob('*.py'):
                zf.write(script, arcname=f'scripts/{script.name}')
                print(f"  Added: scripts/{script.name}")

        # Add references/ if exists
        refs_dir = skill_dir / 'references'
        if refs_dir.exists():
            for ref in refs_dir.rglob('*'):
                if ref.is_file():
                    arc_path = f'references/{ref.name}'
                    zf.write(ref, arcname=arc_path)
                    print(f"  Added: {arc_path}")

    print(f"\nPackaged to: {output_path}")
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir> [output_path]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    package_skill(skill_dir, output_path)


if __name__ == '__main__':
    main()