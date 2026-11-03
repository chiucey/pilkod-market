"""
AI Drama Director Skill - Package Script
Package skill into distributable .skill file
"""

import os
import zipfile
import json
import shutil
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = None):
    """Package skill into .skill file"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = skill_path.parent / "dist"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # Read meta
    meta_path = skill_path / "_meta.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Create zip package
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # Exclude temp files and hidden files
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)

    print(f"OK Skill packaged: {output_file}")
    print(f"OK Version: {meta['version']}")

    return str(output_file)


def main():
    import sys

    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/ai-drama-director"

    print("=" * 50)
    print("AI Drama Director Skill - Packaging Tool")
    print("=" * 50)

    output_file = package_skill(skill_path)

    print("\nPackaging complete!")
    return output_file


if __name__ == "__main__":
    main()
