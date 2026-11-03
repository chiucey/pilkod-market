#!/usr/bin/env python3
"""
Quick validation script for skill quality checks.
Validates frontmatter, structure, and naming conventions.
"""

import json
import os
import re
import sys
from pathlib import Path


class ValidationError:
    def __init__(self, message, file_path=None, line=None):
        self.message = message
        self.file_path = file_path
        self.line = line

    def __str__(self):
        location = ""
        if self.file_path:
            location = f" [{self.file_path}"
            if self.line:
                location += f":{self.line}"
            location += "]"
        return f"❌ {self.message}{location}"


class ValidationSuccess:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"✅ {self.message}"


def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter."""
    errors = []
    successes = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append(ValidationError("SKILL.md not found", str(skill_path)))
        return errors, successes

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter
    if not content.strip().startswith('---'):
        errors.append(ValidationError(
            "SKILL.md must start with frontmatter (---), not markdown title",
            "SKILL.md"
        ))
    else:
        successes.append(ValidationSuccess("SKILL.md starts with frontmatter"))

    # Parse frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append(ValidationError(
            "Could not parse frontmatter. Ensure proper YAML format with opening and closing ---",
            "SKILL.md"
        ))
        return errors, successes

    frontmatter_text = frontmatter_match.group(1)

    # Check required fields
    if 'name:' not in frontmatter_text:
        errors.append(ValidationError(
            "Frontmatter missing 'name' field",
            "SKILL.md"
        ))
    else:
        successes.append(ValidationSuccess("Frontmatter has 'name' field"))

    if 'description:' not in frontmatter_text:
        errors.append(ValidationError(
            "Frontmatter missing 'description' field",
            "SKILL.md"
        ))
    else:
        successes.append(ValidationSuccess("Frontmatter has 'description' field"))

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*([a-z0-9\-]+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1)
        if not re.match(r'^[a-z0-9][a-z0-9\-]*$', name):
            errors.append(ValidationError(
                f"Skill name '{name}' should use hyphen-case (e.g., 'my-skill')",
                "SKILL.md"
            ))
        else:
            successes.append(ValidationSuccess(f"Skill name format is valid: {name}"))

            # Check if name matches folder name
            folder_name = skill_path.name
            if name != folder_name:
                errors.append(ValidationError(
                    f"Skill name '{name}' does not match folder name '{folder_name}'",
                    "SKILL.md"
                ))

    # Check description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
        if len(description) < 20:
            errors.append(ValidationError(
                "Description is too short (minimum 20 characters)",
                "SKILL.md"
            ))
        else:
            successes.append(ValidationSuccess("Description length is adequate"))

    return errors, successes


def validate_meta_json(skill_path):
    """Validate _meta.json structure."""
    errors = []
    successes = []

    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append(ValidationError("_meta.json not found", str(skill_path)))
        return errors, successes

    try:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # Check required fields
        if 'id' not in meta:
            errors.append(ValidationError(
                "_meta.json missing 'id' field",
                "_meta.json"
            ))
        else:
            successes.append(ValidationSuccess("_meta.json has 'id' field"))

        if 'version' not in meta:
            errors.append(ValidationError(
                "_meta.json missing 'version' field",
                "_meta.json"
            ))
        else:
            successes.append(ValidationSuccess("_meta.json has 'version' field"))

            # Validate version format (semantic versioning)
            version = meta['version']
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                errors.append(ValidationError(
                    f"Version '{version}' should use semantic versioning (e.g., '1.0.0')",
                    "_meta.json"
                ))
            else:
                successes.append(ValidationSuccess(f"Version format is valid: {version}"))

        return errors, successes
    except json.JSONDecodeError as e:
        errors.append(ValidationError(
            f"Invalid JSON in _meta.json: {e}",
            "_meta.json"
        ))
        return errors, successes


def validate_naming(skill_path):
    """Validate all paths and names are in English."""
    errors = []
    successes = []

    # Check skill folder name
    folder_name = skill_path.name
    if not re.match(r'^[a-z0-9\-]+$', folder_name):
        errors.append(ValidationError(
            f"Folder name '{folder_name}' contains non-English characters. Use only lowercase letters, numbers, and hyphens.",
            str(skill_path)
        ))
    else:
        successes.append(ValidationSuccess(f"Folder name is valid: {folder_name}"))

    # Check all file and folder names recursively
    for root, dirs, files in os.walk(skill_path):
        for dirname in dirs:
            dir_path = os.path.join(root, dirname)
            rel_path = os.path.relpath(dir_path, skill_path)
            if not re.match(r'^[a-z0-9\-_/]+$', rel_path):
                errors.append(ValidationError(
                    f"Directory name '{rel_path}' contains non-English characters",
                    str(skill_path)
                ))

        for filename in files:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, skill_path)
            if not re.match(r'^[a-z0-9\-_./]+\.[a-z]+$', rel_path, re.IGNORECASE):
                errors.append(ValidationError(
                    f"File name '{rel_path}' contains non-English or special characters",
                    str(skill_path)
                ))

    if not errors:
        successes.append(ValidationSuccess("All file and folder names are in English"))

    return errors, successes


def validate_structure(skill_path):
    """Validate skill directory structure."""
    errors = []
    successes = []

    # Check SKILL.md exists
    if not (skill_path / "SKILL.md").exists():
        errors.append(ValidationError("SKILL.md not found", str(skill_path)))

    # Check _meta.json exists
    if not (skill_path / "_meta.json").exists():
        errors.append(ValidationError("_meta.json not found", str(skill_path)))

    # Check for optional directories
    if (skill_path / "references").exists():
        successes.append(ValidationSuccess("references/ directory exists"))
        ref_count = len(list((skill_path / "references").glob("*.md")))
        successes.append(ValidationSuccess(f"Found {ref_count} reference files"))

    if (skill_path / "scripts").exists():
        successes.append(ValidationSuccess("scripts/ directory exists"))

    if (skill_path / "assets").exists():
        successes.append(ValidationSuccess("assets/ directory exists"))

    return errors, successes


def validate_skill(skill_path):
    """Main validation function."""
    skill_path = Path(skill_path)

    print(f"\n{'='*60}")
    print(f"🔍 Validating skill: {skill_path.name}")
    print(f"{'='*60}\n")

    all_errors = []
    all_successes = []

    # Run all validations
    struct_errors, struct_successes = validate_structure(skill_path)
    front_errors, front_successes = validate_frontmatter(skill_path)
    meta_errors, meta_successes = validate_meta_json(skill_path)
    name_errors, name_successes = validate_naming(skill_path)

    all_errors.extend(struct_errors + front_errors + meta_errors + name_errors)
    all_successes.extend(struct_successes + front_successes + meta_successes + name_successes)

    # Print results
    print("📋 Structure & Metadata:")
    for s in struct_successes:
        print(f"  {s}")
    for e in struct_errors:
        print(f"  {e}")

    print("\n📝 Frontmatter:")
    for s in front_successes:
        print(f"  {s}")
    for e in front_errors:
        print(f"  {e}")

    print("\n⚙️  Meta JSON:")
    for s in meta_successes:
        print(f"  {s}")
    for e in meta_errors:
        print(f"  {e}")

    print("\n🔤 Naming:")
    for s in name_successes:
        print(f"  {s}")
    for e in name_errors:
        print(f"  {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Validation Summary:")
    print(f"   ✅ Passed: {len(all_successes)}")
    print(f"   ❌ Failed: {len(all_errors)}")
    print(f"{'='*60}\n")

    if all_errors:
        print("❌ VALIDATION FAILED")
        for error in all_errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ VALIDATION PASSED - All checks passed!")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
