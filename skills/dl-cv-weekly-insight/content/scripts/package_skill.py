#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a compressed archive with proper structure.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_info(skill_path: Path) -> dict:
    """Extract skill metadata from _meta.json."""
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text(encoding="utf-8"))
    return {}


def scan_for_secrets(skill_path: Path) -> list[str]:
    """Scan for potentially sensitive files to exclude."""
    secrets = []
    secret_patterns = [
        r"\.env$",
        r"\.key$",
        r"\.pem$",
        r"credentials",
        r"secrets",
        r"password",
        r"token",
        r"\.git",
        r"__pycache__",
        r"\.pyc$",
    ]

    for f in skill_path.rglob("*"):
        if f.is_file():
            name_lower = f.name.lower()
            for pattern in secret_patterns:
                if pattern.lower() in name_lower:
                    secrets.append(str(f.relative_to(skill_path)))
                    break

    return secrets


def create_skill_package(skill_path: str, output_dir: str = None) -> Path:
    """
    Create a .skill package file.

    Args:
        skill_path: Path to the skill directory
        output_dir: Optional output directory (defaults to skill parent)

    Returns:
        Path to the created .skill file
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        raise ValueError(f"Invalid skill path: {skill_path}")

    # Get skill info
    meta = get_skill_info(skill_path)
    skill_name = meta.get("id", skill_path.name)
    version = meta.get("version", "1.0.0")

    # Set output path
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create package filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_name}-{version}.skill"
    package_path = output_dir / package_name

    # Scan for secrets
    secrets = scan_for_secrets(skill_path)
    if secrets:
        print("⚠️  Warning: Found potential sensitive files (will be excluded):")
        for s in secrets:
            print(f"   - {s}")

    # Create zip archive
    print(f"Packaging skill: {skill_name} v{version}")

    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # Skip secrets
                rel_path = file_path.relative_to(skill_path)
                if any(s in str(rel_path) for s in secrets):
                    continue

                # Skip hidden files at root level
                if rel_path.parts[0].startswith(".") and rel_path.parts[0] != ".git":
                    continue

                zf.write(file_path, rel_path)
                print(f"  + {rel_path}")

    print(f"\n✅ Package created: {package_path}")
    print(f"   Size: {package_path.stat().st_size:,} bytes")

    return package_path


def verify_package(package_path: Path) -> bool:
    """Verify a .skill package can be read and contains required files."""
    required_files = ["SKILL.md", "_meta.json"]

    try:
        with zipfile.ZipFile(package_path, "r") as zf:
            names = zf.namelist()

            # Check required files
            for req in required_files:
                if req not in names:
                    print(f"❌ Missing required file: {req}")
                    return False

            # Validate frontmatter in SKILL.md
            skill_md = zf.read("SKILL.md").decode("utf-8")
            if not skill_md.strip().startswith("---"):
                print("❌ SKILL.md does not start with frontmatter")
                return False

            # Validate _meta.json
            meta = json.loads(zf.read("_meta.json").decode("utf-8"))
            if "id" not in meta or "version" not in meta:
                print("❌ _meta.json missing required fields")
                return False

        print("✅ Package verification passed")
        return True

    except zipfile.BadZipFile:
        print("❌ Invalid zip file")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        # Default: package parent of scripts dir
        script_path = Path(__file__).resolve()
        skill_path = script_path.parent.parent
        output_dir = None
    else:
        skill_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    skill_path = Path(skill_path)
    print(f"Skill path: {skill_path}")
    print("-" * 50)

    try:
        package_path = create_skill_package(skill_path, output_dir)
        print("-" * 50)
        verify_package(package_path)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
