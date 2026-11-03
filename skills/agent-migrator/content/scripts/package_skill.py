#!/usr/bin/env python3
"""
Package Skill Script for Agent Migrator
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


def calculate_dir_hash(directory: str) -> str:
    """Calculate combined hash of all files in directory."""
    sha256 = hashlib.sha256()
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        files.sort()
        for filename in files:
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, directory)
            sha256.update(relpath.encode())
            with open(filepath, 'rb') as f:
                sha256.update(f.read())
    return sha256.hexdigest()


def get_skill_metadata(skill_dir: str) -> dict:
    """Load skill metadata from _meta.json."""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError("_meta.json not found in skill directory")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill_structure(skill_dir: str) -> tuple[bool, list]:
    """Validate skill directory structure."""
    errors = []

    # Required files
    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        if not os.path.exists(os.path.join(skill_dir, fname)):
            errors.append(f"Missing required file: {fname}")

    # Validate _meta.json structure
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            for field in ['id', 'name', 'version', 'description']:
                if field not in meta:
                    errors.append(f"Missing required field in _meta.json: {field}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid _meta.json: {e}")

    # Check for sensitive files
    sensitive_patterns = ['.env', 'secrets.json', 'credentials.json', '*.key', '*.pem']
    for root, dirs, files in os.walk(skill_dir):
        for f in files:
            if any(f.startswith(p.replace('*', '')) or f.endswith(p.replace('*', ''))
                   for p in sensitive_patterns if '*' in p):
                errors.append(f"Sensitive file found: {os.path.join(root, f)}")
            elif f in sensitive_patterns:
                errors.append(f"Sensitive file found: {os.path.join(root, f)}")

    return len(errors) == 0, errors


def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """
    Package skill directory into a .skill zip file.

    Returns the path to the created package.
    """
    # Validate structure
    valid, errors = validate_skill_structure(skill_dir)
    if not valid:
        for e in errors:
            print(f"ERROR: {e}")
        raise ValueError("Skill validation failed")

    # Load metadata
    meta = get_skill_metadata(skill_dir)
    skill_name = meta.get('name', 'unknown')
    skill_version = meta.get('version', '0.0.0')

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_filename = f"{skill_name}-{skill_version}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # Create zip file
    print(f"Packaging skill: {skill_name} v{skill_version}")
    print(f"Source: {os.path.abspath(skill_dir)}")
    print(f"Output: {os.path.abspath(output_path)}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Walk through skill directory
        for root, dirs, files in os.walk(skill_dir):
            # Sort for consistent ordering
            dirs.sort()
            files.sort()

            for filename in files:
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, skill_dir)

                # Skip __pycache__ and other unwanted directories
                if '__pycache__' in filepath or filepath.endswith('.pyc'):
                    continue

                zf.write(filepath, arcname)
                print(f"  + {arcname}")

    # Calculate package hash
    package_hash = calculate_file_hash(output_path)
    content_hash = calculate_dir_hash(skill_dir)

    # Create manifest
    manifest = {
        "package_version": "1.0",
        "created_at": datetime.now().isoformat(),
        "skill_name": skill_name,
        "skill_version": skill_version,
        "skill_id": meta.get('id'),
        "package_hash": package_hash,
        "content_hash": content_hash,
        "files_count": sum(1 for _ in Path(skill_dir).rglob('*') if _.is_file()),
    }

    manifest_path = output_path + '.manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Package created successfully!")
    print(f"   Package: {output_path}")
    print(f"   Size: {os.path.getsize(output_path):,} bytes")
    print(f"   Hash: {package_hash[:16]}...")
    print(f"   Manifest: {manifest_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Package Agent Migrator skill into distributable .skill file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python package_skill.py /path/to/agent-migrator
  python package_skill.py /path/to/agent-migrator --output /tmp/packages
  python package_skill.py .  # Package current directory
        """
    )
    parser.add_argument('skill_dir', nargs='?', default='.',
                        help="Path to skill directory (default: current directory)")
    parser.add_argument('--output', '-o', default='.',
                        help="Output directory for .skill package (default: current directory)")

    args = parser.parse_args()

    # Resolve paths
    skill_dir = os.path.abspath(args.skill_dir)
    output_dir = os.path.abspath(args.output)

    # Ensure output directory exists
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
