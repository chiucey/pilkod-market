#!/usr/bin/env python3
"""
Package skill into distributable .skill file
"""
import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def package_skill(skill_dir, output_dir=None):
    """Package skill into .skill file"""
    skill_dir = Path(skill_dir)

    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)

    # Read meta
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        skill_name = meta.get('id', skill_dir.name)
        version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_dir.name
        version = '1.0.0'

    # Output file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

    # Create zip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip __pycache__ etc
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print(f"Packaged: {output_file}")
    print(f"Size: {output_file.stat().st_size} bytes")
    return output_file

def main():
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output = package_skill(skill_dir, output_dir)
        print(f"\n✅ Package created: {output}")
    except Exception as e:
        print(f"\n❌ Package failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
