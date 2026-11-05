#!/usr/bin/env python3
"""
Skill Validation Script - Frontmatter and Structure Verification
Validates SKILL.md frontmatter, _meta.json, naming conventions, and structure.
"""

import os
import sys
import json
import re
from pathlib import Path

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_result(check_name: str, passed: bool, message: str = ""):
    """Print validation result with colored output."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status} {check_name}")
    if message:
        print(f"         {message}")


def validate_frontmatter(skill_dir: Path) -> bool:
    """Validate SKILL.md frontmatter format and required fields."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print_result("SKILL.md exists", False, f"File not found: {skill_md}")
        return False

    content = skill_md.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check if file starts with frontmatter delimiter
    if not lines or lines[0].strip() != '---':
        print_result("Frontmatter at start", False, "SKILL.md must start with '---'")
        return False

    # Find closing delimiter
    try:
        end_idx = lines[1:].index('---') + 1
    except ValueError:
        print_result("Frontmatter delimiter", False, "Missing closing '---' delimiter")
        return False

    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # Parse frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    all_passed = True

    # Check required fields
    if 'name' not in frontmatter:
        print_result("name field", False, "Missing required 'name' field")
        all_passed = False
    else:
        name = frontmatter['name']
        # Check naming convention (hyphen-case)
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            print_result("name format", False, f"'{name}' should use hyphen-case (e.g., 'my-skill')")
            all_passed = False
        else:
            print_result("name field", True)

        # Check length
        if len(name) > 64:
            print_result("name length", False, f"'{name}' exceeds 64 characters")
            all_passed = False
        else:
            print_result("name length", True)

    if 'description' not in frontmatter:
        print_result("description field", False, "Missing required 'description' field")
        all_passed = False
    else:
        print_result("description field", True)
        desc = frontmatter['description']
        # Check if description contains trigger phrases
        if not any(phrase in desc.lower() for phrase in ['when', 'use when', 'activate', 'trigger']):
            print_result("description quality", False, "Description should include trigger conditions (e.g., 'Use when...')")
            all_passed = False
        else:
            print_result("description quality", True)

    print_result("Frontmatter at start", True)
    return all_passed


def validate_meta_json(skill_dir: Path) -> bool:
    """Validate _meta.json format and required fields."""
    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        print_result("_meta.json exists", False, "Missing _meta.json file")
        return False

    print_result("_meta.json exists", True)

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print_result("_meta.json format", False, f"Invalid JSON: {e}")
        return False

    all_passed = True

    if 'id' not in meta:
        print_result("id field", False, "Missing required 'id' field")
        all_passed = False
    else:
        print_result("id field", True)

    if 'version' not in meta:
        print_result("version field", False, "Missing required 'version' field")
        all_passed = False
    else:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            print_result("version format", False, f"'{version}' should follow semantic versioning (e.g., '1.0.0')")
            all_passed = False
        else:
            print_result("version field", True)

    return all_passed


def validate_directory_structure(skill_dir: Path) -> bool:
    """Validate directory naming and structure."""
    all_passed = True

    # Check directory name matches skill name
    if '_meta.json' in (skill_dir / '_meta.json').read_text(encoding='utf-8'):
        try:
            meta = json.loads((skill_dir / '_meta.json').read_text(encoding='utf-8'))
            skill_name = meta.get('id')
            # Directory name should match skill name in frontmatter
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding='utf-8')
                if content.startswith('---'):
                    end_idx = content.index('---', 3)
                    fm = content[3:end_idx]
                    name_match = re.search(r"name:\s*([^\n]+)", fm)
                    if name_match:
                        frontmatter_name = name_match.group(1).strip()
                        dir_name = skill_dir.name
                        if frontmatter_name != dir_name:
                            print_result("Directory naming", False,
                                        f"Directory '{dir_name}' should match 'name: {frontmatter_name}'")
                            all_passed = False
                        else:
                            print_result("Directory naming", True)
        except:
            pass

    # Check for unwanted files
    unwanted_patterns = ['*.pyc', '__pycache__', '.DS_Store', '*.swp']
    for pattern in unwanted_patterns:
        if list(skill_dir.rglob(pattern)):
            print_result(f"Clean structure ({pattern})", False, f"Found unwanted file matching '{pattern}'")
            all_passed = False

    print_result("Directory structure", True)
    return all_passed


def validate_skill(skill_path: str) -> bool:
    """Run all validations on a skill directory."""
    skill_dir = Path(skill_path).resolve()

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Validating: {skill_dir.name}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    if not skill_dir.exists():
        print(f"{RED}Error: Skill directory not found: {skill_dir}{RESET}")
        return False

    if not skill_dir.is_dir():
        print(f"{RED}Error: {skill_dir} is not a directory{RESET}")
        return False

    results = []
    results.append(("Frontmatter", validate_frontmatter(skill_dir)))
    results.append(("_meta.json", validate_meta_json(skill_dir)))
    results.append(("Structure", validate_directory_structure(skill_dir)))

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Summary{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    all_passed = all(r[1] for r in results)
    for name, passed in results:
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {status} {name}")

    if all_passed:
        print(f"\n{GREEN}{BOLD}All validations passed!{RESET}")
    else:
        print(f"\n{RED}{BOLD}Some validations failed.{RESET}")

    return all_passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <skill_directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
