"""
Paper Plagiarism Checker Skill - Packaging script
Packages skill into distributable .skill file
"""

import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into .skill file"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir) if output_dir else skill_path.parent

    # Read meta
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    meta = json.loads(meta_file.read_text(encoding='utf-8'))
    skill_name = skill_path.name
    version = meta.get('version', '1.0.0')

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Security check: avoid symlink escape
                try:
                    file_path.resolve().relative_to(skill_path.resolve())
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)
                except ValueError:
                    print(f"⚠️  Skipping symlink: {file_path}")
                    continue

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/paper-plagiarism-checker"
    else:
        skill_path = sys.argv[1]

    print(f"📦 Packaging skill at: {skill_path}\n")

    try:
        output_file = package_skill(skill_path)
        print(f"✅ Package created: {output_file}")

        # Show archive contents
        print("\n📁 Archive contents:")
        with zipfile.ZipFile(output_file, 'r') as zf:
            for name in zf.namelist():
                print(f"   - {name}")

    except Exception as e:
        print(f"❌ Package failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())