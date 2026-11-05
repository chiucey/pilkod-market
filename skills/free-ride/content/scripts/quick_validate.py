#!/usr/bin/env python3
"""
Quick Validation Script for Free-Ride Skill

Validates:
1. SKILL.md frontmatter format
2. Required frontmatter fields (name, description)
3. _meta.json format and required fields
4. Directory structure compliance
"""

import json
import os
import re
import sys
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
META_JSON = SKILL_DIR / "_meta.json"


def check_result(check_name: str, passed: bool, message: str = ""):
    """Print check result with color"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  [{status}] {check_name}")
    if message:
        print(f"         {message}")
    return passed


def validate_frontmatter():
    """Validate SKILL.md frontmatter format"""
    print("\n📋 Validating SKILL.md frontmatter...")

    if not SKILL_MD.exists():
        return check_result("SKILL.md exists", False, f"File not found: {SKILL_MD}")

    content = SKILL_MD.read_text(encoding="utf-8")

    # Check 1: Frontmatter must be at the beginning
    if not content.startswith("---"):
        return check_result(
            "Frontmatter at beginning",
            False,
            "SKILL.md must start with '---' (YAML frontmatter)"
        )

    # Extract frontmatter - split with limit 3 to get: [empty, frontmatter, content]
    parts = content.split("---", 3)
    if len(parts) < 3:
        return check_result(
            "Frontmatter format",
            False,
            "Frontmatter must have opening and closing '---'"
        )

    frontmatter_text = parts[1]
    # Content is in parts[2] (with limit=3), but we need to verify no --- inside frontmatter
    # If there's a --- inside description, split would give wrong result
    # Check if frontmatter ends properly by verifying we can find the closing ---
    content_after_frontmatter = content[len("---") + len(frontmatter_text) + len("---\n"):] if len(parts) >= 2 else ""

    # Verify frontmatter doesn't contain --- (which would break parsing)
    if "---" in frontmatter_text:
        check_result(
            "Frontmatter integrity",
            False,
            "Frontmatter contains '---' which breaks YAML parsing"
        )

    # Content starts after the closing --- marker
    rest_content = content_after_frontmatter.lstrip("").lstrip("\n")

    # Parse frontmatter
    try:
        frontmatter = {}
        for line in frontmatter_text.strip().split("\n"):
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                frontmatter[key] = True
    except Exception as e:
        return check_result("Frontmatter parse", False, str(e))

    # Check 2: Must have 'name' field
    has_name = check_result(
        "Has 'name' field",
        "name" in frontmatter,
        "Frontmatter must include 'name' field"
    )

    # Check 3: Must have 'description' field
    has_desc = check_result(
        "Has 'description' field",
        "description" in frontmatter,
        "Frontmatter must include 'description' field"
    )

    # Check 4: Name should match folder name
    expected_name = SKILL_DIR.name
    name_match = False
    for line in frontmatter_text.strip().split("\n"):
        if line.startswith("name:"):
            actual_name = line.split(":", 1)[1].strip()
            name_match = actual_name == expected_name
            break

    check_result(
        "Name matches folder",
        name_match,
        f"Expected: '{expected_name}'" if not name_match else ""
    )

    # Check 5: Content starts properly after frontmatter
    if rest_content and not rest_content.startswith("#"):
        check_result(
            "Content structure",
            True,
            "Content starts after frontmatter"
        )
    elif not rest_content:
        check_result(
            "Content structure",
            False,
            "No content after frontmatter"
        )
    else:
        check_result("Content structure", True)

    return has_name and has_desc


def validate_meta_json():
    """Validate _meta.json format"""
    print("\n📋 Validating _meta.json...")

    if not META_JSON.exists():
        return check_result("_meta.json exists", False, f"File not found: {META_JSON}")

    try:
        data = json.loads(META_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return check_result("Valid JSON", False, str(e))

    # Check required fields
    has_id = check_result("Has 'id' field", "id" in data)
    has_version = check_result("Has 'version' field", "version" in data)

    # Check id is a valid integer
    if "id" in data:
        valid_id = isinstance(data["id"], int) and data["id"] > 0
        check_result("'id' is valid integer", valid_id, "id must be a positive integer")

    # Check version is a valid string
    if "version" in data:
        valid_version = isinstance(data["version"], str) and re.match(
            r"^\d+\.\d+\.\d+$", data["version"]
        )
        check_result(
            "'version' is valid semver",
            valid_version,
            "version must follow semver format (e.g., 1.0.0)"
        )

    return has_id and has_version


def validate_directory_structure():
    """Validate skill directory structure"""
    print("\n📋 Validating directory structure...")

    # Required files
    required_files = {
        "SKILL.md": SKILL_MD,
        "_meta.json": META_JSON,
    }

    all_passed = True
    for name, path in required_files.items():
        passed = path.exists()
        all_passed = check_result(f"Has {name}", passed, f"Missing: {path}") and all_passed

    # Optional directories
    optional_dirs = {
        "scripts/": SKILL_DIR / "scripts",
        "references/": SKILL_DIR / "references",
        "assets/": SKILL_DIR / "assets",
    }

    for name, path in optional_dirs.items():
        exists = path.exists() and path.is_dir()
        status = f"{GREEN}✓ (optional){RESET}" if exists else f"{YELLOW}○ (optional){RESET}"
        print(f"  [{status}] {name} {'present' if exists else 'not present'}")

    return all_passed


def validate_no_unsafe_paths():
    """Check for unsafe path patterns"""
    print("\n📋 Checking for unsafe patterns...")

    # Check for symlink escapes (in skill directory)
    all_files = list(SKILL_DIR.rglob("*"))
    unsafe_found = False

    for f in all_files:
        if f.is_symlink():
            target = f.readlink()
            if not target.is_relative_to(SKILL_DIR):
                check_result(
                    f"Safe symlink: {f.name}",
                    False,
                    f"Symlink escapes skill directory: {target}"
                )
                unsafe_found = True

    if not unsafe_found:
        check_result("No unsafe symlinks", True)

    return not unsafe_found


def main():
    """Run all validations"""
    print("=" * 60)
    print("🔍 Free-Ride Skill Quick Validation")
    print("=" * 60)

    results = [
        validate_frontmatter(),
        validate_meta_json(),
        validate_directory_structure(),
        validate_no_unsafe_paths(),
    ]

    print("\n" + "=" * 60)
    if all(results):
        print(f"{GREEN}✓ All validations passed!{RESET}")
        return 0
    else:
        print(f"{RED}✗ Some validations failed{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
