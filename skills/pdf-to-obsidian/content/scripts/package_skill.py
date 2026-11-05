#!/usr/bin/env python3
"""
Skill Packager
Creates .skill package from skill directory
"""

import os
import sys
import zipfile
import tempfile
from pathlib import Path
import shutil
from datetime import datetime

def sanitize_path(path: Path, base_path: Path) -> bool:
    """Check if path is safe (no symlink escape)"""
    try:
        resolved = path.resolve()
        base_resolved = base_path.resolve()
        return str(resolved).startswith(str(base_resolved))
    except:
        return False

def create_skill_package(skill_path: str, output_dir: str = None) -> str:
    """Create .skill package from skill directory"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise ValueError(f"Skill path does not exist: {skill_path}")

    # Create output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent

    output_path.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    skill_name = skill_path.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"{skill_name}.skill"

    # Create zip package
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Security check
                if not sanitize_path(file_path, skill_path):
                    print(f"Warning: Skipping unsafe path: {file_path}")
                    continue

                # Calculate archive name (relative path)
                arcname = file_path.relative_to(skill_path)

                # Add file to archive
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ Package created: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")

    return str(output_file)

def verify_package(package_path: str) -> bool:
    """Verify the created package"""
    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            # Check for essential files
            files = zf.namelist()
            required = ['SKILL.md', '_meta.json']

            for req in required:
                if req not in files:
                    print(f"Warning: Missing required file in package: {req}")
                    return False

            print("\n✓ Package verification passed")
            print(f"  Total files: {len(files)}")
            return True
    except zipfile.BadZipFile:
        print("Error: Invalid zip file")
        return False
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        print("\nExample:")
        print("  python package_skill.py /workspace/temp-skills/pdf-to-obsidian")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 50)
    print("Skill Packager")
    print("=" * 50)

    try:
        package_path = create_skill_package(skill_path, output_dir)
        verify_package(package_path)
        print("\n" + "=" * 50)
        print("Package ready for distribution!")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
