#!/usr/bin/env python3
"""
Quick Validation Script for ppt-slides-generator Skill

Validates:
1. SKILL.md frontmatter structure
2. Required fields present
3. No forbidden patterns (e.g., title before frontmatter)
4. References path validity
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
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def validate_skill(skill_path: str) -> bool:
    """Validate the skill structure and content."""
    skill_dir = Path(skill_path)
    skill_md = skill_dir / "SKILL.md"
    meta_json = skill_dir / "_meta.json"
    references_dir = skill_dir / "references"

    all_passed = True

    # 1. Check SKILL.md exists
    print(f"\n{Colors.BOLD}Validating: {skill_path}{Colors.END}\n")

    if not skill_md.exists():
        print_error(f"SKILL.md not found at {skill_md}")
        return False

    # 2. Read SKILL.md content
    content = skill_md.read_text(encoding='utf-8')

    # 3. Check frontmatter is at the beginning
    if not content.startswith('---'):
        print_error("SKILL.md must start with frontmatter (---)")
        print_warning("Frontmatter must be the FIRST content (before any markdown)")
        all_passed = False
    else:
        print_success("Frontmatter starts correctly at first line")

    # 4. Parse frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print_error("Could not parse frontmatter")
        all_passed = False
    else:
        frontmatter_text = frontmatter_match.group(1)
        print_success("Frontmatter parsed successfully")

        # 5. Check required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
                print_error(f"Missing required field: {field}")
                all_passed = False
            else:
                print_success(f"Required field '{field}' present")

        # 6. Check name matches folder
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()
            expected_name = skill_dir.name
            if skill_name != expected_name:
                print_error(f"Name mismatch: frontmatter='{skill_name}', folder='{expected_name}'")
                all_passed = False
            else:
                print_success(f"Name matches folder: '{skill_name}'")

        # 7. Check description is not empty
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE | re.IGNORECASE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 10:
                print_warning("Description is very short, may need more detail")
            else:
                print_success(f"Description length: {len(desc)} chars")

    # 8. Check _meta.json exists
    if not meta_json.exists():
        print_error("_meta.json not found")
        all_passed = False
    else:
        print_success("_meta.json exists")
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            required_meta = ['id', 'version']
            for field in required_meta:
                if field not in meta:
                    print_error(f"Missing _meta.json field: {field}")
                    all_passed = False
                else:
                    print_success(f"_meta.json field '{field}': {meta[field]}")
        except json.JSONDecodeError as e:
            print_error(f"_meta.json is invalid JSON: {e}")
            all_passed = False

    # 9. Check references directory and files
    if references_dir.exists():
        ref_files = list(references_dir.glob("*"))
        if ref_files:
            print_success(f"References directory has {len(ref_files)} file(s)")
            for rf in ref_files:
                print_info(f"  - {rf.name}")
        else:
            print_warning("References directory is empty")
    else:
        print_info("No references directory (optional)")

    # 10. Check for forbidden patterns
    forbidden_patterns = [
        (r'^# .+', "Markdown title before frontmatter"),
    ]

    lines = content.split('\n')
    for i, line in enumerate(lines[:10], 1):
        if line.startswith('# ') and i > 1:
            print_error(f"Line {i}: Markdown title found before frontmatter end")
            all_passed = False
            break

    # 11. Validate description has trigger phrases
    if desc_match:
        desc = desc_match.group(1)
        if '触发' not in desc and 'trigger' not in desc.lower():
            print_warning("Description should include trigger phrases for proper routing")

    # Summary
    print(f"\n{Colors.BOLD}{'='*50}{Colors.END}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED{Colors.END}")
        return False


def main():
    if len(sys.argv) < 2:
        # Default to current skill directory
        skill_path = "/workspace/temp-skills/ppt-slides-generator"
    else:
        skill_path = sys.argv[1]

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
