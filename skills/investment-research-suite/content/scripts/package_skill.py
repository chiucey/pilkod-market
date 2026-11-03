#!/usr/bin/env python3
"""
Package Skill Script for Investment Research Suite
Creates a distributable .skill package.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_package_name(skill_path: Path) -> str:
    """Generate package filename."""
    meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
    name = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")
    return f"{name}_v{version}.skill"


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """Package a skill into a .skill file."""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    package_name = get_package_name(skill_path)
    output_path = output_dir / package_name

    # Create .skill package (zip format)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and .pyc
                if '__pycache__' in str(file_path) or file_path.suffix == '.pyc':
                    continue
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"✅ Package created: {output_path}")
    print(f"   Size: {output_path.stat().st_size:,} bytes")
    return str(output_path)


def list_skill_contents(skill_path: str):
    """List contents of a skill package."""
    skill_path = Path(skill_path)
    print(f"\n📦 Skill contents: {skill_path}")
    for file_path in sorted(skill_path.rglob('*')):
        if file_path.is_file() and '__pycache__' not in str(file_path):
            rel_path = file_path.relative_to(skill_path)
            size = file_path.stat().st_size
            print(f"   {rel_path} ({size:,} bytes)")


def main():
    import sys

    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    skill_path = Path(skill_path)

    print("=" * 50)
    print("Investment Research Suite - Package Tool")
    print("=" * 50)

    # List contents
    list_skill_contents(skill_path)

    # Package
    print("\n📦 Creating package...")
    package_path = package_skill(skill_path)

    print("\n" + "=" * 50)
    print("Package ready for distribution!")
    print(f"Path: {package_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
