#!/usr/bin/env python3
"""
Package skill for distribution
Creates a .skill archive file for sharing
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "/workspace/temp-skills") -> str:
    """Package skill directory into a .skill file"""

    skill_name = os.path.basename(skill_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # Files to include (security check)
    allowed_extensions = {'.md', '.json', '.py', '.txt', '.yml', '.yaml'}
    allowed_files = {'_meta.json', 'SKILL.md'}

    files_to_package = []

    for root, dirs, files in os.walk(skill_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, skill_dir)

            # Security: skip forbidden patterns
            forbidden = ['.env', 'credentials', 'secrets', 'id_rsa', '.pem', '__pycache__']
            if any(f in file.lower() for f in forbidden):
                print(f"⏭️  Skipping forbidden file: {rel_path}")
                continue

            files_to_package.append((file_path, rel_path))

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for abs_path, rel_path in files_to_package:
            zf.write(abs_path, rel_path)
            print(f"📦 Added: {rel_path}")

    print(f"\n✅ Skill packaged successfully: {output_file}")
    return output_file


def main():
    skill_dir = "/workspace/temp-skills/daily-news-briefing"

    print("=" * 50)
    print("📦 Daily News Briefing - Skill Packager")
    print("=" * 50)

    if not os.path.exists(skill_dir):
        print(f"❌ Skill directory not found: {skill_dir}")
        return 1

    output = package_skill(skill_dir)

    print("\n" + "=" * 50)
    print(f"📦 Output: {output}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    exit(main())
