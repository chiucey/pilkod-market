#!/usr/bin/env python3
"""
Quick validation script for lietou-candidate-hunter skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import re
import json
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log(msg, level="info"):
    prefix = {
        "info": "[INFO]",
        "pass": f"{GREEN}[PASS]{RESET}",
        "fail": f"{RED}[FAIL]{RESET}",
        "warn": f"{YELLOW}[WARN]{RESET}"
    }
    print(f"{prefix.get(level, '[INFO]')} {msg}")

def check_frontmatter(skill_path):
    """Check SKILL.md frontmatter format and required fields."""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        log(f"SKILL.md not found at {skill_md}", "fail")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check 1: Frontmatter must start at the very beginning
    if not content.strip().startswith('---'):
        log("SKILL.md must start with YAML frontmatter (---)", "fail")
        return False

    # Extract frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        log("Cannot parse YAML frontmatter", "fail")
        return False

    frontmatter_text = fm_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    missing = []
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            missing.append(field)

    if missing:
        log(f"Missing required frontmatter fields: {', '.join(missing)}", "fail")
        return False

    # Check name field format (hyphen-case, <= 64 chars)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            log(f"name '{name}' should be lowercase hyphen-case", "fail")
            return False
        if len(name) > 64:
            log(f"name exceeds 64 characters: {len(name)}", "fail")
            return False

    # Check description has trigger phrases
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            log("description too short, should be descriptive", "warn")

    log("Frontmatter validation passed", "pass")
    return True

def check_meta_json(skill_path):
    """Check _meta.json exists and has required fields."""
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        log("_meta.json not found", "fail")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        log(f"Invalid JSON in _meta.json: {e}", "fail")
        return False

    required_fields = ['id', 'version']
    missing = []
    for field in required_fields:
        if field not in meta:
            missing.append(field)

    if missing:
        log(f"Missing _meta.json fields: {', '.join(missing)}", "fail")
        return False

    # Check id is numeric
    if not isinstance(meta.get('id'), (int, str)):
        log("id should be a number or string", "fail")
        return False

    # Check version format (semver)
    version = str(meta.get('version', ''))
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        log(f"version '{version}' should be semver format (x.y.z)", "fail")
        return False

    log("_meta.json validation passed", "pass")
    return True

def check_naming_consistency(skill_path):
    """Check folder name matches frontmatter name."""
    folder_name = skill_path.name

    skill_md = skill_path / "SKILL.md"
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(1)
        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            frontmatter_name = name_match.group(1).strip()
            if folder_name != frontmatter_name:
                log(f"Folder name '{folder_name}' != frontmatter name '{frontmatter_name}'", "fail")
                return False

    log("Naming consistency check passed", "pass")
    return True

def check_english_paths(skill_path):
    """Check all paths and names are English (ASCII)."""
    issues = []

    # Check folder name
    if not skill_path.name.isascii():
        issues.append(f"Folder name contains non-ASCII: {skill_path.name}")

    # Check all files
    for item in skill_path.rglob('*'):
        if item.is_file():
            if not item.name.isascii():
                issues.append(f"File name contains non-ASCII: {item.relative_to(skill_path)}")

    # Check SKILL.md content for non-ASCII in paths
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        # Check for file path references that might have Chinese
        path_patterns = re.findall(r'[`"\'](/[^\s`"\']+)', content)
        for path in path_patterns:
            if not all(ord(c) < 128 for c in path):
                issues.append(f"Path in SKILL.md contains non-ASCII: {path}")

    if issues:
        for issue in issues:
            log(issue, "fail")
        return False

    log("English path validation passed", "pass")
    return True

def check_directory_structure(skill_path):
    """Check basic directory structure."""
    required_files = ['SKILL.md', '_meta.json']

    for filename in required_files:
        filepath = skill_path / filename
        if not filepath.exists():
            log(f"Missing required file: {filename}", "fail")
            return False

    log("Directory structure validation passed", "pass")
    return True

def main():
    skill_path = Path(__file__).parent.parent

    print(f"\n{'='*50}")
    print(f"Validating skill: {skill_path.name}")
    print(f"{'='*50}\n")

    checks = [
        ("Directory Structure", lambda: check_directory_structure(skill_path)),
        ("Frontmatter Format", lambda: check_frontmatter(skill_path)),
        ("_meta.json Format", lambda: check_meta_json(skill_path)),
        ("Naming Consistency", lambda: check_naming_consistency(skill_path)),
        ("English Paths", lambda: check_english_paths(skill_path)),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            log(f"Check failed with error: {e}", "fail")
            results.append((name, False))

    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name}")

    print(f"\nResult: {passed}/{total} checks passed")

    if passed == total:
        print(f"\n{GREEN}All validations passed! Skill is ready.{RESET}")
        return 0
    else:
        print(f"\n{RED}Some validations failed. Please fix the issues above.{RESET}")
        return 1

if __name__ == "__main__":
    exit(main())
