#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a clean .skill archive from the skill directory.
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# Files/directories to exclude from packaging
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".git",
    ".DS_Store",
    "*.pyc",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "out",  # output directory
    "*.log",
    ".env",
]

def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
        if pattern.startswith("*.") and path_str.endswith(pattern[1:]):
            return True
    return False

def create_package(skill_dir: Path, output_dir: Path = None) -> Path:
    """Create a .skill package from the skill directory."""
    skill_dir = skill_dir.resolve()

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    # Load meta for version info
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        skill_name = f"{skill_dir.name}-{meta.get('version', '1.0.0')}"
    else:
        skill_name = skill_dir.name

    # Output location
    if output_dir is None:
        output_dir = Path.cwd() / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create package filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_name}-{timestamp}.skill"
    package_path = output_dir / package_name

    # Build file list (exclude unwanted)
    files_to_add = []
    for item in skill_dir.rglob("*"):
        if should_exclude(item):
            continue
        if item.is_file():
            rel_path = item.relative_to(skill_dir)
            files_to_add.append((item, rel_path))

    # Create the zip package
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, rel_path in files_to_add:
            zf.write(file_path, rel_path)

    print(f"✅ Package created: {package_path}")
    print(f"   Size: {package_path.stat().st_size:,} bytes")
    print(f"   Files: {len(files_to_add)}")

    # Print contents summary
    print("\n📦 Package contents:")
    for _, rel_path in sorted(files_to_add):
        print(f"   - {rel_path}")

    return package_path

def verify_package(package_path: Path) -> bool:
    """Verify the created package can be opened and read."""
    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            # Check for essential files
            names = zf.namelist()
            essential = ["SKILL.md", "_meta.json"]
            for req in essential:
                if not any(req in n for n in names):
                    print(f"⚠️  Missing essential file: {req}")

            # Test integrity
            bad_file = zf.testzip()
            if bad_file:
                print(f"❌ Corrupt file in archive: {bad_file}")
                return False

        print("✅ Package verification passed")
        return True
    except zipfile.BadZipFile:
        print("❌ Invalid zip file created")
        return False

def main():
    if len(sys.argv) < 2:
        # Default to parent directory of this script (skill root)
        script_dir = Path(__file__).parent.resolve()
        skill_dir = script_dir.parent
    else:
        skill_dir = Path(sys.argv[1]).resolve()

    print(f"📦 Packaging skill: {skill_dir.name}")
    print("=" * 50)

    try:
        package_path = create_package(skill_dir)
        if verify_package(package_path):
            print("\n🎉 Skill is ready for distribution!")
            print(f"   Path: {package_path}")
            sys.exit(0)
        else:
            print("\n❌ Package verification failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
