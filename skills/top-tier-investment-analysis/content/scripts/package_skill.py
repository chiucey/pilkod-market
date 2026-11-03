#!/usr/bin/env python3
"""
Package Skill Script
Creates a distributable .skill archive from a skill directory
"""

import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path


# Files/directories to exclude from package
EXCLUDE_PATTERNS = [
    ".git",
    ".svn",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "Thumbs.db",
    ".idea",
    ".vscode",
    "node_modules",
    ".venv",
    "venv",
    "*.md",
    "LICENSE",
    "README.md",
    ".env",
    ".env.*",
]

# Files to always include
REQUIRED_FILES = [
    "SKILL.md",
    "_meta.json",
]


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from package"""
    path_str = str(path)
    name = path.name

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True

    return False


def validate_skill_structure(skill_path: Path) -> bool:
    """Validate skill has required files"""
    for required in REQUIRED_FILES:
        if not (skill_path / required).exists():
            print(f"❌ Missing required file: {required}")
            return False

    print("✅ Skill structure validated")
    return True


def create_package(skill_path: str, output_path: str = None) -> str:
    """
    Create a .skill package from skill directory

    Args:
        skill_path: Path to skill directory
        output_path: Optional output path for .skill file

    Returns:
        Path to created .skill file
    """
    skill_path = Path(skill_path).resolve()
    skill_name = skill_path.name

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path does not exist: {skill_path}")

    # Validate structure
    if not validate_skill_structure(skill_path):
        raise ValueError("Invalid skill structure")

    # Determine output path
    if output_path is None:
        output_path = skill_path.parent / f"{skill_name}.skill"
    else:
        output_path = Path(output_path).resolve()

    # Remove existing package if present
    if output_path.exists():
        output_path.unlink()

    # Create temporary directory for package contents
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Copy files to temp directory
        for item in skill_path.rglob("*"):
            if should_exclude(item):
                continue

            # Calculate relative path
            rel_path = item.relative_to(skill_path)
            dest_path = temp_path / rel_path

            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            if item.is_file():
                shutil.copy2(item, dest_path)

        # Create tar archive
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(temp_path, arcname=skill_name)

    print(f"✅ Package created: {output_path}")
    return str(output_path)


def extract_package(skill_path: str, output_dir: str = None) -> str:
    """
    Extract a .skill package

    Args:
        skill_path: Path to .skill file
        output_dir: Optional output directory

    Returns:
        Path to extracted skill directory
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"Package does not exist: {skill_path}")

    if not str(skill_path).endswith(".skill"):
        raise ValueError("File must have .skill extension")

    # Determine output directory
    if output_dir is None:
        output_dir = skill_path.parent / skill_path.stem
    else:
        output_dir = Path(output_dir).resolve()

    # Remove existing directory if present
    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True)

    # Extract tar archive
    with tarfile.open(skill_path, "r:gz") as tar:
        tar.extractall(output_dir)

    print(f"✅ Package extracted to: {output_dir}")
    return str(output_dir)


def show_package_info(skill_path: str) -> None:
    """Show information about a .skill package"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"Package does not exist: {skill_path}")

    print(f"\nPackage: {skill_path.name}")
    print("-" * 50)

    with tarfile.open(skill_path, "r:gz") as tar:
        members = tar.getmembers()
        print(f"Files: {len(members)}")

        for member in members[:10]:  # Show first 10 files
            print(f"  - {member.name}")

        if len(members) > 10:
            print(f"  ... and {len(members) - 10} more files")

    # Show meta.json if available
    meta_path = skill_path.parent / skill_path.stem / "_meta.json"
    if meta_path.exists():
        with open(meta_path, "r") as f:
            meta = json.load(f)
            print(f"\nSkill ID: {meta.get('id', 'N/A')}")
            print(f"Version: {meta.get('version', 'N/A')}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Package:   python package_skill.py pack <skill_path> [output_path]")
        print("  Extract:   python package_skill.py extract <skill.skill> [output_dir]")
        print("  Info:      python package_skill.py info <skill.skill>")
        print("\nExamples:")
        print("  python package_skill.py pack ../my-skill")
        print("  python package_skill.py pack ../my-skill ./my-skill.skill")
        print("  python package_skill.py extract ./my-skill.skill")
        print("  python package_skill.py info ./my-skill.skill")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "pack":
        if len(sys.argv) < 3:
            print("❌ Missing skill_path argument")
            sys.exit(1)

        skill_path = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None

        try:
            result = create_package(skill_path, output_path)
            print(f"\n📦 Package ready: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    elif command == "extract":
        if len(sys.argv) < 3:
            print("❌ Missing skill.skill argument")
            sys.exit(1)

        skill_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None

        try:
            result = extract_package(skill_path, output_dir)
            print(f"\n📂 Extraction complete: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Missing skill.skill argument")
            sys.exit(1)

        skill_path = sys.argv[2]

        try:
            show_package_info(skill_path)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
