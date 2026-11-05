#!/usr/bin/env python3
"""
Package TensorFlow.js Skill for Distribution
Creates a .skill archive file for deployment
"""

import os
import json
import shutil
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path("/workspace/temp-skills/dist")
SKILL_NAME = "tensorflow-js"


def validate_skill():
    """Validate skill structure before packaging"""
    errors = []

    # Check SKILL.md exists
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md must start with frontmatter")
        if "name:" not in content or "description:" not in content:
            errors.append("SKILL.md missing required frontmatter fields")

    # Check _meta.json
    meta_json = SKILL_DIR / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta or "version" not in meta:
                errors.append("_meta.json missing required fields")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    return errors


def package_skill():
    """Create .skill package"""
    print(f"Packaging skill: {SKILL_NAME}")

    # Validate first
    errors = validate_skill()
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read meta
    meta = json.loads((SKILL_DIR / "_meta.json").read_text(encoding="utf-8"))

    # Create package filename
    output_file = OUTPUT_DIR / f"{SKILL_NAME}-{meta['version']}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # Skip __pycache__ and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                zf.write(file_path, arcname)
                print(f"  Adding: {arcname}")

    print(f"Package created: {output_file}")
    return True


if __name__ == "__main__":
    success = package_skill()
    exit(0 if success else 1)
