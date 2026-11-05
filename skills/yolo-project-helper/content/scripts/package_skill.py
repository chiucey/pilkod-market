#!/usr/bin/env python3
"""
Package YOLO Project Helper Skill for distribution
Creates a .skill archive file
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    if status == "success":
        print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {message}")
    elif status == "error":
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {message}")
    else:
        print(f"[INFO] {message}")

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def should_include(path, relative_to):
    """Check if file should be included in package"""
    # Exclude patterns
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.git',
        '.gitignore',
        'node_modules',
        '.DS_Store',
        'Thumbs.db',
        '*.egg-info',
        '.pytest_cache',
        '.vscode',
        '.idea'
    ]

    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str or path_str.endswith(pattern):
            return False
    return True

def create_skill_package(skill_path, output_dir):
    """Create a .skill package file"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_path.name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_name}_{timestamp}.skill"
    package_path = output_dir / package_name

    print_status(f"Creating skill package: {package_name}")

    manifest = {
        "name": skill_name,
        "created_at": datetime.now().isoformat(),
        "files": []
    }

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if should_include(Path(root) / d, skill_path)]

            for file in files:
                file_path = Path(root) / file
                if not should_include(file_path, skill_path):
                    continue

                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

                # Calculate checksum for non-hidden files
                if not file.startswith('.'):
                    checksum = calculate_checksum(file_path)
                    manifest["files"].append({
                        "path": str(arcname),
                        "checksum": checksum,
                        "size": file_path.stat().st_size
                    })

    # Save manifest
    manifest_path = package_path.with_suffix('.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print_status(f"Package created: {package_path}")
    print_status(f"Manifest saved: {manifest_path}")
    print_status(f"Package size: {package_path.stat().st_size / 1024:.2f} KB")

    return package_path

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    if not skill_path.exists():
        print_status(f"Skill path does not exist: {skill_path}", "error")
        sys.exit(1)

    # Validate skill structure before packaging
    meta_path = skill_path / "_meta.json"
    skill_md = skill_path / "SKILL.md"

    if not meta_path.exists():
        print_status("_meta.json not found", "error")
        sys.exit(1)

    if not skill_md.exists():
        print_status("SKILL.md not found", "error")
        sys.exit(1)

    # Read and validate meta
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        print_status(f"Skill: {meta.get('name', 'unknown')} v{meta.get('version', '1.0.0')}")
    except Exception as e:
        print_status(f"Failed to read _meta.json: {e}", "error")
        sys.exit(1)

    try:
        package_path = create_skill_package(skill_path, output_dir)
        print_status("Package created successfully!", "success")
        print(f"\n{Colors.BOLD}Output:{Colors.RESET} {package_path}")
    except Exception as e:
        print_status(f"Failed to create package: {e}", "error")
        sys.exit(1)

if __name__ == "__main__":
    main()
