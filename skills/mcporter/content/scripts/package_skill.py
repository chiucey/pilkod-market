#!/usr/bin/env python3
"""
Skill Packaging Script - Create .skill distribution package
Packages a skill directory into a distributable .skill archive.
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_status(msg: str):
    """Print status message."""
    print(f"{CYAN}→{RESET} {msg}")


def print_success(msg: str):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {msg}")


def print_error(msg: str):
    """Print error message."""
    print(f"{RED}✗{RESET} {msg}")


def print_warning(msg: str):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {msg}")


def get_skill_metadata(skill_dir: Path) -> dict:
    """Extract skill metadata from SKILL.md and _meta.json."""
    skill_md = skill_dir / "SKILL.md"
    meta_json = skill_dir / "_meta.json"

    metadata = {
        "name": skill_dir.name,
        "id": None,
        "version": "1.0.0",
        "description": "",
        "validated": False
    }

    # Read frontmatter from SKILL.md
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        if content.startswith('---'):
            end_idx = content.index('---', 3)
            fm_text = content[3:end_idx]
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == 'name':
                        metadata['name'] = value
                    elif key == 'description':
                        metadata['description'] = value

    # Read _meta.json
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            metadata['id'] = meta.get('id')
            metadata['version'] = meta.get('version', '1.0.0')
        except json.JSONDecodeError:
            pass

    return metadata


def validate_before_pack(skill_dir: Path) -> bool:
    """Run basic validation before packaging."""
    errors = []

    # Check required files
    if not (skill_dir / "SKILL.md").exists():
        errors.append("Missing SKILL.md")
    if not (skill_dir / "_meta.json").exists():
        errors.append("Missing _meta.json")

    # Validate _meta.json
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("Missing 'id' in _meta.json")
            if 'version' not in meta:
                errors.append("Missing 'version' in _meta.json")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid _meta.json: {e}")

    # Check for secrets/unwanted files
    unwanted_files = [
        '.env', '*.env', 'secrets.json', 'credentials.json',
        '*.key', '*.pem', '*.log', '__pycache__'
    ]
    for pattern in unwanted_files:
        if list(skill_dir.rglob(pattern)):
            errors.append(f"Found unwanted file pattern: {pattern}")

    if errors:
        print_error("Validation failed:")
        for err in errors:
            print(f"  - {err}")
        return False

    return True


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package a skill directory into a .skill archive."""
    skill_dir = Path(skill_path).resolve()

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Packaging Skill: {skill_dir.name}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    if not skill_dir.exists():
        print_error(f"Skill directory not found: {skill_dir}")
        return None

    if not skill_dir.is_dir():
        print_error(f"Not a directory: {skill_dir}")
        return None

    # Validate
    print_status("Running pre-packaging validation...")
    if not validate_before_pack(skill_dir):
        return None
    print_success("Validation passed")

    # Get metadata
    metadata = get_skill_metadata(skill_dir)
    print_status(f"Skill: {metadata['name']}")
    print_status(f"Version: {metadata['version']}")
    if metadata['id']:
        print_status(f"ID: {metadata['id']}")

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_dir.parent

    output_path.mkdir(parents=True, exist_ok=True)

    # Create .skill filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    skill_file = output_path / f"{metadata['name']}.skill"

    # If file exists, add timestamp
    if skill_file.exists():
        skill_file = output_path / f"{metadata['name']}_{timestamp}.skill"

    print_status(f"Creating package: {skill_file.name}")

    # Create the .skill archive (ZIP format)
    try:
        with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add manifest
            manifest = {
                "name": metadata['name'],
                "version": metadata['version'],
                "created_at": datetime.now().isoformat(),
                "files": []
            }

            # Walk through skill directory
            for root, dirs, files in os.walk(skill_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    # Skip hidden files
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(skill_dir)

                    # Security check: no absolute paths or path traversal
                    if '..' in str(arcname):
                        print_warning(f"Skipping suspicious path: {arcname}")
                        continue

                    zf.write(file_path, arcname)
                    manifest["files"].append(str(arcname))

            # Add manifest to archive
            manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
            zf.writestr("manifest.json", manifest_json)

        # Get file size
        size = skill_file.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        print_success(f"Package created: {skill_file}")
        print_success(f"Size: {size_str}")
        print_success(f"Files included: {len(manifest['files'])}")

        return str(skill_file)

    except Exception as e:
        print_error(f"Failed to create package: {e}")
        if skill_file.exists():
            skill_file.unlink()
        return None


def list_package_contents(skill_file: str):
    """List contents of a .skill package."""
    skill_path = Path(skill_file)

    if not skill_path.exists():
        print_error(f"File not found: {skill_path}")
        return

    print(f"\n{BOLD}Contents of {skill_path.name}:{RESET}\n")

    try:
        with zipfile.ZipFile(skill_path, 'r') as zf:
            for info in zf.infolist():
                size = info.file_size
                if size < 1024:
                    size_str = f"{size:>6} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:>6.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):>6.1f} MB"
                print(f"  {size_str}  {info.filename}")

            print(f"\n  Total: {len(zf.namelist())} files")

    except zipfile.BadZipFile:
        print_error("Invalid .skill file (not a valid ZIP archive)")
    except Exception as e:
        print_error(f"Error reading package: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage:")
        print(f"  Package: python {sys.argv[0]} <skill_directory> [output_dir]")
        print(f"  List:   python {sys.argv[0]} --list <package.skill>")
        sys.exit(1)

    if sys.argv[1] == "--list":
        if len(sys.argv) < 3:
            print(f"Usage: python {sys.argv[0]} --list <package.skill>")
            sys.exit(1)
        list_package_contents(sys.argv[2])
    else:
        skill_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        result = package_skill(skill_path, output_dir)
        sys.exit(0 if result else 1)
