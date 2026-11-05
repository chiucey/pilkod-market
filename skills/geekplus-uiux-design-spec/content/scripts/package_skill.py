#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a zip archive of the skill directory.
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_skill_info(skill_dir: str) -> tuple[str, str]:
    """Extract skill name and version from files."""
    meta_path = os.path.join(skill_dir, '_meta.json')
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')

    name = None
    version = None

    # Get from _meta.json
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            name = meta.get('name')
            version = meta.get('version')

    # Fallback to folder name
    if not name:
        name = os.path.basename(skill_dir)

    if not version:
        version = "1.0.0"

    return name, version


def scan_for_secrets(skill_dir: str) -> list[str]:
    """Scan for potential secrets or sensitive data."""
    warnings = []
    secret_patterns = [
        'password', 'secret', 'token', 'api_key', 'apikey',
        'private_key', 'credential', 'auth'
    ]

    for root, dirs, files in os.walk(skill_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for f in files:
            if f.startswith('.'):
                continue

            file_path = os.path.join(root, f)

            # Check for potentially sensitive file names
            f_lower = f.lower()
            for pattern in secret_patterns:
                if pattern in f_lower:
                    warnings.append(f"Potentially sensitive file: {file_path}")

            # Check file content for secrets
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read(5000)  # Read first 5KB
                    content_lower = content.lower()
                    for pattern in secret_patterns:
                        if f'"{pattern}"' in content_lower or f"'{pattern}'" in content_lower:
                            warnings.append(f"Potential secret in {file_path}")
                            break
            except:
                pass  # Skip binary files

    return warnings


def create_package(skill_dir: str, output_dir: str = None) -> str:
    """Create a .skill package file."""
    skill_dir = os.path.abspath(skill_dir)
    skill_name, version = get_skill_info(skill_dir)

    # Sanitize name for filename
    safe_name = skill_name.replace(' ', '-').lower()

    # Determine output directory
    if output_dir:
        output_dir = os.path.abspath(output_dir)
    else:
        # Default to skill directory's parent
        output_dir = os.path.dirname(skill_dir)

    os.makedirs(output_dir, exist_ok=True)

    # Create output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"{safe_name}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # Check for secrets
    warnings = scan_for_secrets(skill_dir)
    if warnings:
        print("⚠️  Security warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    # Create the zip file
    print(f"Creating package: {output_path}")
    print(f"  Skill: {skill_name}")
    print(f"  Version: {version}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")

    # Get file size
    size = os.path.getsize(output_path)
    print(f"\n✓ Package created: {output_path}")
    print(f"  Size: {size:,} bytes")

    return output_path


def list_package_contents(package_path: str):
    """List contents of a .skill package."""
    with zipfile.ZipFile(package_path, 'r') as zipf:
        print(f"\nPackage contents:")
        for info in zipf.infolist():
            print(f"  {info.filename} ({info.file_size:,} bytes)")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: package_skill.py <skill_directory> [output_directory]")
        print("\nExample:")
        print("  package_skill.py /path/to/my-skill")
        print("  package_skill.py /path/to/my-skill /output/dir")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_dir):
        print(f"Error: Skill directory not found: {skill_dir}")
        sys.exit(1)

    # Run validation first
    import subprocess
    validate_script = os.path.join(os.path.dirname(__file__), 'quick_validate.py')
    if os.path.exists(validate_script):
        print("Running validation...")
        result = subprocess.run([sys.executable, validate_script, skill_dir])
        if result.returncode != 0:
            print("\n⚠️  Validation failed. Package anyway? (y/N)")
            if input().lower() != 'y':
                sys.exit(1)
        print()

    # Create package
    output_path = create_package(skill_dir, output_dir)

    # List contents
    list_package_contents(output_path)

    print("\n" + "=" * 50)
    print("Package ready for distribution!")
    print(f"Path: {output_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
