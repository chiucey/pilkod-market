#!/usr/bin/env python3
"""
Quick Validation Script for Penetration Testing Skill
Validates SKILL.md frontmatter and structure requirements.
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate penetration testing skill structure and content."""
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False

    # Read SKILL.md content
    content = skill_md.read_text()

    # Check frontmatter is at the start
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid or missing YAML frontmatter")
    else:
        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if 'name:' not in frontmatter:
            errors.append("Frontmatter missing 'name' field")

        if 'description:' not in frontmatter:
            errors.append("Frontmatter missing 'description' field")

        # Validate name format (hyphen-case)
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if ' ' in name:
                errors.append(f"Name should use hyphen-case format, got: '{name}'")

        # Validate description contains trigger phrases
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append("Description seems too short for proper routing")
            if 'when' not in desc.lower() and 'use' not in desc.lower():
                warnings.append("Description should include trigger phrases like 'Use when...'")

    # Check _meta.json exists and is valid
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text())
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    errors.append(f"Version should be semantic (x.y.z), got: {version}")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Check references directory exists with expected files
    references_dir = skill_path / "references"
    expected_refs = [
        'pentest-checklist.md',
        'cvss-calculator.md',
        'report-template.md',
        'tools-usage.md'
    ]

    if not references_dir.exists():
        errors.append("references/ directory not found")
    else:
        for ref in expected_refs:
            ref_path = references_dir / ref
            if not ref_path.exists():
                warnings.append(f"Expected reference file not found: {ref}")

    # Report results
    print("\n" + "=" * 60)
    print("SKILL VALIDATION RESULTS")
    print("=" * 60)

    if errors:
        print("\nERRORS:")
        for err in errors:
            print(f"  [X] {err}")

    if warnings:
        print("\nWARNINGS:")
        for warn in warnings:
            print(f"  [!] {warn}")

    if not errors and not warnings:
        print("\n[+] All validations passed!")
    elif not errors:
        print("\n[*] Validation passed with warnings")
    else:
        print("\n[X] Validation FAILED")
        return False

    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/penetration-testing"
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
