#!/usr/bin/env python3
"""
Package skill script for ascii-chart
Creates a distributable .skill package
"""

import json
import os
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path


def validate_skill(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill before packaging"""
    errors = []

    # Check required files
    if not (skill_path / "SKILL.md").exists():
        errors.append("SKILL.md not found")
    if not (skill_path / "_meta.json").exists():
        errors.append("_meta.json not found")

    # Validate _meta.json
    if (skill_path / "_meta.json").exists():
        try:
            meta = json.loads((skill_path / "_meta.json").read_text())
            if "id" not in meta or "version" not in meta:
                errors.append("_meta.json missing required fields")
        except Exception as e:
            errors.append(f"Invalid _meta.json: {e}")

    # Check for secrets
    sensitive_files = []
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file in [".env", "credentials.json", "secrets.json"]:
                sensitive_files.append(file)

    if sensitive_files:
        errors.append(f"Found sensitive files: {sensitive_files}")

    return len(errors) == 0, errors


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """
    Package skill into a .skill file

    Args:
        skill_path: Path to skill directory
        output_dir: Output directory (default: same as skill_path)

    Returns:
        Path to created .skill file
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise ValueError(f"Skill path does not exist: {skill_path}")

    # Validate
    valid, errors = validate_skill(skill_path)
    if not valid:
        raise ValueError(f"Validation failed: {', '.join(errors)}")

    # Read metadata
    meta = json.loads((skill_path / "_meta.json").read_text())
    skill_name = skill_path.name
    version = meta["version"]

    # Output path
    if output_dir is None:
        output_dir = skill_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create package name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"{skill_name}_{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # Create temporary directory for package contents
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy skill contents
        for item in skill_path.iterdir():
            # Skip hidden files and __pycache__
            if item.name.startswith("."):
                continue
            if item.name == "__pycache__":
                continue

            dest = tmp_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # Create package
        with tarfile.open(package_path, "w:gz") as tar:
            tar.add(tmp_path, arcname=skill_name)

    print(f"Package created: {package_path}")
    return package_path


def list_skill_contents(skill_path: Path):
    """List contents of a skill package"""
    print(f"\nContents of {skill_path}:")
    print("-" * 40)

    with tarfile.open(skill_path, "r:gz") as tar:
        for member in tar.getmembers():
            print(f"  {member.name} ({member.size} bytes)")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # Default to ascii-chart skill
        skill_path = Path("/workspace/temp-skills/ascii-chart")
    else:
        skill_path = Path(sys.argv[1])

    print(f"Packaging skill: {skill_path}")
    print("=" * 50)

    # Validate
    print("Validating skill...")
    valid, errors = validate_skill(skill_path)
    if not valid:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✓ Validation passed")

    # Package
    print("\nCreating package...")
    try:
        package_path = package_skill(skill_path)
        print("✓ Package created successfully")

        # List contents
        list_skill_contents(package_path)

        print("\n" + "=" * 50)
        print(f"Package: {package_path}")
        return 0

    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
