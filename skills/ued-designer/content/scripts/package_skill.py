#!/usr/bin/env python3
"""
Skill Packaging Script

Packages a validated skill into a distributable .skill file.
Creates a clean archive with only necessary files.

Usage:
    python package_skill.py <path_to_skill> [--output <output_dir>]

Example:
    python package_skill.py ./ued-designer
    python package_skill.py ./ued-designer --output ./dist
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional


# Files and patterns to exclude from packaging
EXCLUDE_PATTERNS: Set[str] = {
    '__pycache__',
    '.pyc',
    '.pyo',
    '.git',
    '.gitignore',
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    '*.tmp',
    '.env',
    '.venv',
    'node_modules',
}

# Files that should always be excluded for security
SECURITY_EXCLUDE: Set[str] = {
    '.env',
    '.credentials',
    '*.key',
    '*.pem',
    'id_rsa',
    'secrets.json',
}


class PackagingError(Exception):
    """Custom exception for packaging errors."""
    pass


def should_exclude(file_path: Path, parent_relative: Path) -> bool:
    """Check if a file should be excluded from the package."""
    # Check absolute patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if file_path.name.endswith(pattern[1:]):
                return True
        elif pattern in file_path.name:
            return True

    # Check security-sensitive files
    for pattern in SECURITY_EXCLUDE:
        if pattern.startswith('*'):
            if file_path.name.endswith(pattern[1:]):
                return True
        elif pattern in file_path.name:
            return True

    # Check if file is a symlink (potential security issue)
    if file_path.is_symlink():
        return True

    return False


def get_package_files(skill_path: Path) -> List[Path]:
    """Get all files that should be included in the package."""
    package_files = []

    for item in skill_path.rglob('*'):
        if item.is_file():
            # Get path relative to skill directory
            relative_path = item.relative_to(skill_path)

            if should_exclude(item, relative_path):
                continue

            package_files.append(relative_path)

    return sorted(package_files)


def validate_before_packaging(skill_path: Path) -> bool:
    """Run quick validation before packaging."""
    print("📋 Running pre-packaging validation...")

    # Check essential files
    essential_files = ['SKILL.md', '_meta.json']
    for file_name in essential_files:
        if not (skill_path / file_name).exists():
            raise PackagingError(f"Missing essential file: {file_name}")

    # Validate _meta.json
    meta_path = skill_path / "_meta.json"
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta or 'version' not in meta:
            raise PackagingError("_meta.json missing required fields: id, version")
    except json.JSONDecodeError as e:
        raise PackagingError(f"Invalid _meta.json: {e}")

    # Validate SKILL.md frontmatter
    skill_md_path = skill_path / "SKILL.md"
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        raise PackagingError("SKILL.md must start with YAML frontmatter")

    print("✅ Pre-packaging validation passed")
    return True


def create_package(skill_path: Path, output_dir: Path) -> Path:
    """Create the skill package."""
    skill_name = skill_path.name
    meta_path = skill_path / "_meta.json"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    version = meta.get('version', '0.0.0')

    # Create output filename
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f"{skill_name}-{version}.skill"
    output_path = output_dir / output_filename

    # Get files to package
    package_files = get_package_files(skill_path)

    if not package_files:
        raise PackagingError("No files found to package")

    print(f"\n📦 Creating package: {output_filename}")
    print("-" * 40)

    # Create zip file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for relative_path in package_files:
            source_path = skill_path / relative_path
            # Use string paths for cross-platform compatibility
            zipf.write(str(source_path), str(relative_path))

            # Get compressed size
            info = zipf.getinfo(str(relative_path))
            size_kb = info.compress_size / 1024
            print(f"  + {relative_path} ({size_kb:.1f} KB)")

    # Get final file size
    final_size = output_path.stat().st_size / 1024
    print("-" * 40)
    print(f"✅ Package created successfully!")
    print(f"   Size: {final_size:.1f} KB")
    print(f"   Files: {len(package_files)}")
    print(f"   Path: {output_path}")

    return output_path


def create_digest(output_path: Path) -> Path:
    """Create a SHA256 digest file for the package."""
    import hashlib

    sha256_hash = hashlib.sha256()

    with open(output_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    digest_path = Path(str(output_path) + ".sha256")
    with open(digest_path, 'w') as f:
        f.write(sha256_hash.hexdigest())

    print(f"   Digest: {digest_path.name}")
    return digest_path


def package_skill(skill_path: str, output_dir: Optional[str] = None) -> List[Path]:
    """Main packaging function."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise PackagingError(f"Skill directory not found: {skill_path}")

    if not skill_path.is_dir():
        raise PackagingError(f"Path is not a directory: {skill_path}")

    print(f"\n🎯 Packaging skill: {skill_path.name}")
    print("=" * 60)

    # Create output directory if not specified
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent / "dist"

    output_path.mkdir(parents=True, exist_ok=True)

    # Validate before packaging
    validate_before_packaging(skill_path)

    # Create package
    package_path = create_package(skill_path, output_path)

    # Create digest
    digest_path = create_digest(package_path)

    print("=" * 60)
    print("\n📤 DELIVERY")
    print(f"   Package: {package_path}")
    print(f"   Digest: {digest_path}")

    return [package_path, digest_path]


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <path_to_skill> [--output <output_dir>]")
        print("\nExample:")
        print("  python package_skill.py ./ued-designer")
        print("  python package_skill.py ./ued-designer --output ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = None

    # Parse optional arguments
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    try:
        package_skill(skill_path, output_dir)
    except PackagingError as e:
        print(f"\n❌ Packaging failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
