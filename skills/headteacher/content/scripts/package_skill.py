#!/usr/bin/env python3
"""
Package headteacher-workbench skill for distribution.
Creates a .skill archive file.
"""
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

def read_meta(skill_dir):
    """Read skill metadata."""
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")

    return json.loads(meta_path.read_text(encoding="utf-8"))

def validate_skill(skill_dir):
    """Validate skill before packaging."""
    # Check required files
    required = ["SKILL.md", "_meta.json"]
    for f in required:
        if not (skill_dir / f).exists():
            raise FileNotFoundError(f"Required file missing: {f}")

    # Check required directories
    required_dirs = ["prompts", "references", "tools"]
    for d in required_dirs:
        if not (skill_dir / d).is_dir():
            raise FileNotFoundError(f"Required directory missing: {d}")

    # Read and validate meta
    meta = read_meta(skill_dir)
    if "id" not in meta or "version" not in meta:
        raise ValueError("_meta.json must have 'id' and 'version' fields")

    print(f"Validation passed for skill: {meta['id']} v{meta['version']}")

def create_package(skill_dir, output_dir):
    """Create .skill package."""
    meta = read_meta(skill_dir)
    skill_id = meta["id"]
    version = meta["version"]

    # Create output filename
    safe_name = skill_id.replace("/", "-").replace("\\", "-")
    output_file = output_dir / f"{safe_name}-{version}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip hidden files and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            files = [f for f in files if not f.startswith(".")]

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print(f"Package created: {output_file}")
    print(f"Package size: {output_file.stat().st_size:,} bytes")
    return output_file

def main():
    """Package the skill."""
    # Get skill directory (parent of scripts/)
    script_dir = Path(__file__).parent.resolve()
    skill_dir = script_dir.parent

    # Output to skill_packages/ directory
    output_dir = Path(__file__).parent.parent.parent / "skill_packages"
    output_dir.mkdir(exist_ok=True)

    print(f"Packaging skill: {skill_dir}")
    print(f"Output directory: {output_dir}")

    # Validate first
    validate_skill(skill_dir)

    # Create package
    output_file = create_package(skill_dir, output_dir)

    print(f"\nSuccess! Package ready at: {output_file}")

if __name__ == "__main__":
    main()
