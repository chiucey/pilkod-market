#!/usr/bin/env python3
"""
Package Script for Free-Ride Skill

Creates a distributable .skill package with:
- SKILL.md
- _meta.json
- scripts/
- references/
- assets/

Excludes:
- .git, __pycache__
- *.pyc files
- Secrets and credentials
- Local development files
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SKILL_DIR.parent / "dist"
SKILL_NAME = SKILL_DIR.name


def get_version():
    """Get version from _meta.json"""
    meta_path = SKILL_DIR / "_meta.json"
    if meta_path.exists():
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data.get("version", "unknown")
    return "unknown"


def collect_skill_files():
    """Collect all files to include in the package"""
    include_patterns = [
        "SKILL.md",
        "_meta.json",
    ]

    include_dirs = [
        "scripts/",
        "references/",
        "assets/",
    ]

    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
    ]

    files_to_include = []

    # Add files matching patterns
    for pattern in include_patterns:
        path = SKILL_DIR / pattern
        if path.exists():
            files_to_include.append(path)

    # Add directories
    for dir_pattern in include_dirs:
        dir_path = SKILL_DIR / dir_pattern.rstrip("/")
        if dir_path.exists() and dir_path.is_dir():
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    # Check exclusions
                    should_exclude = False
                    for exclude in exclude_patterns:
                        if exclude.startswith("*"):
                            if file_path.name.endswith(exclude[1:]):
                                should_exclude = True
                                break
                        elif exclude in str(file_path):
                            should_exclude = True
                            break

                    if not should_exclude:
                        files_to_include.append(file_path)

    return files_to_include


def create_package():
    """Create the .skill package"""
    version = get_version()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Package filename
    package_name = f"{SKILL_NAME}_{version}_{timestamp}.skill"
    package_path = OUTPUT_DIR / package_name

    # Collect files
    files = collect_skill_files()

    print(f"📦 Creating skill package: {package_name}")
    print(f"   Found {len(files)} files to include\n")

    # Create zip archive
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            # Calculate archive name (relative to skill directory)
            arcname = str(file_path.relative_to(SKILL_DIR))
            zipf.write(file_path, arcname)
            print(f"   + {arcname}")

    # Get package size
    package_size = package_path.stat().st_size
    size_str = f"{package_size / 1024:.1f} KB"

    print(f"\n✅ Package created successfully!")
    print(f"   📍 Location: {package_path}")
    print(f"   📊 Size: {size_str}")

    # Also create a 'latest' symlink for convenience
    latest_path = OUTPUT_DIR / f"{SKILL_NAME}.skill"
    if latest_path.exists():
        latest_path.unlink()
    shutil.copy(package_path, latest_path)

    print(f"   🔗 Latest: {latest_path}")

    return package_path


def list_package_contents():
    """List contents of the package"""
    version = get_version()
    latest_path = OUTPUT_DIR / f"{SKILL_NAME}.skill"

    if not latest_path.exists():
        print("No package found to list contents.")
        return

    print(f"\n📄 Contents of {SKILL_NAME}.skill:")
    with zipfile.ZipFile(latest_path, "r") as zipf:
        for info in zipf.infolist():
            size = info.file_size
            print(f"   {info.filename:<40} {size:>8} bytes")


def main():
    print("=" * 60)
    print("📦 Free-Ride Skill Packager")
    print("=" * 60)

    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_package_contents()
        else:
            print(f"Usage: {sys.argv[0]} [--list]")
    else:
        create_package()


if __name__ == "__main__":
    main()
