#!/usr/bin/env python3
"""
Package skill into a distributable .skill archive.
Creates a clean, versioned package for distribution.
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime


def get_meta(skill_path: Path) -> dict:
    """Read skill metadata."""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")
    return json.loads(meta_file.read_text(encoding="utf-8"))


def create_package(skill_path: Path, output_dir: Path = None) -> Path:
    """Create a .skill package archive."""
    skill_path = Path(skill_path)

    if output_dir is None:
        output_dir = Path.cwd() / "dist"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get metadata
    meta = get_meta(skill_path)
    skill_name = meta.get("id", skill_path.name)
    version = meta.get("version", "1.0.0")

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}-{version}.skill"

    # Files to include
    include_patterns = [
        "SKILL.md",
        "_meta.json",
    ]

    include_dirs = [
        "references",
        "scripts",
        "assets",
    ]

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add files
        for pattern in include_patterns:
            file_path = skill_path / pattern
            if file_path.exists():
                zf.write(file_path, arcname=pattern)
                print(f"  Added: {pattern}")

        # Add directories
        for dir_name in include_dirs:
            dir_path = skill_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(skill_path)
                        zf.write(file_path, arcname=str(relative_path))
                        print(f"  Added: {relative_path}")

    print(f"\nPackage created: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.2f} KB")

    return output_file


def verify_package(package_path: Path) -> bool:
    """Verify package contents."""
    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            files = zf.namelist()

            # Check required files
            required = ["SKILL.md", "_meta.json"]
            for req in required:
                if req not in files:
                    print(f"ERROR: Missing required file: {req}")
                    return False

            # Check for sensitive files
            sensitive_patterns = [".env", ".pem", ".key", "secrets"]
            for file in files:
                for pattern in sensitive_patterns:
                    if pattern in file.lower():
                        print(f"WARNING: Sensitive file in package: {file}")

            print(f"\nPackage verification PASSED")
            print(f"Total files: {len(files)}")
            for f in sorted(files):
                print(f"  - {f}")

            return True
    except zipfile.BadZipFile:
        print(f"ERROR: Invalid zip file: {package_path}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    print("-" * 50)

    try:
        package_path = create_package(skill_path, output_dir)

        print("-" * 50)
        if verify_package(package_path):
            print("\nPackage ready for distribution!")
            print(f"Path: {package_path.absolute()}")
        else:
            print("\nPackage verification failed!")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
