#!/usr/bin/env python3
"""
Package Skill Script for administrative-review-evidence
Creates a distributable .skill package from the skill directory.
"""

import os
import sys
import json
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path

def read_file(path: str) -> str:
    """Read file content safely."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def calculate_checksum(directory: str) -> str:
    """Calculate SHA256 checksum of all files in directory."""
    hash_md5 = hashlib.sha256()
    for root, dirs, files in os.walk(directory):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                hash_md5.update(f.read())
    return hash_md5.hexdigest()

def validate_skill(directory: str) -> tuple[bool, list[str]]:
    """Validate skill structure and content."""
    errors = []

    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(directory, file)
        if not os.path.exists(file_path):
            errors.append(f"Missing required file: {file}")

    # Validate SKILL.md frontmatter
    skill_md = os.path.join(directory, 'SKILL.md')
    if os.path.exists(skill_md):
        content = read_file(skill_md)
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter")
        if 'name:' not in content[:200]:
            errors.append("SKILL.md missing 'name' in frontmatter")
        if 'description:' not in content[:500]:
            errors.append("SKILL.md missing 'description' in frontmatter")

    # Validate _meta.json
    meta_json = os.path.join(directory, '_meta.json')
    if os.path.exists(meta_json):
        try:
            meta = json.loads(read_file(meta_json))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    return len(errors) == 0, errors

def package_skill(directory: str, output_dir: str = None):
    """Package the skill into a .skill file."""
    directory = os.path.abspath(directory)

    # Validate first
    valid, errors = validate_skill(directory)
    if not valid:
        print("❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("✅ Validation passed")

    # Read metadata
    meta = json.loads(read_file(os.path.join(directory, '_meta.json')))
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # Create output filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    if output_dir is None:
        output_dir = os.path.dirname(directory) or '.'
    output_file = os.path.join(output_dir, f"{skill_id}_{version}_{timestamp}.skill")

    # Create the .skill package (ZIP format)
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(directory):
            # Skip empty directories and assets if empty
            if root == directory:
                dirs[:] = [d for d in dirs if os.path.join(directory, d) != os.path.join(directory, 'assets') or os.listdir(os.path.join(directory, 'assets'))]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    # Calculate checksum
    checksum = calculate_checksum(directory)

    # Create manifest
    manifest = {
        "skill_id": skill_id,
        "version": version,
        "packaged_at": datetime.now().isoformat(),
        "checksum": checksum,
        "files": []
    }

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, directory)
            manifest["files"].append(arcname)

    # Save manifest alongside package
    manifest_file = output_file + '.manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n📦 Skill packaged successfully: {output_file}")
    print(f"📋 Manifest saved: {manifest_file}")
    print(f"🔐 Checksum: {checksum[:16]}...")

    return output_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📂 Packaging skill from: {skill_dir}\n")
    package_skill(skill_dir, output_dir)