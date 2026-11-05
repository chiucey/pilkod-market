#!/usr/bin/env python3
"""
Package GARP Stock Picker skill into a distributable .skill file.
"""
import os
import json
import zipfile
import shutil
from datetime import datetime

SKILL_DIR = "/workspace/temp-skills/garp-stock-picker"
OUTPUT_DIR = "/workspace/temp-skills"
SKILL_NAME = "garp-stock-picker"

def validate_skill():
    """Validate skill structure before packaging."""
    errors = []

    # Check SKILL.md exists
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
    else:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check frontmatter
            if not content.startswith('---'):
                errors.append("SKILL.md must start with frontmatter (---)")
            if 'name: garp-stock-picker' not in content:
                errors.append("frontmatter 'name' field missing or incorrect")
            if 'description:' not in content:
                errors.append("frontmatter 'description' field missing")

    # Check _meta.json
    meta_json = os.path.join(SKILL_DIR, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("_meta.json not found")
    else:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")

    return errors

def package_skill():
    """Package the skill into a .skill file."""
    print("Validating skill structure...")
    errors = validate_skill()

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("Validation passed. Packaging...")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create .skill package (zip format)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"{SKILL_NAME}.skill")

    # Remove existing if present
    if os.path.exists(output_file):
        os.remove(output_file)

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, SKILL_DIR)
                zf.write(file_path, arcname)

    print(f"Package created: {output_file}")

    # Verify package contents
    with zipfile.ZipFile(output_file, 'r') as zf:
        print("\nPackage contents:")
        for name in zf.namelist():
            print(f"  - {name}")

    return True

if __name__ == "__main__":
    success = package_skill()
    exit(0 if success else 1)