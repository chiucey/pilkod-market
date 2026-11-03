#!/usr/bin/env python3
"""
Package Skill Script for Expert Coordination Framework
Creates a distributable .skill package for publishing
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


def get_file_hashes(directory: Path) -> dict:
    """Calculate SHA256 hashes for all files in directory."""
    hashes = {}
    for item in sorted(directory.rglob("*")):
        if item.is_file() and not item.name.startswith("."):
            rel_path = str(item.relative_to(directory))
            sha256_hash = hashlib.sha256(item.read_bytes()).hexdigest()
            hashes[rel_path] = sha256_hash
    return hashes


def create_package(skill_path: str, output_dir: str = None) -> tuple[bool, str]:
    """
    Create a .skill package from the skill directory.

    Returns:
        tuple: (success, output_path or error_message)
    """
    skill_path = Path(skill_path)

    if not skill_path.exists() or not skill_path.is_dir():
        return False, f"Skill path does not exist: {skill_path}"

    # Read metadata
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        return False, "_meta.json not found"

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"Invalid _meta.json: {e}"

    skill_name = meta.get("name", skill_path.name)
    skill_id = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")

    # Determine output path
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent / "dist"

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{skill_name}.skill"

    # Create manifest
    manifest = {
        "name": skill_name,
        "id": skill_id,
        "version": version,
        "packaged_at": datetime.now().isoformat(),
        "files": {}
    }

    # Build package
    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add all files from skill directory
            for item in sorted(skill_path.rglob("*")):
                if item.is_file() and not item.name.startswith("."):
                    rel_path = str(item.relative_to(skill_path))

                    # Skip the package itself if in dist folder
                    if str(output_file) == str(item.resolve()):
                        continue

                    zf.write(item, arcname=rel_path)

                    # Calculate hash
                    file_hash = hashlib.sha256(item.read_bytes()).hexdigest()
                    manifest["files"][rel_path] = {
                        "size": item.stat().st_size,
                        "hash": file_hash
                    }

        # Save manifest alongside package
        manifest_file = output_dir / f"{skill_name}.manifest.json"
        manifest_file.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        return True, str(output_file)

    except Exception as e:
        return False, f"Failed to create package: {e}"


def extract_package(package_path: str, output_dir: str = None) -> tuple[bool, str]:
    """
    Extract a .skill package to a directory.

    Returns:
        tuple: (success, output_path or error_message)
    """
    package_path = Path(package_path)

    if not package_path.exists():
        return False, f"Package not found: {package_path}"

    if output_dir:
        output_dir = Path(output_dir)
    else:
        # Extract to parent directory with skill name
        output_dir = package_path.parent / package_path.stem

    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            zf.extractall(output_dir)
        return True, str(output_dir)
    except Exception as e:
        return False, f"Failed to extract package: {e}"


def verify_package(package_path: str) -> tuple[bool, list[str]]:
    """
    Verify integrity of a .skill package.

    Returns:
        tuple: (success, list of issues)
    """
    package_path = Path(package_path)

    if not package_path.exists():
        return False, [f"Package not found: {package_path}"]

    issues = []

    # Check manifest exists
    manifest_path = package_path.with_suffix(".manifest.json")
    if not manifest_path.exists():
        issues.append("Manifest file not found alongside package")

    # Verify zip integrity
    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            bad_file = zf.testzip()
            if bad_file:
                issues.append(f"Corrupted file in package: {bad_file}")
    except zipfile.BadZipFile:
        return False, ["Invalid zip file format"]

    # Verify required files
    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            namelist = zf.namelist()
            required = ["SKILL.md", "_meta.json"]
            for req in required:
                if req not in namelist:
                    issues.append(f"Missing required file: {req}")
    except Exception as e:
        issues.append(f"Failed to verify package: {e}")

    return len(issues) == 0, issues


def package(skill_path: str, output_dir: str = None) -> bool:
    """Package a skill and print results."""
    print(f"\nPackaging skill: {skill_path}")
    print("=" * 50)

    success, result = create_package(skill_path, output_dir)

    if success:
        print(f"✓ Package created: {result}")

        # Verify the package
        verify_success, issues = verify_package(result)
        if verify_success:
            print(f"✓ Package verification PASSED")
        else:
            print(f"✗ Package verification FAILED:")
            for issue in issues:
                print(f"  - {issue}")
            return False

        print("=" * 50)
        print(f"✓ Packaging SUCCESSFUL")
        return True
    else:
        print(f"✗ Packaging FAILED: {result}")
        print("=" * 50)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python package_skill.py <skill_path> [output_dir]")
        print("  python package_skill.py --verify <package_path>")
        sys.exit(1)

    if sys.argv[1] == "--verify":
        if len(sys.argv) < 3:
            print("Usage: python package_skill.py --verify <package_path>")
            sys.exit(1)
        success, issues = verify_package(sys.argv[2])
        if success:
            print("✓ Package verification PASSED")
            sys.exit(0)
        else:
            print("✗ Package verification FAILED:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    success = package(sys.argv[1], output_dir)
    sys.exit(0 if success else 1)
