#!/usr/bin/env python3
"""
Package script for official-account-article-assistant skill.
Creates a distributable .skill package.
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = "/workspace/temp-skills") -> str:
    """Package skill into a .skill file."""

    skill_name = os.path.basename(skill_path)
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)

    return output_file

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/official-account-article-assistant"
    output = package_skill(skill_path)
    print(f"✅ Skill packaged: {output}")
