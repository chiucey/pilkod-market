#!/usr/bin/env python3
"""
Quick validation script for Chem-Converter skill
Run this to verify the skill structure and code quality
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_frontmatter(skill_dir: Path) -> dict:
    """Validate SKILL.md frontmatter"""
    errors = []
    warnings = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return {"valid": False, "errors": errors, "warnings": warnings}

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter starts at line 1
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        errors.append("Frontmatter must start with '---' at line 1")

    # Find end of frontmatter
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter not closed with '---'")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Parse frontmatter
    frontmatter_lines = '\n'.join(lines[1:frontmatter_end])
    fm = {}
    for line in frontmatter_lines.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm[key.strip()] = value.strip()

    # Required fields
    if 'name' not in fm:
        errors.append("Missing required field: name")
    elif not re.match(r'^[a-z0-9-]+$', fm['name']):
        errors.append("name must be lowercase with hyphens only")

    if 'description' not in fm:
        errors.append("Missing required field: description")

    # Check no markdown before frontmatter
    for i, line in enumerate(lines[:frontmatter_end]):
        if line.strip().startswith('#'):
            errors.append(f"Markdown heading found before frontmatter at line {i+1}")

    # Check name matches directory
    expected_name = skill_dir.name
    if 'name' in fm and fm['name'] != expected_name:
        warnings.append(f"name '{fm['name']}' doesn't match directory '{expected_name}'")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "frontmatter": fm
    }


def validate_meta(skill_dir: Path) -> dict:
    """Validate _meta.json"""
    errors = []
    warnings = []

    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        errors.append("_meta.json not found")
        return {"valid": False, "errors": errors, "warnings": warnings}

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is not valid JSON: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    if 'id' not in meta:
        errors.append("Missing required field: id")
    elif not str(meta['id']).isdigit():
        errors.append("id must be a numeric string")

    if 'version' not in meta:
        errors.append("Missing required field: version")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        warnings.append("version should follow semantic versioning (e.g., 1.0.0)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "meta": meta
    }


def validate_structure(skill_dir: Path) -> dict:
    """Validate directory structure"""
    errors = []
    warnings = []

    # Check main module exists
    module_dir = skill_dir / "chem_converter"
    if not module_dir.exists():
        errors.append("chem_converter module not found")
    else:
        init_file = module_dir / "__init__.py"
        if not init_file.exists():
            warnings.append("chem_converter/__init__.py missing")
        converter_file = module_dir / "converter.py"
        if not converter_file.exists():
            warnings.append("chem_converter/converter.py missing")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_python_code(skill_dir: Path) -> dict:
    """Basic Python syntax validation"""
    errors = []
    warnings = []

    module_dir = skill_dir / "chem_converter"
    if not module_dir.exists():
        return {"valid": True, "errors": [], "warnings": []}

    for py_file in module_dir.glob("*.py"):
        try:
            compile(py_file.read_text(encoding='utf-8'), str(py_file), 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error in {py_file.name}: {e}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def main():
    skill_dir = Path("/workspace/temp-skills/smiles-inchi-key-converter")

    print("=" * 60)
    print("Smiles-InChI-Key-Converter Skill Validation")
    print("=" * 60)
    print()

    results = {}

    # Run all validations
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta),
        ("Structure", validate_structure),
        ("Python Code", validate_python_code),
    ]

    all_valid = True
    for name, validator in validations:
        result = validator(skill_dir)
        results[name] = result

        status = "PASS" if result["valid"] else "FAIL"
        if not result["valid"]:
            all_valid = False

        print(f"[{status}] {name}")

        for error in result.get("errors", []):
            print(f"      ERROR: {error}")

        for warning in result.get("warnings", []):
            print(f"      WARN:  {warning}")

        print()

    # Summary
    print("=" * 60)
    if all_valid:
        print("Result: ALL CHECKS PASSED")
        print()
        print("Next steps:")
        print("  1. Review the skill at: /workspace/temp-skills/chem-converter")
        print("  2. When ready, confirm to package")
    else:
        print("Result: VALIDATION FAILED")
        print("Please fix the errors above before packaging")

    print("=" * 60)
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
