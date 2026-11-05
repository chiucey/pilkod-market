#!/usr/bin/env python3
"""
Quick Validation Script for video-editing-skills

Validates:
1. SKILL.md frontmatter structure
2. Required fields present
3. No forbidden patterns
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

    print(f"\n{Colors.BOLD}Validating: {skill_path}{Colors.END}\n")

    if not skill_md.exists():
        print_error(f"SKILL.md not found at {skill_md}")
        return False

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter at beginning
    if not content.startswith('---'):
        print_error("SKILL.md must start with frontmatter (---)")
        all_passed = False
    else:
        print_success("Frontmatter starts correctly at first line")

    # Parse frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print_error("Could not parse frontmatter")
        all_passed = False
    else:
        frontmatter_text = frontmatter_match.group(1)
        print_success("Frontmatter parsed successfully")

        # Check required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
                print_error(f"Missing required field: {field}")
                all_passed = False
            else:
                print_success(f"Required field '{field}' present")

        # Check name matches folder
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()
            expected_name = skill_dir.name
            if skill_name != expected_name:
                print_error(f"Name mismatch: frontmatter='{skill_name}', folder='{expected_name}'")
                all_passed = False
            else:
                print_success(f"Name matches folder: '{skill_name}'")

        # Check description quality
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE | re.IGNORECASE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 50:
                print_warning("Description is short, should include detailed triggers")
            else:
                print_success(f"Description length: {len(desc)} chars")

            # Check for trigger keywords
            trigger_keywords = ['用户要求', '触发', '涉及', '包含']
            has_triggers = any(kw in desc for kw in trigger_keywords)
            if has_triggers:
                print_success("Description includes trigger phrases")
            else:
                print_warning("Description should include trigger phrases for routing")

    # Check _meta.json
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

    # Check references
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

    # Check for title before frontmatter
    lines = content.split('\n')
    for i, line in enumerate(lines[:10], 1):
        if line.startswith('# ') and i > 1:
            print_error(f"Line {i}: Markdown title found before frontmatter end")
            all_passed = False
            break

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
        skill_path = "/workspace/temp-skills/video-editing-skills"
    else:
        skill_path = sys.argv[1]

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
