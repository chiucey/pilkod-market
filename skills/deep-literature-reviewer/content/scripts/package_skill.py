#!/usr/bin/env python3
"""
Package Skill Script for Deep Literature Reviewer
Creates a distributable .skill package (zip archive).
"""

import argparse
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_skill_metadata(skill_dir: str) -> dict:
    """Load skill metadata from _meta.json."""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill_structure(skill_dir: str) -> tuple[bool, list]:
    """Validate skill directory structure."""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        if not os.path.exists(os.path.join(skill_dir, fname)):
            errors.append(f"Missing required file: {fname}")

    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            for field in ['id', 'name', 'version', 'description']:
                if field not in meta:
                    errors.append(f"Missing required field: {field}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid _meta.json: {e}")

    sensitive_patterns = ['.env', 'secrets.json', 'credentials.json', '*.key', '*.pem']
    for root, dirs, files in os.walk(skill_dir):
        for f in files:
            filepath = os.path.join(root, f)
            if any(f.startswith(p.replace('*', '')) or f.endswith(p.replace('*', ''))
                   for p in sensitive_patterns if '*' in p):
                errors.append(f"Sensitive file found: {filepath}")
            elif f in sensitive_patterns:
                errors.append(f"Sensitive file found: {filepath}")

    return len(errors) == 0, errors


def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """Package skill directory into a .skill zip file."""
    valid, errors = validate_skill_structure(skill_dir)
    if not valid:
        for e in errors:
            print(f"ERROR: {e}")
        raise ValueError("Skill validation failed")

    meta = get_skill_metadata(skill_dir)
    skill_name = meta.get('name', 'unknown')
    skill_version = meta.get('version', '0.0.0')

    output_filename = f"{skill_name}-{skill_version}.skill"
    output_path = os.path.join(output_dir, output_filename)

    print(f"Packaging skill: {skill_name} v{skill_version}")
    print(f"Source: {os.path.abspath(skill_dir)}")
    print(f"Output: {os.path.abspath(output_path)}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            dirs.sort()
            files.sort()

            for filename in files:
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, skill_dir)

                if '__pycache__' in filepath or filepath.endswith('.pyc'):
                    continue

                zf.write(filepath, arcname)
                print(f"  + {arcname}")

    package_hash = calculate_file_hash(output_path)

    manifest = {
        "package_version": "1.0",
        "created_at": datetime.now().isoformat(),
        "skill_name": skill_name,
        "skill_version": skill_version,
        "skill_id": meta.get('id'),
        "package_hash": package_hash,
        "files_count": sum(1 for _ in Path(skill_dir).rglob('*') if _.is_file()),
    }

    manifest_path = output_path + '.manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Package created successfully!")
    print(f"   Package: {output_path}")
    print(f"   Size: {os.path.getsize(output_path):,} bytes")
    print(f"   Hash: {package_hash[:16]}...")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Package Deep Literature Reviewer skill"
    )
    parser.add_argument('skill_dir', nargs='?', default='.',
                        help="Path to skill directory")
    parser.add_argument('--output', '-o', default='.',
                        help="Output directory")

    args = parser.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)
    output_dir = os.path.abspath(args.output)

    os.makedirs(output_dir, exist_ok=True)

    try:
        package_path = package_skill(skill_dir, output_dir)
        print(f"\nReady for distribution: {package_path}")
        return 0
    except Exception as e:
        print(f"\n❌ Packaging failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
