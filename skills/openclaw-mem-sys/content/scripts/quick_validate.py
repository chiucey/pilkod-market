#!/usr/bin/env python3
"""
OpenClaw Memory System - Skill Validation Script
Validates SKILL.md frontmatter and structure
"""
import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter format"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter starts at line 1
    if not content.startswith("---"):
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # Extract frontmatter
    lines = content.split("\n")
    if len(lines) < 3:
        return False, "Frontmatter too short"

    frontmatter_end = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter missing closing ---"

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # Check for required fields
    if not re.search(r"^name:\s*\S", frontmatter_text, re.MULTILINE):
        return False, "Missing 'name' field in frontmatter"

    if not re.search(r"^description:\s*", frontmatter_text, re.MULTILINE):
        return False, "Missing 'description' field in frontmatter"

    # Check no markdown title before frontmatter
    if re.search(r"^#\s+\S", content):
        return False, "Markdown title (#) found before frontmatter"

    return True, "Frontmatter validation passed"

def validate_meta(skill_path: Path) -> tuple[bool, str]:
    """Validate _meta.json structure"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"_meta.json invalid JSON: {e}"

    # Check required fields
    if "id" not in meta:
        return False, "Missing 'id' in _meta.json"
    if "version" not in meta:
        return False, "Missing 'version' in _meta.json"

    # Validate id is numeric
    try:
        int(meta["id"])
    except (ValueError, TypeError):
        return False, f"Invalid id: {meta['id']} (must be numeric)"

    return True, "_meta.json validation passed"

def validate_naming(skill_path: Path) -> tuple[bool, str]:
    """Validate folder and name consistency"""
    folder_name = skill_path.name

    # Check folder name is hyphen-case
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", folder_name):
        return False, f"Folder name '{folder_name}' should be hyphen-case (e.g., 'my-skill')"

    # Check SKILL.md frontmatter name matches folder
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if match:
            frontmatter_name = match.group(1).strip().strip('"')
            if frontmatter_name != folder_name:
                return False, f"Name mismatch: folder='{folder_name}', SKILL.md name='{frontmatter_name}'"

    return True, "Naming validation passed"

def validate_paths_english(skill_path: Path) -> tuple[bool, str]:
    """Check all paths are English-only"""
    for item in skill_path.rglob("*"):
        if item.is_dir():
            name = item.name
            if not re.match(r"^[a-zA-Z0-9_\-./]+$", name):
                return False, f"Non-ASCII path found: {item.relative_to(skill_path)}"
    return True, "Path validation passed"

def main():
    skill_path = Path(__file__).parent.parent
    all_passed = True
    results = []

    validations = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta),
        ("Naming", validate_naming),
        ("Paths", validate_paths_english),
    ]

    for name, validator in validations:
        passed, msg = validator(skill_path)
        status = "✅" if passed else "❌"
        results.append(f"{status} {name}: {msg}")
        if not passed:
            all_passed = False

    print("\n📋 Validation Results for:", skill_path.name)
    print("=" * 50)
    for r in results:
        print(r)
    print("=" * 50)

    if all_passed:
        print("✅ All validations passed!")
        sys.exit(0)
    else:
        print("❌ Validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
