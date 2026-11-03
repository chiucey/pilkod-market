#!/usr/bin/env python3
"""
Skill Packaging Script for dynamic-multi-agent-system
Packages the skill into a .skill archive for distribution
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path("/workspace/temp-skills/dynamic-multi-agent-system")
OUTPUT_DIR = Path("/workspace/temp-skills/output")
SKILL_ID = "1892486405"
VERSION = "1.4.0"

def validate_skill():
    """Validate skill structure and metadata"""
    errors = []

    # Check SKILL.md exists and has valid frontmatter
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter")
        if 'name: dynamic-multi-agent-system' not in content:
            errors.append("SKILL.md missing required name field")

    # Check _meta.json exists and is valid
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
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    return errors

def count_files():
    """Count files in skill directory"""
    count = 0
    for root, dirs, files in os.walk(SKILL_DIR):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        count += len([f for f in files if not f.startswith('.')])
    return count

def create_skill_archive():
    """Create the .skill archive file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = OUTPUT_DIR / f"dynamic-multi-agent-system-v{VERSION}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                zipf.write(file_path, arcname)

    return output_file

def main():
    print("=" * 60)
    print("Skill Packaging: dynamic-multi-agent-system")
    print("=" * 60)

    # Validate
    print("\n[1/3] Validating skill structure...")
    errors = validate_skill()
    if errors:
        print("FAILED: Validation errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    print("PASSED: Validation successful")

    # Count files
    print("\n[2/3] Counting files...")
    file_count = count_files()
    print(f"   Total files: {file_count}")

    # Create archive
    print("\n[3/3] Creating .skill archive...")
    output_file = create_skill_archive()
    print(f"SUCCESS: Archive created: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.2f} KB")

    print("\n" + "=" * 60)
    print("Packaging complete!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    main()
