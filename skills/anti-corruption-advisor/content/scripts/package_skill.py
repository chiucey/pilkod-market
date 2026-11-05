#!/usr/bin/env python3
"""
Packaging script for anti-corruption-advisor skill
"""
import json
import os
import shutil
import zipfile
from pathlib import Path

def validate_skill(skill_dir):
    """Validate skill structure and metadata"""
    errors = []
    
    # Check SKILL.md exists and has valid frontmatter
    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors
    
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter")
        if 'name:' not in content:
            errors.append("SKILL.md missing 'name' field")
        if 'description:' not in content:
            errors.append("SKILL.md missing 'description' field")
    
    # Check _meta.json exists
    meta_json = Path(skill_dir) / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
    
    return errors

def package_skill(skill_dir, output_dir):
    """Create .skill package"""
    skill_name = "anti-corruption-advisor"
    version = "1.0.0"
    output_file = Path(output_dir) / f"{skill_name}-{version}.skill"
    
    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip scripts directory
            if 'scripts' in root:
                continue
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
    
    return output_file

def main():
    skill_dir = Path("/workspace/temp-skills/anti-corruption-advisor")
    output_dir = Path("/workspace/temp-skills")
    
    print("=" * 50)
    print("Anti-Corruption Advisor Skill Packaging")
    print("=" * 50)
    
    # Validate
    print("\n[1/3] Validating skill structure...")
    errors = validate_skill(skill_dir)
    if errors:
        print("❌ Validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("✅ Validation passed")
    
    # Package
    print("\n[2/3] Packaging skill...")
    output_file = package_skill(skill_dir, output_dir)
    print(f"✅ Created: {output_file}")
    
    # Summary
    print("\n[3/3] Package summary:")
    print(f"  File: {output_file.name}")
    print(f"  Size: {output_file.stat().st_size:,} bytes")
    print(f"  ID: anti-corruption-advisor-2024")
    print(f"  Version: 1.0.0")
    
    print("\n" + "=" * 50)
    print("Packaging complete!")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    exit(main())
