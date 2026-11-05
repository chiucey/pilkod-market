#!/usr/bin/env python3
"""
Package Skill Script
Packages the stock-sector-research skill for distribution
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent / "dist"

def validate_skill_structure():
    """Validate skill directory structure"""
    errors = []
    warnings = []

    # Check required files
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        path = SKILL_DIR / f
        if not path.exists():
            errors.append(f"Missing required file: {f}")

    # Check _meta.json
    meta_path = SKILL_DIR / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Check SKILL.md frontmatter
    skill_path = SKILL_DIR / "SKILL.md"
    if skill_path.exists():
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        # Check frontmatter fields
        if 'name:' not in content:
            errors.append("SKILL.md frontmatter missing 'name' field")
        if 'description:' not in content:
            errors.append("SKILL.md frontmatter missing 'description' field")

    # Check optional directories
    optional_dirs = ["scripts", "references", "assets"]
    for d in optional_dirs:
        if (SKILL_DIR / d).exists():
            print(f"  ✓ Found optional directory: {d}")

    return errors, warnings

def validate_file_paths():
    """Validate all file paths are English only"""
    errors = []

    for root, dirs, files in os.walk(SKILL_DIR):
        # Check directory names
        for d in dirs:
            if not is_english_only(d):
                errors.append(f"Non-English directory name: {d}")

        # Check file names
        for f in files:
            if not is_english_only(f):
                errors.append(f"Non-English file name: {f}")

    return errors

def is_english_only(s):
    """Check if string contains only English characters"""
    return all(ord(c) < 128 for c in s)

def create_package():
    """Create skill package"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"stock-sector-research_v2.0.0_{timestamp}.skill"

    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # Skip dist directory
            if 'dist' in root:
                continue

            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(SKILL_DIR)
                zf.write(file_path, arc_name)

    print(f"\n✓ Package created: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")

    return output_file

def main():
    print("=" * 60)
    print("Stock Sector Research Skill - Package Builder")
    print("=" * 60)

    print("\n[1/4] Validating skill structure...")
    errors, warnings = validate_skill_structure()

    if errors:
        print("\n✗ Validation errors:")
        for e in errors:
            print(f"  - {e}")
        return

    if warnings:
        print("\n⚠ Warnings:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("  ✓ Structure validation passed")

    print("\n[2/4] Validating file paths...")
    path_errors = validate_file_paths()

    if path_errors:
        print("\n✗ Path validation errors:")
        for e in path_errors:
            print(f"  - {e}")
        return

    print("  ✓ All paths are English-only")

    print("\n[3/4] Generating package contents...")
    print("  Files to include:")

    for root, dirs, files in os.walk(SKILL_DIR):
        if 'dist' in root:
            continue
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(SKILL_DIR)
            print(f"    + {rel_path}")

    print("\n[4/4] Creating package...")
    output_file = create_package()

    print("\n" + "=" * 60)
    print("Package build completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
