#!/usr/bin/env python3
"""
Package Skill Script for Multi-Agent Trading Analyst
Creates distributable .skill archive with proper structure.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_manifest(skill_dir: Path) -> dict:
    """Create package manifest from skill metadata."""
    meta_path = skill_dir / '_meta.json'
    skill_md = skill_dir / 'SKILL.md'

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # Extract name and description from SKILL.md
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)

    manifest = {
        'skill_id': meta.get('id'),
        'name': name_match.group(1).strip() if name_match else skill_dir.name,
        'description': desc_match.group(1).strip() if desc_match else '',
        'version': meta.get('version', '1.0.0'),
        'created_at': datetime.now().isoformat(),
        'files': [],
        'structure': {}
    }

    # Build file list and structure
    for item in sorted(skill_dir.rglob('*')):
        if item.is_file():
            rel_path = item.relative_to(skill_dir)
            manifest['files'].append(str(rel_path))
            manifest['structure'][str(rel_path)] = {
                'size': item.stat().st_size,
                'type': get_file_type(item)
            }

    return manifest


def get_file_type(path: Path) -> str:
    """Determine file type for manifest."""
    suffix = path.suffix.lower()
    type_map = {
        '.md': 'documentation',
        '.py': 'script',
        '.json': 'metadata',
        '.yaml': 'configuration',
        '.yml': 'configuration'
    }
    return type_map.get(suffix, 'other')


def validate_package_contents(skill_dir: Path, manifest: dict) -> tuple[bool, list]:
    """Validate package contents meet requirements."""
    errors = []

    # Check required files
    required = ['SKILL.md', '_meta.json']
    for req in required:
        if not (skill_dir / req).exists():
            errors.append(f"Missing required file: {req}")

    # Check for non-ASCII in file names
    for f in manifest['files']:
        if not all(ord(c) < 128 for c in f):
            errors.append(f"Non-ASCII characters in file path: {f}")

    # Check for secrets patterns (basic check)
    forbidden_patterns = ['password', 'secret', 'api_key', 'token', 'credential']
    for f in manifest['files']:
        if any(pattern in f.lower() for pattern in forbidden_patterns):
            errors.append(f"Potentially sensitive file: {f}")

    return len(errors) == 0, errors


def create_archive(skill_dir: Path, output_dir: Path, manifest: dict) -> Path:
    """Create .skill archive file."""
    skill_name = skill_dir.name
    version = manifest['version']
    archive_name = f"{skill_name}-{version}.skill"
    archive_path = output_dir / archive_name

    # Create zip archive
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add manifest
        manifest_content = json.dumps(manifest, indent=2, ensure_ascii=False)
        zf.writestr('manifest.json', manifest_content)

        # Add all skill files
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(skill_dir)
                zf.write(file_path, rel_path)

    return archive_path


def main():
    """Main packaging entry point."""
    # Determine skill directory
    if len(sys.argv) > 1:
        skill_dir = Path(sys.argv[1]).resolve()
    else:
        script_dir = Path(__file__).resolve().parent
        skill_dir = script_dir.parent

    print(f"Packaging skill: {skill_dir.name}")
    print("-" * 50)

    # Create manifest
    print("Creating manifest...")
    manifest = create_manifest(skill_dir)

    # Validate contents
    print("Validating package contents...")
    valid, errors = validate_package_contents(skill_dir, manifest)
    if not valid:
        print("✗ Validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"✓ Found {len(manifest['files'])} files")

    # Create output directory
    output_dir = skill_dir / 'dist'
    output_dir.mkdir(exist_ok=True)

    # Create archive
    print("Creating archive...")
    archive_path = create_archive(skill_dir, output_dir, manifest)

    print("-" * 50)
    print(f"✓ Package created: {archive_path}")
    print(f"  Size: {archive_path.stat().st_size / 1024:.1f} KB")
    print(f"  Files: {len(manifest['files'])}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
