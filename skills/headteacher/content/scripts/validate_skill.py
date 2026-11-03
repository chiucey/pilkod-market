#!/usr/bin/env python3
"""
Validate headteacher-workbench skill structure.
Run this before packaging to ensure quality gates pass.
"""
import json
import os
import sys
from pathlib import Path

def check_frontmatter():
    """Check SKILL.md frontmatter structure."""
    skill_md = Path(__file__).parent.parent / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    # Must start with ---
    if not content.startswith("---"):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # Extract frontmatter
    lines = content.split("\n")
    if len(lines) < 3 or lines[1].strip() == "":
        return False, "Frontmatter is empty or malformed"

    # Find end of frontmatter
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter closing --- not found"

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # Check required fields
    if "name:" not in frontmatter_text:
        return False, "Frontmatter missing 'name' field"
    if "description:" not in frontmatter_text:
        return False, "Frontmatter missing 'description' field"

    return True, "Frontmatter validation passed"

def check_meta_json():
    """Check _meta.json structure."""
    meta_json = Path(__file__).parent.parent / "_meta.json"
    if not meta_json.exists():
        return False, "_meta.json not found"

    try:
        data = json.loads(meta_json.read_text(encoding="utf-8"))
        if "id" not in data:
            return False, "_meta.json missing 'id' field"
        if "version" not in data:
            return False, "_meta.json missing 'version' field"
        return True, "_meta.json validation passed"
    except json.JSONDecodeError as e:
        return False, f"_meta.json is not valid JSON: {e}"

def check_directory_structure():
    """Check required directories exist."""
    base = Path(__file__).parent.parent
    required_dirs = ["prompts", "references", "tools"]
    missing = []

    for d in required_dirs:
        if not (base / d).is_dir():
            missing.append(d)

    if missing:
        return False, f"Missing required directories: {', '.join(missing)}"
    return True, "Directory structure validation passed"

def check_naming():
    """Check all files use English names only."""
    base = Path(__file__).parent.parent

    # Check SKILL.md name field
    skill_md = base / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Extract name from frontmatter
    for line in content.split("\n"):
        if line.startswith("name:"):
            name = line.split("name:")[1].strip().strip('"')
            # Check name is ASCII only
            if not name.replace("-", "").replace("_", "").isalnum():
                return False, f"SKILL.md name contains non-ASCII: {name}"

    # Check all file names
    for f in base.rglob("*"):
        if f.is_file():
            name = f.name
            # Allow README_ZH.md and README_EN.md
            if name in ["README_ZH.md", "README_EN.md"]:
                continue
            # Check for non-ASCII in filename
            try:
                name.encode("ascii")
            except UnicodeEncodeError:
                return False, f"Non-ASCII filename found: {f.relative_to(base)}"

    return True, "Naming validation passed"

def main():
    """Run all validations."""
    checks = [
        ("Frontmatter", check_frontmatter),
        ("Meta JSON", check_meta_json),
        ("Directory Structure", check_directory_structure),
        ("Naming", check_naming),
    ]

    all_passed = True
    for name, check_func in checks:
        passed, msg = check_func()
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {msg}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll validations passed!")
        sys.exit(0)
    else:
        print("\nValidation failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
