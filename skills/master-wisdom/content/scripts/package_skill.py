#!/usr/bin/env python3
"""Package skill into a distributable .skill file."""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

def package_skill(skill_path, output_dir="."):
    """Package skill into a .skill archive."""
    skill_name = os.path.basename(skill_path)

    # Read meta
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Create output filename
    output_file = os.path.join(
        output_dir,
        f"{skill_name}_{meta['version']}.skill"
    )

    # Create temp directory for packaging
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy skill contents
        for item in os.listdir(skill_path):
            src = os.path.join(skill_path, item)
            dst = os.path.join(tmpdir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        # Create archive
        archive_base = os.path.join(output_dir, f"{skill_name}_{meta['version']}")
        shutil.make_archive(archive_base, "zip", tmpdir)

        # Rename to .skill
        zip_file = archive_base + ".zip"
        if os.path.exists(output_file):
            os.remove(output_file)
        shutil.move(zip_file, output_file)

    print(f"Packaged skill to: {output_file}")
    return output_file

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    package_skill(skill_path, output_dir)
