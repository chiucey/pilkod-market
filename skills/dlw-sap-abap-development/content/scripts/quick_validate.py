#!/usr/bin/env python3
"""
Quick validation script for SAP ABAP Development skill.
Validates structure, frontmatter, and file integrity.
"""

import os
import sys
import json
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and content."""
    skill_dir = Path(skill_path)
    errors = []
    warnings = []

    # Check required files exist
    if not (skill_dir / "SKILL.md").exists():
        errors.append("SKILL.md is missing")
    if not (skill_dir / "_meta.json").exists():
        errors.append("_meta.json is missing")

    # Validate _meta.json
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Validate SKILL.md frontmatter
    skill_md_path = skill_dir / "SKILL.md"
    if skill_md_path.exists():
        with open(skill_md_path, 'r') as f:
            content = f.read()

        # Check frontmatter starts at line 0
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        # Extract and validate frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter = parts[1]
                if 'name:' not in frontmatter:
                    errors.append("Frontmatter missing 'name:' field")
                if 'description:' not in frontmatter:
                    errors.append("Frontmatter missing 'description:' field")

                # Check name matches folder
                import re
                name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
                if name_match:
                    expected_name = skill_dir.name
                    actual_name = name_match.group(1).strip()
                    if actual_name != expected_name:
                        warnings.append(
                            f"Frontmatter name '{actual_name}' doesn't match folder '{expected_name}'"
                        )
            else:
                errors.append("Frontmatter malformed - missing closing ---")
        else:
            errors.append("SKILL.md must have YAML frontmatter at the start")

    # Check references directory exists and has content
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        warnings.append("references/ directory is missing")
    elif not any(refs_dir.iterdir()):
        warnings.append("references/ directory is empty")

    # Print results
    print(f"\n{'='*60}")
    print(f"Validation Results for: {skill_dir.name}")
    print(f"{'='*60}")

    if errors:
        print(f"\n[X] ERRORS ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")

    if warnings:
        print(f"\n[!] WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")

    if not errors and not warnings:
        print("\n[OK] All validations passed!")

    print(f"{'='*60}\n")

    return len(errors) == 0

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
