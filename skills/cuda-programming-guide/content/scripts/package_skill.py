#!/usr/bin/env python3
"""Package CUDA Programming Guide skill for distribution."""

import os
import zipfile
import shutil
from datetime import datetime

SKILL_DIR = "/workspace/temp-skills/cuda-programming-guide"
OUTPUT_DIR = "/workspace/temp-skills"
OUTPUT_NAME = "cuda-programming-guide.skill"

def package_skill():
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_NAME)

    # Remove existing package if present
    if os.path.exists(output_path):
        os.remove(output_path)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # Skip scripts directory (internal tooling)
            if 'scripts' in root.split(os.sep):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, SKILL_DIR)
                zipf.write(file_path, arcname)

    print(f"✓ Skill packaged: {output_path}")
    print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")

    # List contents
    with zipfile.ZipFile(output_path, 'r') as zipf:
        print("\nPackage contents:")
        for info in zipf.infolist():
            print(f"  - {info.filename} ({info.file_size} bytes)")

if __name__ == "__main__":
    package_skill()