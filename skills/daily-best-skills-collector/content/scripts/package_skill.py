#!/usr/bin/env python3
"""
Skill packaging script.
Creates a distributable .skill archive from a validated skill directory.
"""

import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path


def gather_skill_files(skill_path: Path) -> list[Path]:
    """Gather all files to include in the package, excluding build artifacts."""
    exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", "tmp"}
    exclude_files = {".DS_Store", "Thumbs.db", "*.pyc"}

    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # Filter excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in filenames:
            # Skip excluded files
            if any(filename.endswith(ext[1:]) for ext in exclude_files if ext.startswith("*")):
                continue

            file_path = Path(root) / filename
            # Make path relative to skill root
            rel_path = file_path.relative_to(skill_path)
            files.append((file_path, rel_path))

    return files


def create_package(skill_path: Path, output_dir: Path) -> Path:
    """Create a .skill package archive."""
    skill_name = skill_path.name

    # Read meta for version
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        version = meta.get("version", "1.0.0")
        skill_id = meta.get("id", "unknown")
    else:
        version = "1.0.0"
        skill_id = "unknown"

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"{skill_name}_v{version}_{timestamp}.skill"
    output_path = output_dir / output_name

    # Gather files
    files = gather_skill_files(skill_path)

    if not files:
        raise ValueError("No files found to package")

    # Create tar archive
    with tarfile.open(output_path, "w:gz") as tar:
        for file_path, rel_path in files:
            tar.add(file_path, arcname=str(rel_path))

    return output_path


def validate_package(output_path: Path, skill_path: Path) -> bool:
    """Validate the created package can be extracted and matches expectations."""
    try:
        with tarfile.open(output_path, "r:gz") as tar:
            members = tar.getmembers()

            # Check required files exist
            required_files = {"SKILL.md", "_meta.json"}
            extracted_names = {m.name for m in members}

            for req in required_files:
                if req not in extracted_names:
                    print(f"  WARNING: Missing required file in package: {req}")

            # List all files
            print("\n  Package contents:")
            member_names = [m.name for m in members]
            for name in sorted(member_names):
                print(f"    - {name}")

            return True

    except Exception as e:
        print(f"  Package validation failed: {e}")
        return False


def main():
    """Package the skill."""
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "dist").resolve()

    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"Error: Skill path must be a directory: {skill_path}")
        sys.exit(1)

    print(f"Packaging skill: {skill_path.name}")
    print("-" * 50)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Create package
        output_path = create_package(skill_path, output_dir)
        print(f"\n✓ Package created: {output_path.name}")
        print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

        # Validate package
        print("\nValidating package...")
        if validate_package(output_path, skill_path):
            print("\n✓ Package validated successfully!")
            print(f"\nFull path: {output_path}")
        else:
            print("\n✗ Package validation failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
