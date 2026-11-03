#!/usr/bin/env python3
"""
Package Script for equity-investment-evaluator skill
Creates a distributable .skill archive
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

SKILL_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent.parent

def get_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_manifest():
    """Create package manifest"""
    manifest = {
        "package_name": SKILL_ROOT.name,
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "files": []
    }

    for file_path in sorted(SKILL_ROOT.rglob('*')):
        if file_path.is_file():
            rel_path = file_path.relative_to(SKILL_ROOT)
            manifest["files"].append({
                "path": str(rel_path),
                "size": file_path.stat().st_size,
                "hash": get_file_hash(file_path)
            })

    return manifest

def package_skill():
    """Create .skill package"""
    output_file = OUTPUT_DIR / f"{SKILL_ROOT.name}.skill"

    print(f"Packaging skill: {SKILL_ROOT.name}")
    print(f"Output: {output_file}")
    print()

    # Create manifest
    manifest = create_manifest()

    # Create zip package
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add manifest
        manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
        zf.writestr('manifest.json', manifest_json)

        # Add all files
        for file_path in SKILL_ROOT.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(SKILL_ROOT)
                zf.write(file_path, rel_path)
                print(f"  + {rel_path}")

    print()
    print(f"Package created: {output_file}")
    print(f"Total files: {len(manifest['files'])}")
    print(f"Package size: {output_file.stat().st_size / 1024:.2f} KB")

    return str(output_file)

if __name__ == "__main__":
    try:
        output = package_skill()
        print()
        print("Packaging successful!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
