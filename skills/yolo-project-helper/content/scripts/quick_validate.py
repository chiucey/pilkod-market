#!/usr/bin/env python3
"""
YOLO Project Helper Skill Validation Script
Validates skill structure and frontmatter compliance
"""

import os
import sys
import json
import re
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_check(passed, message):
    status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
    print(f"[{status}] {message}")
    return "PASS" if passed else "FAIL"

def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter format and content"""
    skill_md = skill_path / "SKILL.md"
    results = []

    if not skill_md.exists():
        results.append(print_check(False, "SKILL.md not found"))
        return results

    content = skill_md.read_text(encoding='utf-8')

    # Check 1: Frontmatter must start at line 1
    if not content.startswith('---'):
        results.append(print_check(False, "Frontmatter must start at line 1 (no markdown headers before '---')"))
        return results

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        results.append(print_check(False, "Frontmatter closing '---' not found"))
        return results

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])
    results.append(print_check(True, "Frontmatter format valid"))

    # Parse YAML-like frontmatter
    frontmatter = {}
    current_key = None
    for line in lines[1:frontmatter_end]:
        if ':' in line:
            key, value = line.split(':', 1)
            current_key = key.strip()
            frontmatter[current_key] = value.strip()

    # Check required fields
    results.append(print_check('name' in frontmatter, "Frontmatter contains 'name' field"))
    results.append(print_check('description' in frontmatter, "Frontmatter contains 'description' field"))

    # Validate name format (hyphen-case)
    if 'name' in frontmatter:
        name = frontmatter['name']
        is_valid_name = bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name))
        results.append(print_check(is_valid_name, f"Name format valid: '{name}'"))

    # Check description is not empty
    if 'description' in frontmatter:
        desc = frontmatter['description']
        results.append(print_check(len(desc) >= 10, "Description is not empty and meaningful"))

    return results

def validate_meta_json(skill_path):
    """Validate _meta.json exists and has required fields"""
    meta_path = skill_path / "_meta.json"
    results = []

    if not meta_path.exists():
        results.append(print_check(False, "_meta.json not found"))
        return results

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        results.append(print_check('id' in meta, "_meta.json contains 'id' field"))
        results.append(print_check('version' in meta, "_meta.json contains 'version' field"))

        # Validate version format
        if 'version' in meta:
            version = meta['version']
            is_valid_version = bool(re.match(r'^\d+\.\d+\.\d+$', version))
            results.append(print_check(is_valid_version, f"Version format valid: '{version}'"))

        results.append(print_check(True, "_meta.json is valid JSON"))
    except json.JSONDecodeError as e:
        results.append(print_check(False, f"_meta.json is not valid JSON: {e}"))
    except Exception as e:
        results.append(print_check(False, f"Error reading _meta.json: {e}"))

    return results

def validate_directory_structure(skill_path):
    """Validate directory naming and structure"""
    results = []

    # Check skill name matches folder name
    skill_name = skill_path.name if skill_path.name else skill_path.absolute().name
    is_valid_name = bool(re.match(r'^[a-z0-9-]+$', skill_name))
    results.append(print_check(is_valid_name, f"Skill folder name valid: '{skill_name}'"))

    # Check for unwanted files in root
    unwanted_patterns = ['__pycache__', '.pyc', '.git', 'node_modules']
    for item in skill_path.iterdir():
        if any(pattern in item.name for pattern in unwanted_patterns):
            results.append(print_check(False, f"Unwanted item found: {item.name}"))
        else:
            results.append(print_check(True, f"Clean directory structure"))

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"{Colors.RED}Error: Path does not exist: {skill_path}{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.BOLD}Validating YOLO Project Helper Skill{Colors.RESET}")
    print("=" * 50)

    all_results = []

    print(f"\n{Colors.BOLD}[1] Frontmatter Validation{Colors.RESET}")
    all_results.extend(validate_frontmatter(skill_path))

    print(f"\n{Colors.BOLD}[2] Meta JSON Validation{Colors.RESET}")
    all_results.extend(validate_meta_json(skill_path))

    print(f"\n{Colors.BOLD}[3] Directory Structure{Colors.RESET}")
    all_results.extend(validate_directory_structure(skill_path))

    print(f"\n{Colors.BOLD}Summary{Colors.RESET}")
    print("=" * 50)

    passed = sum(1 for r in all_results if 'PASS' in r)
    total = len(all_results)

    print(f"Passed: {Colors.GREEN}{passed}/{total}{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All validations passed!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some validations failed.{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
