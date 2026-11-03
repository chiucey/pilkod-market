#!/usr/bin/env python3
"""
Oncology Case Analyzer - Skill Packager
Creates distributable .skill package
"""

import os
import shutil
import json
import zipfile
from datetime import datetime

def package_skill(skill_dir: str, output_dir: str = None):
    """Package skill into .skill file"""

    skill_name = os.path.basename(skill_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # Files to include (only actual skill content)
    include_patterns = ['SKILL.md', '_meta.json', 'references/', 'scripts/', 'assets/']
    exclude_patterns = ['__pycache__', '.pyc', '.skill', '.zip']

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(e in d for e in exclude_patterns)]

            for file in files:
                if any(e in file for e in exclude_patterns):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"✅ Skill packaged: {output_file}")
    print(f"   Size: {os.path.getsize(output_file) / 1024:.1f} KB")

    return output_file

def main():
    import sys

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_dir = os.path.join(os.path.dirname(skill_dir), 'output')
    os.makedirs(output_dir, exist_ok=True)

    package_skill(skill_dir, output_dir)

if __name__ == '__main__':
    main()
