#!/usr/bin/env python3
"""Package ai-scientist-v2 skill for distribution."""

import os
import json
import shutil
import zipfile
from pathlib import Path

def package_skill(skill_path, output_dir=None):
    """Package skill into a distributable .skill file."""
    skill_path = Path(skill_path)
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Read meta for naming
    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    output_name = f"{meta['id']}-{meta['version']}.skill"
    output_path = output_dir / output_name

    # Create zip archive
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__ and other Python artifacts
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"[OK] Packaged skill to: {output_path}")
    print(f"     Size: {output_path.stat().st_size / 1024:.1f} KB")
    return output_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Package ai-scientist-v2 skill')
    parser.add_argument('skill_path', nargs='?', default=Path(__file__).parent.parent,
                        help='Path to skill directory')
    parser.add_argument('--output', '-o', help='Output directory')
    args = parser.parse_args()

    package_skill(args.skill_path, args.output)

if __name__ == "__main__":
    main()
