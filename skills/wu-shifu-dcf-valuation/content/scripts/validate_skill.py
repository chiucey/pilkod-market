#!/usr/bin/env python3
"""
DCF Valuation Skill Validator
Validates the skill structure, frontmatter, and content quality.
"""

import os
import re
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")


def print_info(msg):
    print(f"{BOLD}→ {msg}{RESET}")


def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter format and content."""
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        print_error(f"SKILL.md not found at {skill_md}")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter
    if not content.startswith('---'):
        print_error("SKILL.md must start with YAML frontmatter (---)")
        return False

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print_error("Invalid frontmatter format")
        return False

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        print_error(f"Missing required frontmatter fields: {', '.join(missing_fields)}")
        return False

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            print_warning(f"Name '{name}' should be hyphen-case (e.g., 'dcf-valuation')")

    # Validate description contains trigger keywords
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            print_warning("Description is very short, consider adding more detail")
        if 'DCF' not in desc.upper() and '估值' not in desc:
            print_warning("Description should mention DCF or valuation")

    print_success("Frontmatter validation passed")
    return True


def validate_meta_json(skill_path):
    """Validate _meta.json exists and has required fields."""
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        print_error("_meta.json not found")
        return False

    import json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    missing_fields = []

    for field in required_fields:
        if field not in meta:
            missing_fields.append(field)

    if missing_fields:
        print_error(f"Missing required _meta.json fields: {', '.join(missing_fields)}")
        return False

    # Validate id is integer
    if not isinstance(meta['id'], int):
        print_error("_meta.json 'id' must be an integer")
        return False

    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        print_error("_meta.json 'version' must be semantic versioning (e.g., 1.0.0)")
        return False

    print_success("_meta.json validation passed")
    return True


def validate_directory_structure(skill_path):
    """Validate skill directory structure."""
    skill_path = Path(skill_path)
    expected_dirs = ['references', 'scripts']

    for dir_name in expected_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            print_warning(f"Optional directory '{dir_name}' not found (optional)")
        else:
            print_success(f"Directory '{dir_name}' exists")

    print_success("Directory structure validation passed")
    return True


def validate_content_quality(skill_path):
    """Validate SKILL.md content quality."""
    skill_md = Path(skill_path) / "SKILL.md"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract content after frontmatter
    content_after_fm = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)

    # Check for key sections
    required_sections = [
        ('DCF估值', 'DCF valuation content'),
        ('现金流', 'Cash flow content'),
        ('WACC', 'WACC calculation'),
        ('假设', 'Assumptions section'),
    ]

    missing = []
    for keyword, description in required_sections:
        if keyword not in content_after_fm:
            missing.append(f"{description} ('{keyword}')")

    if missing:
        print_warning(f"Possible missing content: {', '.join(missing)}")

    # Check for Chinese content
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    if chinese_chars < 500:
        print_warning("Content has limited Chinese characters, ensure Chinese output requirement")

    print_success("Content quality check passed")
    return True


def validate_references(skill_path):
    """Validate reference files if they exist."""
    ref_dir = Path(skill_path) / "references"

    if not ref_dir.exists():
        print_warning("No references directory found (optional)")
        return True

    expected_refs = ['dcf_formulas.md', 'wacc_methodology.md', 'segment_analysis.md']
    missing = []

    for ref in expected_refs:
        ref_path = ref_dir / ref
        if not ref_path.exists():
            missing.append(ref)

    if missing:
        print_warning(f"Recommended reference files missing: {', '.join(missing)}")
    else:
        print_success("All recommended reference files present")

    return True


def run_validation(skill_path):
    """Run all validation checks."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Validating Skill: {skill_path}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    checks = [
        ("Frontmatter Validation", lambda: validate_frontmatter(skill_path)),
        ("Meta JSON Validation", lambda: validate_meta_json(skill_path)),
        ("Directory Structure", lambda: validate_directory_structure(skill_path)),
        ("Content Quality", lambda: validate_content_quality(skill_path)),
        ("References Check", lambda: validate_references(skill_path)),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{BOLD}[{name}]{RESET}")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print_error(f"Validation error: {str(e)}")
            results.append(False)

    print(f"\n{BOLD}{'='*60}{RESET}")
    if all(results):
        print(f"{GREEN}{BOLD}✓ All validations passed!{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some validations failed{RESET}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/wu-shifu-dcf-valuation"
    else:
        skill_path = sys.argv[1]

    sys.exit(run_validation(skill_path))
