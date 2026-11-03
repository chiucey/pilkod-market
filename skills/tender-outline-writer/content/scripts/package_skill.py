#!/usr/bin/env python3
"""
package_skill.py - Skill packaging script for tender-outline-writer

Creates a distributable .skill archive containing:
- SKILL.md
- _meta.json
- scripts/ (if present)
- references/ (if present)
- assets/ (if present)

Excludes:
- Build artifacts
- __pycache__
- .DS_Store
- Other system files
"""

import json
import os
import sys
import tarfile
import tempfile
from pathlib import Path


# Files/directories to exclude from packaging
EXCLUDE_PATTERNS = {
    "__pycache__",
    ".DS_Store",
    "Thumbs.db",
    ".git",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "*.pyc",
    "*.pyo",
    "*.egg-info",
    "dist",
    "build",
}

# Files that must be present
REQUIRED_FILES = ["SKILL.md", "_meta.json"]


def should_exclude(path: Path, base_path: Path) -> bool:
    """Check if a path should be excluded from the package."""
    rel_path = path.relative_to(base_path)

    # Check exact matches
    if rel_path.name in EXCLUDE_PATTERNS:
        return True

    # Check patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*") and rel_path.name.endswith(pattern[1:]):
            return True

    return False


def validate_for_packaging(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill is ready for packaging."""
    errors = []

    # Check required files
    for req_file in REQUIRED_FILES:
        if not (skill_path / req_file).exists():
            errors.append(f"Required file missing: {req_file}")

    # Validate _meta.json
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            if "id" not in meta or "version" not in meta:
                errors.append("_meta.json missing required fields (id, version)")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid _meta.json: {e}")

    # Validate frontmatter in SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        lines = content.split("\n")

        if not lines or lines[0].strip() != "---":
            errors.append("SKILL.md must start with frontmatter (---)")

        # Check frontmatter has required fields
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            errors.append("SKILL.md missing closing --- for frontmatter")
        else:
            frontmatter_text = "\n".join(lines[1:frontmatter_end])
            has_name = any("name:" in line for line in frontmatter_text.split("\n"))
            has_desc = any("description:" in line for line in frontmatter_text.split("\n"))

            if not has_name:
                errors.append("SKILL.md frontmatter missing 'name' field")
            if not has_desc:
                errors.append("SKILL.md frontmatter missing 'description' field")

    return len(errors) == 0, errors


def collect_files(skill_path: Path) -> list[Path]:
    """Collect all files to include in the package."""
    files = []

    for item in skill_path.rglob("*"):
        if item.is_file() and not should_exclude(item, skill_path):
            files.append(item)

    return sorted(files)


def create_package(skill_path: str, output_dir: str = None) -> str:
    """Create a .skill package from the skill directory."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    # Validate
    is_valid, errors = validate_for_packaging(skill_path)
    if not is_valid:
        raise ValueError(f"Validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    # Determine output path
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get skill name and version
    meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
    skill_name = skill_path.name
    version = meta.get("version", "1.0.0")

    output_file = output_dir / f"{skill_name}_{version}.skill"

    # Create package
    files = collect_files(skill_path)

    print(f"\n{'='*60}")
    print(f"Packaging skill: {skill_name}")
    print(f"{'='*60}\n")
    print(f"Version: {version}")
    print(f"Output: {output_file}")
    print(f"\nIncluding {len(files)} file(s):")

    with tarfile.open(output_file, "w:gz") as tar:
        for file_path in files:
            arcname = file_path.relative_to(skill_path)
            print(f"  + {arcname}")
            tar.add(file_path, arcname=arcname)

    print(f"\n✅ Package created successfully!")
    print(f"{'='*60}\n")

    return str(output_file)


def extract_package(package_path: str, output_dir: str = None) -> str:
    """Extract a .skill package."""
    package_path = Path(package_path)

    if not package_path.exists():
        raise FileNotFoundError(f"Package not found: {package_path}")

    # Determine output directory
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = package_path.parent / package_path.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract
    with tarfile.open(package_path, "r:gz") as tar:
        tar.extractall(output_dir)

    print(f"\n✅ Package extracted to: {output_dir}")
    return str(output_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Package:   python package_skill.py <path_to_skill> [output_dir]")
        print("  Extract:   python package_skill.py --extract <package.skill> [output_dir]")
        sys.exit(1)

    if sys.argv[1] == "--extract":
        if len(sys.argv) < 3:
            print("Error: Package path required for extraction")
            sys.exit(1)
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        extract_package(sys.argv[2], output_dir)
    else:
        skill_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        create_package(skill_path, output_dir)
