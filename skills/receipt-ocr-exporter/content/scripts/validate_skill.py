#!/usr/bin/env python3
"""
Validation script for receipt-ocr-exporter skill
"""

import os
import json
import re
from pathlib import Path

def validate_frontmatter(file_path):
    """Check frontmatter format"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with ---
    if not content.startswith('---'):
        return False, "SKILL.md must start with frontmatter (---)"

    # Check frontmatter closing
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(parts[1])
    except:
        import yaml
        try:
            frontmatter = yaml.safe_load(parts[1])
        except:
            return False, "Invalid YAML in frontmatter"

    # Check required fields
    required = ['name', 'description']
    for field in required:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    return True, "Valid"

def check_english_content(file_path):
    """Check for non-English characters in code files"""
    issues = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Check for CJK characters
        if re.search(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', line):
            issues.append(f"Line {i}: Contains CJK/Full-width characters")

    return issues

def main():
    skill_dir = Path(__file__).parent.parent

    print("=" * 50)
    print("Receipt OCR Exporter - Validation Report")
    print("=" * 50)

    # Check SKILL.md
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists():
        valid, msg = validate_frontmatter(skill_file)
        print(f"\n[{'PASS' if valid else 'FAIL'}] SKILL.md frontmatter: {msg}")
    else:
        print("\n[FAIL] SKILL.md not found")

    # Check _meta.json
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r') as f:
            meta = json.load(f)

        has_id = 'id' in meta
        has_version = 'version' in meta

        print(f"[{'PASS' if has_id else 'FAIL'}] _meta.json has 'id' field")
        print(f"[{'PASS' if has_version else 'FAIL'}] _meta.json has 'version' field")
    else:
        print("\n[FAIL] _meta.json not found")

    # Check for non-English content in code files
    print("\n--- English Content Check ---")
    code_files = [
        skill_dir / "references" / "app.py",
        skill_dir / "references" / "requirements.txt",
    ]

    all_pass = True
    for file_path in code_files:
        if file_path.exists():
            issues = check_english_content(file_path)
            if issues:
                all_pass = False
                for issue in issues:
                    print(f"[FAIL] {file_path.name}: {issue}")
            else:
                print(f"[PASS] {file_path.name}: No non-English content found")

    # Check directory structure
    print("\n--- Directory Structure ---")
    expected_dirs = ['references', 'scripts']
    for dir_name in expected_dirs:
        path = skill_dir / dir_name
        if path.exists():
            print(f"[PASS] {dir_name}/ directory exists")
        else:
            print(f"[FAIL] {dir_name}/ directory missing")

    print("\n" + "=" * 50)
    print("Validation Complete")
    print("=" * 50)

    return 0 if all_pass else 1

if __name__ == "__main__":
    exit(main())
