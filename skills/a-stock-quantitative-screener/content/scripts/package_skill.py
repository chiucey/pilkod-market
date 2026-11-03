#!/usr/bin/env python3
"""
Package skill into .skill archive for distribution.
Creates a clean, reproducible package without secrets or build artifacts.
"""

import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_package_files(skill_path: Path) -> list[Path]:
    """Get all files to include in package, excluding unwanted patterns."""
    exclude_patterns = {
        "__pycache__", ".pyc", ".pyo", ".git", ".DS_Store",
        "Thumbs.db", ".pytest_cache", "*.log", ".env"
    }

    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # Filter out directories
        dirs[:] = [d for d in dirs if d not in exclude_patterns and not d.startswith(".")]

        for filename in filenames:
            # Skip hidden files and excluded patterns
            if filename.startswith("."):
                continue
            if any(pattern in filename for pattern in exclude_patterns):
                continue

            file_path = Path(root) / filename
            # Ensure relative path doesn't escape
            rel_path = file_path.relative_to(skill_path)
            if ".." in str(rel_path):
                print(f"Skipping unsafe path: {rel_path}")
                continue

            files.append(file_path)

    return files


def create_package(skill_path: str, output_path: str = None) -> str:
    """Create .skill package from skill directory."""
    skill_path = Path(skill_path)

    if not skill_path.is_dir():
        raise ValueError(f"Skill path is not a directory: {skill_path}")

    # Determine output path
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = skill_path.parent / f"{skill_path.name}_{timestamp}.skill"
    else:
        output_path = Path(output_path)

    # Get files to package
    files = get_package_files(skill_path)

    if not files:
        raise ValueError("No files to package")

    # Create package
    print(f"Creating package: {output_path}")
    print(f"Including {len(files)} files:")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(files):
            arcname = str(file_path.relative_to(skill_path))
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

    print(f"\nPackage created: {output_path}")
    print(f"Size: {output_path.stat().st_size:,} bytes")

    return str(output_path)


def verify_package(package_path: str) -> bool:
    """Verify package contents and structure."""
    package_path = Path(package_path)

    if not package_path.exists():
        print(f"Package not found: {package_path}")
        return False

    print(f"\nVerifying package: {package_path.name}")
    print("=" * 50)

    required_files = {"SKILL.md", "_meta.json"}
    found_files = set()

    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            for info in zf.infolist():
                found_files.add(info.filename)
                print(f"  {info.filename} ({info.file_size:,} bytes)")

        # Check required files
        missing = required_files - found_files
        if missing:
            print(f"\n[FAIL] Missing required files: {missing}")
            return False

        # Verify frontmatter
        with zipfile.ZipFile(package_path, "r") as zf:
            skill_content = zf.read("SKILL.md").decode("utf-8")
            if not skill_content.startswith("---"):
                print("\n[FAIL] SKILL.md missing frontmatter")
                return False

        # Verify meta.json
        with zipfile.ZipFile(package_path, "r") as zf:
            meta = json.loads(zf.read("_meta.json").decode("utf-8"))
            if "id" not in meta or "version" not in meta:
                print("\n[FAIL] _meta.json missing required fields")
                return False

        print("=" * 50)
        print("[PASS] Package verification passed")
        return True

    except zipfile.BadZipFile:
        print("[FAIL] Invalid ZIP file")
        return False
    except Exception as e:
        print(f"[FAIL] Verification error: {e}")
        return False


def package_skill(skill_path: str, output_path: str = None, verify: bool = True) -> str:
    """Main function to package a skill."""
    print("Skill Packager")
    print("=" * 50)

    try:
        package_path = create_package(skill_path, output_path)

        if verify:
            if verify_package(package_path):
                print("\n" + "=" * 50)
                print(f"SUCCESS: Package ready at {package_path}")
                return package_path
            else:
                print("\n[FAIL] Package verification failed")
                sys.exit(1)
        else:
            return package_path

    except Exception as e:
        print(f"\n[FAIL] Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_path]")
        print("Example: python package_skill.py ./my-skill ./my-skill-1.0.0.skill")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_path, output_path)
