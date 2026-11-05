#!/usr/bin/env python3
"""
DCF Valuation Skill Packager
Packages the skill into a distributable .skill archive.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"{BOLD}→ {msg}{RESET}")


def print_step(msg):
    print(f"\n{BOLD}━━━ {msg} ━━━{RESET}")


def validate_before_packaging(skill_path):
    """Run validation before packaging."""
    print_step("Pre-Packaging Validation")

    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    missing = []

    for f in required_files:
        if not (Path(skill_path) / f).exists():
            missing.append(f)

    if missing:
        print_error(f"Missing required files: {', '.join(missing)}")
        return False

    # Check meta.json
    with open(Path(skill_path) / "_meta.json", 'r') as f:
        meta = json.load(f)

    if 'id' not in meta or 'version' not in meta:
        print_error("_meta.json missing required fields")
        return False

    print_success("Pre-packaging validation passed")
    return True


def create_package(skill_path, output_dir=None):
    """Create the .skill package."""
    print_step("Creating Package")

    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # Read meta
    with open(skill_path / "_meta.json", 'r') as f:
        meta = json.load(f)

    skill_id = meta['id']
    version = meta['version']

    # Output file
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Package filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_name}_{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    print_info(f"Package name: {package_name}")
    print_info(f"Output path: {package_path}")

    # Create zip archive
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__ and hidden files
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path.parent)

                # Skip the package itself
                if str(arcname).endswith('.skill'):
                    continue

                zipf.write(file_path, arcname)
                print_info(f"  Added: {arcname}")

    # Get file size
    size_kb = package_path.stat().st_size / 1024

    print_success(f"Package created: {package_path.name}")
    print_info(f"Size: {size_kb:.1f} KB")

    # Generate manifest
    manifest = {
        "skill_id": skill_id,
        "skill_name": skill_name,
        "version": version,
        "package_path": str(package_path),
        "created_at": datetime.now().isoformat(),
        "file_size_kb": round(size_kb, 1)
    }

    manifest_path = output_dir / f"{skill_name}_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print_success(f"Manifest created: {manifest_path.name}")

    return package_path


def verify_package(package_path):
    """Verify the created package."""
    print_step("Verifying Package")

    try:
        with zipfile.ZipFile(package_path, 'r') as zipf:
            files = zipf.namelist()

            required = ['wu-shifu-dcf-valuation/SKILL.md', 'wu-shifu-dcf-valuation/_meta.json']
            missing = [f for f in required if f not in files]

            if missing:
                print_error(f"Missing required files in package: {', '.join(missing)}")
                return False

            print_success(f"Package contains {len(files)} files")

            # List contents
            for f in sorted(files):
                print_info(f"  - {f}")

            return True

    except zipfile.BadZipFile:
        print_error("Invalid zip file")
        return False


def package_skill(skill_path, output_dir=None):
    """Main packaging function."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}DCF Valuation Skill Packager{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    print_step("Starting Package Process")

    # Validate
    if not validate_before_packaging(skill_path):
        print_error("Validation failed, aborting packaging")
        return None

    # Create package
    package_path = create_package(skill_path, output_dir)

    if not package_path:
        print_error("Packaging failed")
        return None

    # Verify
    if not verify_package(package_path):
        print_error("Package verification failed")
        return None

    print_step("Packaging Complete")

    print(f"\n{GREEN}{BOLD}✓ Skill packaged successfully!{RESET}")
    print(f"\nPackage location: {package_path}")

    return package_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/wu-shifu-dcf-valuation"
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)
