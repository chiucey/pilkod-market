#!/usr/bin/env python3
"""
Package skill files into a .skill archive
Usage: python package_skill.py <skill_directory>
"""

import zipfile
import os
import sys
from datetime import datetime

def package_skill(skill_dir, output_dir="/workspace"):
    """Package a skill directory into a .skill file"""

    # Resolve absolute paths
    skill_dir = os.path.abspath(skill_dir)
    output_dir = os.path.abspath(output_dir)

    # Validate directory exists
    if not os.path.isdir(skill_dir):
        print(f"Error: Directory not found: {skill_dir}")
        sys.exit(1)

    # Get skill name from directory
    skill_name = os.path.basename(skill_dir)

    # Create output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # Collect files to package
    files_to_package = []
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, skill_dir)
            files_to_package.append((file_path, arcname))

    if not files_to_package:
        print("Warning: No files found to package")

    # Create .skill archive (ZIP format)
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, arcname in files_to_package:
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

        print(f"\n✅ Successfully created: {output_file}")
        print(f"   Size: {os.path.getsize(output_file):,} bytes")
        print(f"   Files: {len(files_to_package)}")

        return output_file

    except Exception as e:
        print(f"Error creating archive: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]
    package_skill(skill_dir)