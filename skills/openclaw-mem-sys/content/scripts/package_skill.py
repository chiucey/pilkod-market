#!/usr/bin/env python3
"""
OpenClaw Memory System - Skill Packaging Script
Packages skill into a .skill file for distribution
"""
import os
import json
import shutil
import zipfile
import hashlib
import sys
from pathlib import Path
from datetime import datetime

def get_file_hashes(folder: Path) -> dict:
    """Calculate SHA256 hashes for all files"""
    hashes = {}
    for item in folder.rglob("*"):
        if item.is_file():
            rel_path = str(item.relative_to(folder))
            sha256 = hashlib.sha256()
            sha256.update(item.read_bytes())
            hashes[rel_path] = sha256.hexdigest()
    return hashes

def should_include(path: Path, filename: str) -> bool:
    """Check if file should be included in package"""
    exclude_patterns = [
        "__pycache__", ".git", ".DS_Store", "*.pyc",
        "node_modules", ".env", "*.log", "*.bak",
        ".pytest_cache", ".coverage"
    ]
    name = filename.lower()
    for pattern in exclude_patterns:
        if pattern.startswith("*."):
            if name.endswith(pattern[1:]):
                return False
        elif pattern in path.parts:
            return False
    return True

def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """Package skill into .skill file"""
    if output_dir is None:
        output_dir = Path("/workspace/temp-skills")

    # Read meta
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))

    skill_name = meta.get("name", skill_path.name)
    version = meta.get("version", "1.0.0")
    skill_id = meta.get("id", "unknown")

    # Create package filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_name}_v{version}_{skill_id}.skill"
    output_path = output_dir / package_name

    # Collect files
    files_to_package = []
    for item in skill_path.rglob("*"):
        if item.is_file():
            rel_path = str(item.relative_to(skill_path))
            if should_include(item, item.name):
                files_to_package.append((item, rel_path))

    # Create .skill file (ZIP format)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for abs_path, rel_path in files_to_package:
            zf.write(abs_path, arcname=rel_path)

        # Add manifest
        manifest = {
            "name": skill_name,
            "version": version,
            "id": skill_id,
            "packaged_at": datetime.now().isoformat(),
            "files": [rel for _, rel in files_to_package],
            "file_count": len(files_to_package)
        }
        zf.writestr("MANIFEST.json", json.dumps(manifest, indent=2))

    # Calculate checksums
    sha256 = hashlib.sha256()
    sha256.update(output_path.read_bytes())
    checksum = sha256.hexdigest()

    print(f"\n[\u2705] Skill packaged successfully!")
    print(f"   Name: {skill_name}")
    print(f"   Version: {version}")
    print(f"   ID: {skill_id}")
    print(f"   Files: {len(files_to_package)}")
    print(f"   Package: {output_path}")
    print(f"   SHA256: {checksum[:16]}...")

    return output_path

def main():
    skill_path = Path(__file__).parent.parent

    print(f"[\u2705] Packaging skill: {skill_path.name}")

    try:
        output_path = package_skill(skill_path)
        print(f"\n[\u2705] Package created: {output_path}")
        return 0
    except Exception as e:
        print(f"\n[\u274c] Packaging failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
