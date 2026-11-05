#!/usr/bin/env python3
"""Package skill into .skill.zip file."""

import os
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path

def get_skill_meta(skill_path: str) -> dict:
    """Read skill metadata from _meta.json."""
    meta_file = Path(skill_path) / "_meta.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text(encoding="utf-8"))
    return {"id": "unknown", "version": "1.0.0"}

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """Package skill directory into .skill.zip file."""
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    # Get skill name and version
    meta = get_skill_meta(skill_path)
    skill_name = skill_dir.name
    version = meta.get("version", "1.0.0")

    # Output filename
    output_file = Path(output_dir) / f"{skill_name}.skill.zip"

    # Files/dirs to include
    include_patterns = [".md", ".json"]

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)

                # Check if file should be included
                if any(file.endswith(ext) for ext in include_patterns):
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

    print(f"\n✅ Skill packaged: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/workspace"
    package_skill(skill_path, output_dir)
