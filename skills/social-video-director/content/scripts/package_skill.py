#!/usr/bin/env python3
"""
Skill Packaging Script
Packages the social-video-director skill into a distributable .skill file
"""

import os
import json
import shutil
from pathlib import Path

SKILL_DIR = Path("/workspace/temp-skills/social-video-director")
OUTPUT_DIR = Path("/workspace/temp-skills/output")
SKILL_NAME = "social-video-director"
VERSION = "1.0.0"

def validate_skill():
    """Validate skill structure and metadata"""
    errors = []

    # Check SKILL.md exists and has frontmatter
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            errors.append("SKILL.md must start with frontmatter (---)")

        # Check frontmatter fields
        if 'name:' not in content[:500]:
            errors.append("frontmatter missing 'name' field")
        if 'description:' not in content[:1000]:
            errors.append("frontmatter missing 'description' field")

    # Check _meta.json
    meta_json = SKILL_DIR / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    # Check references directory
    references_dir = SKILL_DIR / "references"
    if not references_dir.exists():
        errors.append("references directory not found")

    return errors

def package_skill():
    """Package the skill into a .skill file"""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Validate first
    errors = validate_skill()
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return False

    # Create output filename
    output_file = OUTPUT_DIR / f"{SKILL_NAME}.skill"

    # Copy skill directory to output with _meta.json
    temp_dir = OUTPUT_DIR / "temp_skill"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    # Copy entire skill directory
    shutil.copytree(SKILL_DIR, temp_dir)

    # Create zip archive
    shutil.make_archive(str(output_file), 'zip', str(temp_dir))

    # Rename .zip to .skill
    zip_file = OUTPUT_DIR / f"{SKILL_NAME}.skill.zip"
    if output_file.exists():
        output_file.unlink()
    shutil.move(str(zip_file), str(output_file))

    # Clean up temp directory
    shutil.rmtree(temp_dir)

    print(f"Skill packaged successfully: {output_file}")
    print(f"Skill version: {VERSION}")
    print(f"Files included:")
    for f in SKILL_DIR.rglob("*"):
        if f.is_file():
            rel_path = f.relative_to(SKILL_DIR)
            print(f"  - {rel_path}")

    return True

if __name__ == "__main__":
    package_skill()
