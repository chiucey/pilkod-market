#!/usr/bin/env python3
"""
Package Skill Script for OpenClaw + RunningHub Connector

Creates a distributable .skill package containing:
- SKILL.md
- _meta.json
- scripts/
- references/
- assets/
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime


def read_skill_metadata(skill_dir: Path) -> dict:
    """Read skill metadata from _meta.json"""
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}


def read_skill_info(skill_dir: Path) -> tuple:
    """Read skill name and description from SKILL.md"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None, None

    content = skill_md.read_text(encoding="utf-8")

    # Parse frontmatter
    import re
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)

        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

        name = name_match.group(1).strip() if name_match else None
        desc = desc_match.group(1).strip() if desc_match else None

        return name, desc

    return None, None


def create_package(skill_dir: Path, output_path: Path) -> bool:
    """Create a .skill package from the skill directory"""

    # Validate skill directory
    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        return False

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print("Error: SKILL.md not found")
        return False

    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        print("Error: _meta.json not found")
        return False

    # Read metadata
    name, description = read_skill_info(skill_dir)
    metadata = read_skill_metadata(skill_dir)

    print(f"Packaging skill: {name or skill_dir.name}")
    print(f"Version: {metadata.get('version', '1.0.0')}")
    print(f"ID: {metadata.get('id', 'N/A')}")

    # Create package
    skill_name = name or skill_dir.name
    safe_name = skill_name.replace('/', '_').replace('\\', '_')

    if not str(output_path).endswith('.skill'):
        output_path = output_path / f"{safe_name}.skill"

    # Create temp directory for package contents
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Copy all files preserving structure
        skip_patterns = ['.git', '__pycache__', '*.pyc', '.DS_Store', 'node_modules']

        for item in skill_dir.rglob('*'):
            if item.is_file():
                # Check skip patterns
                skip = False
                for pattern in skip_patterns:
                    if pattern.startswith('*'):
                        if item.name.endswith(pattern[1:]):
                            skip = True
                            break
                    elif pattern in str(item):
                        skip = True
                        break

                if skip:
                    continue

                # Calculate relative path
                rel_path = item.relative_to(skill_dir)

                # Create destination
                dest = temp_path / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(item, dest)

        # Add manifest
        manifest = {
            "name": name,
            "description": description,
            "version": metadata.get('version', '1.0.0'),
            "id": metadata.get('id'),
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "files": []
        }

        # List all files in package
        for item in temp_path.rglob('*'):
            if item.is_file():
                manifest["files"].append(str(item.relative_to(temp_path)))

        manifest_path = temp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

        # Create tar.gz archive
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(temp_path, arcname=safe_name)

    print(f"\n✓ Package created: {output_path}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")
    print(f"  Files: {len(manifest['files'])}")

    return True


def extract_package(package_path: Path, output_dir: Path) -> bool:
    """Extract a .skill package"""
    if not package_path.exists():
        print(f"Error: Package not found: {package_path}")
        return False

    if not str(package_path).endswith('.skill'):
        print("Error: Invalid package format (must be .skill)")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(package_path, "r:gz") as tar:
            tar.extractall(output_dir)
        print(f"✓ Package extracted to: {output_dir}")
        return True
    except Exception as e:
        print(f"Error extracting package: {e}")
        return False


def list_package_contents(package_path: Path) -> bool:
    """List contents of a .skill package"""
    if not package_path.exists():
        print(f"Error: Package not found: {package_path}")
        return False

    try:
        with tarfile.open(package_path, "r:gz") as tar:
            members = tar.getmembers()
            print(f"Package: {package_path.name}")
            print(f"Contents ({len(members)} files):\n")

            for member in members:
                prefix = "[DIR] " if member.isdir() else "[FILE]"
                print(f"  {prefix} {member.name}")

            # Try to show manifest
            for member in members:
                if member.name.endswith('manifest.json'):
                    f = tar.extractfile(member)
                    if f:
                        manifest = json.loads(f.read().decode('utf-8'))
                        print(f"\nManifest:")
                        print(f"  Name: {manifest.get('name', 'N/A')}")
                        print(f"  Version: {manifest.get('version', 'N/A')}")
                        print(f"  ID: {manifest.get('id', 'N/A')}")
                        print(f"  Description: {manifest.get('description', 'N/A')[:80]}...")
        return True
    except Exception as e:
        print(f"Error reading package: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Package Manager for Skills")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Package command
    pkg_parser = subparsers.add_parser("package", help="Create a .skill package")
    pkg_parser.add_argument("path", help="Path to skill directory")
    pkg_parser.add_argument("-o", "--output", help="Output path (file or directory)")

    # Extract command
    ext_parser = subparsers.add_parser("extract", help="Extract a .skill package")
    ext_parser.add_argument("package", help="Path to .skill file")
    ext_parser.add_argument("-o", "--output", help="Output directory")

    # List command
    list_parser = subparsers.add_parser("list", help="List package contents")
    list_parser.add_argument("package", help="Path to .skill file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "package":
        skill_dir = Path(args.path)
        output_path = Path(args.output) if args.output else Path.cwd()
        success = create_package(skill_dir, output_path)

    elif args.command == "extract":
        package_path = Path(args.package)
        output_dir = Path(args.output) if args.output else Path.cwd()
        success = extract_package(package_path, output_dir)

    elif args.command == "list":
        package_path = Path(args.package)
        success = list_package_contents(package_path)

    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
