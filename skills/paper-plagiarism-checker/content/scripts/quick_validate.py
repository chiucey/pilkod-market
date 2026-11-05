"""
Paper Plagiarism Checker Skill - Quick validation script
Validates SKILL.md structure and frontmatter format
"""

import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """Validate frontmatter format"""
    errors = []
    skill_file = Path(skill_path) / "SKILL.md"

    if not skill_file.exists():
        return False, [f"SKILL.md not found at {skill_path}"]

    content = skill_file.read_text(encoding='utf-8')

    # Check if first line is ---
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        errors.append("❌ Frontmatter must start at line 1 with '---'")
    else:
        # Find closing ---
        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_idx = i
                break

        if end_idx is None:
            errors.append("❌ Frontmatter must have closing '---'")
        else:
            frontmatter_content = '\n'.join(lines[1:end_idx])

            # Check required fields
            if not re.search(r'^name:\s*.+$', frontmatter_content, re.MULTILINE):
                errors.append("❌ Missing required field: name")
            if not re.search(r'^description:\s*.+$', frontmatter_content, re.MULTILINE):
                errors.append("❌ Missing required field: description")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json format"""
    errors = []
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        return False, ["❌ _meta.json not found"]

    try:
        import json
        content = json.loads(meta_file.read_text(encoding='utf-8'))

        if 'id' not in content:
            errors.append("❌ Missing required field: id in _meta.json")
        if 'version' not in content:
            errors.append("❌ Missing required field: version in _meta.json")
    except json.JSONDecodeError as e:
        errors.append(f"❌ Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """Validate directory structure"""
    errors = []
    skill_name = Path(skill_path).name

    # Check name format (hyphen-case)
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"❌ Skill name '{skill_name}' should use hyphen-case format")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/paper-plagiarism-checker"
    else:
        skill_path = sys.argv[1]

    print(f"🔍 Validating skill at: {skill_path}\n")

    all_passed = True

    # Validate frontmatter
    passed, errors = validate_frontmatter(skill_path)
    print("📋 Frontmatter Validation:", "✅ PASSED" if passed else "❌ FAILED")
    for e in errors:
        print(f"   {e}")
    all_passed = all_passed and passed

    # Validate meta json
    passed, errors = validate_meta_json(skill_path)
    print("\n📦 Meta JSON Validation:", "✅ PASSED" if passed else "❌ FAILED")
    for e in errors:
        print(f"   {e}")
    all_passed = all_passed and passed

    # Validate structure
    passed, errors = validate_structure(skill_path)
    print("\n📁 Directory Structure:", "✅ PASSED" if passed else "❌ FAILED")
    for e in errors:
        print(f"   {e}")
    all_passed = all_passed and passed

    print("\n" + "=" * 50)
    print(f"Overall: {'✅ ALL VALIDATIONS PASSED' if all_passed else '❌ VALIDATION FAILED'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())