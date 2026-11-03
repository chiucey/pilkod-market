#!/usr/bin/env python3
"""
Skill Packaging Script for short-video-copywriter
Creates distributable .skill package
"""

import os
import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime

SKILL_NAME = "short-video-copywriter"


def get_version(meta_path: Path) -> str:
    """Get version from _meta.json"""
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return meta.get("version", "1.0.0")
    return "1.0.0"


def collect_files(skill_path: Path) -> list[Path]:
    """Collect all skill files excluding build artifacts"""
    excluded = {
        "__pycache__", ".git", "node_modules", ".DS_Store",
        "Thumbs.db", "*.pyc", ".venv", "venv", "scripts"
    }

    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # Filter excluded directories
        dirs[:] = [d for d in dirs if d not in excluded]

        for f in filenames:
            if f not in excluded and not f.endswith(".pyc"):
                files.append(Path(root) / f)

    return files


def create_package():
    """Create .skill package"""
    # Get the skill directory (parent of scripts)
    skill_path = Path(__file__).parent.parent
    meta_path = skill_path / "_meta.json"

    if not skill_path.exists():
        print(f"Error: Skill folder not found at {skill_path}")
        return False

    if not meta_path.exists():
        print(f"Error: _meta.json not found")
        return False

    # Generate output filename
    version = get_version(meta_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = skill_path / f"{SKILL_NAME}_v{version}_{timestamp}.skill"

    # Collect files
    files = collect_files(skill_path)
    print(f"\nFound {len(files)} files to package:")
    for f in files:
        rel_path = f.relative_to(skill_path)
        print(f"  + {rel_path}")

    # Create zip package
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            rel_path = f.relative_to(skill_path)
            zf.write(f, rel_path)

    print(f"\nPackage created: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Skill Packaging: short-video-copywriter")
    print("=" * 50)

    success = create_package()
    sys.exit(0 if success else 1)
