#!/usr/bin/env python3
"""
Package Skill Script for AI Creative Studio
Creates a .skill package (ZIP archive) for distribution
"""

import os
import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime


def get_version(skill_path: Path) -> str:
    """Get version from _meta.json"""
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            return meta.get("version", "1.0.0")
        except (json.JSONDecodeError, KeyError):
            pass
    return "1.0.0"


def get_skill_name(skill_path: Path) -> str:
    """Get skill name from folder"""
    return skill_path.name


def should_include(path: Path) -> bool:
    """Check if file/directory should be included in package"""
    # Always exclude these
    exclude_patterns = [
        "__pycache__",
        ".pyc",
        ".git",
        ".DS_Store",
        "Thumbs.db",
        ".pytest_cache",
    ]

    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False

    # Only include specific directories
    allowed_dirs = ["scripts", "references", "assets", "SKILL.md", "_meta.json"]
    parent_name = path.parent.name if path.parent != path else None

    if path.is_dir():
        return path.name in allowed_dirs
    elif path.is_file():
        # Include files in allowed directories or at root
        if path.parent == path:
            return path.name in allowed_dirs
        return path.parent.name in allowed_dirs

    return False


def create_package(skill_path: Path, output_dir: Path = None) -> Path:
    """Create .skill package from skill directory"""
    skill_name = get_skill_name(skill_path)
    version = get_version(skill_path)

    # Output filename: skill-name_v1.0.0.skill
    output_name = f"{skill_name}_v{version}.skill"

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_name
    else:
        output_path = skill_path.parent / output_name

    # Create ZIP archive
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in skill_path.rglob("*"):
            if should_include(item):
                arcname = item.relative_to(skill_path)
                zf.write(item, arcname)
                print(f"  + {arcname}")

    print(f"\nPackage created: {output_path}")
    return output_path


def validate_before_packaging(skill_path: Path) -> bool:
    """Basic validation before packaging"""
    required_files = ["SKILL.md", "_meta.json"]
    missing = []

    for filename in required_files:
        if not (skill_path / filename).exists():
            missing.append(filename)

    if missing:
        print(f"Error: Missing required files: {', '.join(missing)}")
        return False

    # Validate _meta.json
    try:
        meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
        if "id" not in meta or "version" not in meta:
            print("Error: _meta.json must contain 'id' and 'version'")
            return False
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: Invalid _meta.json: {e}")
        return False

    return True


def main():
    """Main entry point"""
    # Get skill path from command line or use current directory
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        return 1

    print(f"Packaging skill: {skill_path}")
    print("-" * 50)

    # Validate before packaging
    if not validate_before_packaging(skill_path):
        return 1

    # Create package
    try:
        output_path = create_package(skill_path)
        print("-" * 50)
        print("Packaging complete!")
        return 0
    except Exception as e:
        print(f"Error during packaging: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
