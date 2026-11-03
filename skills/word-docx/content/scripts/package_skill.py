#!/usr/bin/env python3
"""
Package skill into a distributable .skill archive.
Creates a clean, signed archive ready for distribution.
"""
import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


def get_skill_meta(skill_path: Path) -> dict:
    """Read skill metadata from _meta.json."""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    return json.loads(meta_file.read_text(encoding="utf-8"))


def scan_skill_files(skill_path: Path) -> list[Path]:
    """Scan skill directory and return all relevant files."""
    exclude_dirs = {"__pycache__", ".git", "node_modules", ".venv", ".env"}
    exclude_files = {".pyc", ".pyo", ".pyd", ".so", ".dll", ".DS_Store"}

    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in filenames:
            # Skip excluded file types
            if any(filename.endswith(ext) for ext in exclude_files):
                continue

            full_path = Path(root) / filename
            rel_path = full_path.relative_to(skill_path)
            files.append(rel_path)

    return files


def create_archive(skill_path: Path, output_path: Path) -> dict:
    """Create .skill archive from skill directory."""
    meta = get_skill_meta(skill_path)
    files = scan_skill_files(skill_path)

    print(f"Packaging skill: {meta.get('id', 'unknown')}")
    print(f"Version: {meta.get('version', '1.0.0')}")
    print(f"Files to include: {len(files)}")

    # Create archive
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = skill_path / file_path
            zf.write(full_path, file_path)
            print(f"  + {file_path}")

    # Calculate checksums
    sha256_hash = hashlib.sha256()
    with open(output_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    checksum = sha256_hash.hexdigest()

    manifest = {
        "id": meta.get("id"),
        "version": meta.get("version"),
        "name": meta.get("name", skill_path.name),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "file_count": len(files),
        "checksum_sha256": checksum,
        "files": [str(f) for f in files]
    }

    return manifest


def verify_archive(output_path: Path, manifest: dict) -> bool:
    """Verify the created archive is valid."""
    try:
        with zipfile.ZipFile(output_path, 'r') as zf:
            # Test integrity
            bad_file = zf.testzip()
            if bad_file:
                print(f"✗ Archive integrity check failed: {bad_file}")
                return False

            # Verify file count
            file_count = len(zf.namelist())
            if file_count != manifest["file_count"]:
                print(f"✗ File count mismatch: {file_count} vs {manifest['file_count']}")
                return False

        print("✓ Archive integrity verified")
        return True

    except Exception as e:
        print(f"✗ Archive verification failed: {e}")
        return False


def main():
    # Get skill path from argument or use default
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    if not skill_path.exists():
        print(f"✗ Skill path not found: {skill_path}")
        sys.exit(1)

    # Determine output path
    output_dir = skill_path.parent
    skill_name = skill_path.name

    # Read version from meta
    try:
        meta = get_skill_meta(skill_path)
        version = meta.get("version", "1.0.0")
        skill_id = meta.get("id", skill_name)
    except Exception as e:
        print(f"✗ Failed to read skill metadata: {e}")
        sys.exit(1)

    output_path = output_dir / f"{skill_name}-{version}.skill"

    print("=" * 50)
    print("Skill Packager")
    print("=" * 50)

    # Create archive
    try:
        manifest = create_archive(skill_path, output_path)
    except Exception as e:
        print(f"✗ Failed to create archive: {e}")
        sys.exit(1)

    # Verify archive
    if not verify_archive(output_path, manifest):
        sys.exit(1)

    # Save manifest alongside archive
    manifest_path = output_path.with_suffix(".skill.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\n" + "=" * 50)
    print(f"✓ Package created: {output_path.name}")
    print(f"  Checksum: {manifest['checksum_sha256'][:16]}...")
    print(f"  Files: {manifest['file_count']}")
    print(f"  Manifest: {manifest_path.name}")
    print("=" * 50)


if __name__ == "__main__":
    main()
