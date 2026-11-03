#!/usr/bin/env python3
"""
Quick validation script for arxiv-paper-searcher skill.
Validates SKILL.md frontmatter and structure.
"""

import os
import json
import sys


def validate_frontmatter(skill_md_path: str) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter format."""
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check frontmatter exists
    if not content.startswith("---"):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # Find frontmatter end (first closing ---)
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False
    found_end = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                frontmatter_lines.append(line)
            elif not found_end:
                # End of frontmatter
                found_end = True
                break
        elif in_frontmatter and not found_end:
            frontmatter_lines.append(line)

    frontmatter_text = "\n".join(frontmatter_lines)

    # Parse frontmatter
    try:
        import yaml
        meta = yaml.safe_load(frontmatter_text)
    except ImportError:
        # Manual parsing fallback
        meta = {}
        for line in frontmatter_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()

    # Check required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required frontmatter field: {field}"

    # Validate name format
    name = meta["name"]
    if not name.replace("-", "").replace("_", "").isalnum():
        return False, f"Invalid name format: {name}. Use hyphen-case or underscore_case."

    if len(name) > 64:
        return False, f"Name too long: {len(name)} chars (max 64)"

    # Validate description
    desc = meta.get("description", "")
    if len(desc) < 10:
        return False, "Description too short (min 10 chars)"

    return True, "Frontmatter validated successfully"


def validate_meta_json(meta_json_path: str) -> tuple[bool, str]:
    """Validate _meta.json format."""
    if not os.path.exists(meta_json_path):
        return False, "_meta.json not found"

    with open(meta_json_path, "r", encoding="utf-8") as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in _meta.json: {e}"

    # Check required fields
    if "id" not in meta:
        return False, "Missing required field: id"
    if "version" not in meta:
        return False, "Missing required field: version"

    # Validate id is integer
    if not isinstance(meta["id"], int):
        return False, f"id must be integer, got {type(meta['id']).__name__}"

    # Validate version format
    version = meta["version"]
    if not isinstance(version, str):
        return False, f"version must be string, got {type(version).__name__}"

    return True, "_meta.json validated successfully"


def validate_structure(skill_dir: str) -> tuple[bool, str]:
    """Validate skill directory structure."""
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        path = os.path.join(skill_dir, filename)
        if not os.path.exists(path):
            return False, f"Missing required file: {filename}"

    return True, "Structure validated successfully"


def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    all_passed = True

    # Validate structure
    passed, msg = validate_structure(skill_dir)
    print(f"[{'PASS' if passed else 'FAIL'}] Structure: {msg}")
    if not passed:
        all_passed = False

    # Validate _meta.json
    meta_json_path = os.path.join(skill_dir, "_meta.json")
    passed, msg = validate_meta_json(meta_json_path)
    print(f"[{'PASS' if passed else 'FAIL'}] _meta.json: {msg}")
    if not passed:
        all_passed = False

    # Validate frontmatter
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    passed, msg = validate_frontmatter(skill_md_path)
    print(f"[{'PASS' if passed else 'FAIL'}] Frontmatter: {msg}")
    if not passed:
        all_passed = False

    # Validate search script exists
    script_path = os.path.join(skill_dir, "scripts", "search_arxiv.py")
    if os.path.exists(script_path):
        print(f"[PASS] Search script exists")
    else:
        print(f"[WARN] Search script not found (optional)")

    if all_passed:
        print("\n✓ All validation checks passed")
        return 0
    else:
        print("\n✗ Some validation checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
