#!/usr/bin/env python3
"""
Quick validation script for skill structure and frontmatter
"""
import os
import re
import json
import sys

def validate_skill(skill_path):
    """Validate skill structure and frontmatter"""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return errors, warnings

    # Read SKILL.md
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists at the beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Parse frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Could not parse YAML frontmatter")
    else:
        frontmatter_text = frontmatter_match.group(1)

        # Check required fields
        if not re.search(r'^name:', frontmatter_text, re.MULTILINE):
            errors.append("Frontmatter missing 'name' field")
        else:
            name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                # Check name format (hyphen-case)
                if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
                    warnings.append(f"Name '{name}' should use hyphen-case format")
                # Check name matches folder name
                folder_name = os.path.basename(skill_path)
                if name != folder_name:
                    errors.append(f"Name '{name}' does not match folder name '{folder_name}'")

        if not re.search(r'^description:', frontmatter_text, re.MULTILINE):
            errors.append("Frontmatter missing 'description' field")
        else:
            desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
            if desc_match:
                desc = desc_match.group(1).strip()
                if len(desc) < 10:
                    warnings.append("Description is too short (< 10 chars)")
                # Check for trigger phrases
                if not any(phrase in desc for phrase in ['研究选题', '研究问题', '研究想法', '选题', '论文选题', '经济学']):
                    warnings.append("Description should include trigger phrases for routing")

    # Check _meta.json
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("_meta.json not found")
    else:
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
            elif not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
                warnings.append("Version should follow semver format (e.g., 1.0.0)")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Check directory structure
    expected_dirs = []
    for item in os.listdir(skill_path):
        item_path = os.path.join(skill_path, item)
        if os.path.isdir(item_path):
            expected_dirs.append(item)

    valid_dirs = ['scripts', 'references', 'assets']
    for d in valid_dirs:
        if d in expected_dirs:
            # Check directory is not empty
            dir_path = os.path.join(skill_path, d)
            if os.listdir(dir_path):
                print(f"  [OK] {d}/ directory exists and has content")
            else:
                warnings.append(f"{d}/ directory is empty")

    return errors, warnings

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    errors, warnings = validate_skill(skill_path)

    if errors:
        print("\n[ERRORS]:")
        for e in errors:
            print(f"  ❌ {e}")

    if warnings:
        print("\n[WARNINGS]:")
        for w in warnings:
            print(f"  ⚠️ {w}")

    if not errors and not warnings:
        print("\n[SUCCESS] All checks passed!")
        return 0
    elif not errors:
        print("\n[PARTIAL] Passed with warnings")
        return 0
    else:
        print("\n[FAILED] Validation errors found")
        return 1

if __name__ == "__main__":
    sys.exit(main())
