#!/usr/bin/env python3
"""
Package Skill Script for video-editing-skills
Creates a distributable .skill archive file.
"""

import os
import sys
import zipfile
import json
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")


def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")


def get_exclusions() -> set:
    """Return file patterns to exclude from packaging."""
    return {
        '__pycache__',
        '.pyc',
        '.DS_Store',
        '.git',
        '.gitignore',
        '*.log',
        'tmp',
        '.tmp',
        'node_modules',
        'test_output',
        'dist',
        'build',
    }


def should_exclude(path: Path) -> bool:
    """Check if a file/directory should be excluded."""
    exclusions = get_exclusions()

    if path.name in exclusions:
        return True

    for excl in exclusions:
        if excl.startswith('*.') and path.name.endswith(excl[1:]):
            return True

    return False


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package the skill into a .skill file."""
    skill_dir = Path(skill_path)

    if not skill_dir.exists():
        print_error(f"Skill directory not found: {skill_path}")
        sys.exit(1)

    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_dir.parent

    output_path.mkdir(parents=True, exist_ok=True)

    # Read metadata
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        skill_name = meta.get('name', skill_dir.name)
        skill_version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_dir.name
        skill_version = '1.0.0'

    output_file = output_path / f"{skill_name}.skill"

    print(f"\n{Colors.BOLD}Packaging skill: {skill_dir.name}{Colors.END}\n")

    files_included = []
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if not should_exclude(Path(d))]

            for file in files:
                file_path = Path(root) / file

                if should_exclude(file_path):
                    continue

                arcname = file_path.relative_to(skill_dir)

                try:
                    if file.endswith(('.md', '.json', '.txt', '.yaml', '.yml')):
                        file_path.read_text(encoding='utf-8')
                except Exception as e:
                    print_warning(f"Skipping file {arcname}: {e}")
                    continue

                zf.write(file_path, arcname)
                files_included.append(str(arcname))

    print_success(f"Created: {output_file}")
    print_info(f"Total files: {len(files_included)}")

    for f in sorted(files_included):
        print(f"  - {f}")

    # Verify archive
    print(f"\n{Colors.BOLD}Verifying archive...{Colors.END}")
    try:
        with zipfile.ZipFile(output_file, 'r') as zf:
            bad_file = zf.testzip()
            if bad_file:
                print_error(f"Corrupt file in archive: {bad_file}")
                sys.exit(1)
            print_success("Archive integrity verified")

        size_kb = output_file.stat().st_size / 1024
        print_info(f"Archive size: {size_kb:.2f} KB")

    except Exception as e:
        print_error(f"Verification failed: {e}")
        sys.exit(1)

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/video-editing-skills"
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    output_file = package_skill(skill_path, output_dir)

    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Packaging complete!{Colors.END}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
