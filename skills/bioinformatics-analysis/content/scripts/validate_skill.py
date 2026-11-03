#!/usr/bin/env python3
"""
Bioinformatics Skill Validation Script
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# ============================================================================
# Configuration
# ============================================================================

SKILL_ROOT = Path(__file__).parent.parent
REQUIRED_FILES = [
    "SKILL.md",
    "_meta.json"
]

REQUIRED_REFS = [
    "references/deseq2_tutorial.R",
    "references/deseq2_python_implementation.py",
    "references/sci_color_palettes.R",
    "references/plotting_templates/README.md"
]

# ============================================================================
# Validation Functions
# ============================================================================

def validate_frontmatter(skill_md_path: Path) -> Tuple[bool, List[str]]:
    """Validate SKILL.md frontmatter format"""
    errors = []

    content = skill_md_path.read_text()

    # Check if frontmatter starts at first line
    if not content.startswith('---'):
        errors.append("SKILL.md must start with '---' (frontmatter delimiter)")
        return False, errors

    # Parse frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Missing closing '---' for frontmatter")
        return False, errors

    frontmatter = '\n'.join(lines[1:frontmatter_end])

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:\s*.+$'
        if not re.search(pattern, frontmatter, re.MULTILINE):
            errors.append(f"Missing required field: '{field}' in frontmatter")

    # Check name format
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"'name' should be lowercase with hyphens only: '{name}'")
        if len(name) > 64:
            errors.append(f"'name' should be <= 64 characters: current length = {len(name)}")

    # Check description trigger phrases
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("'description' should be descriptive (>= 20 characters)")
        if not re.search(r'(?:when|if|use)[:\s]', desc, re.IGNORECASE):
            errors.append("'description' should contain trigger phrases (e.g., 'Use when...')")

    success = len(errors) == 0
    return success, errors


def validate_meta_json(meta_path: Path) -> Tuple[bool, List[str]]:
    """Validate _meta.json file"""
    errors = []

    import json

    try:
        content = meta_path.read_text()
        data = json.loads(content)

        # Check required fields
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field in _meta.json: '{field}'")

        # Check version format
        if 'version' in data:
            version = data['version']
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                errors.append(f"'version' should be semantic format (e.g., 1.0.0): '{version}'")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")
    except Exception as e:
        errors.append(f"Error reading _meta.json: {e}")

    success = len(errors) == 0
    return success, errors


def validate_directory_structure() -> Tuple[bool, List[str]]:
    """Validate directory structure"""
    errors = []

    # Check root files
    for file in REQUIRED_FILES:
        path = SKILL_ROOT / file
        if not path.exists():
            errors.append(f"Missing required file: {file}")

    # Check references directory
    ref_dir = SKILL_ROOT / "references"
    if not ref_dir.exists():
        errors.append("Missing 'references' directory")
    else:
        for ref in REQUIRED_REFS:
            path = SKILL_ROOT / ref
            if not path.exists():
                errors.append(f"Missing reference file: {ref}")

    # Check scripts directory
    scripts_dir = SKILL_ROOT / "scripts"
    if not scripts_dir.exists():
        errors.append("Missing 'scripts' directory")

    success = len(errors) == 0
    return success, errors


def validate_code_quality() -> Tuple[bool, List[str]]:
    """Validate code quality"""
    errors = []

    # Check R code
    r_files = list(SKILL_ROOT.glob("references/*.R"))
    for r_file in r_files:
        content = r_file.read_text()

        # Check for comments
        if not re.search(r'#.*(?:author|author|version|date|description)', content, re.IGNORECASE):
            errors.append(f"Warning: {r_file.name} - Missing header comments")

        # Check function definitions
        if 'function' in content:
            functions = re.findall(r'(?:function|<-)\s*(\w+)', content)
            for func in functions:
                if not re.search(rf'#\'.*\b{func}\b', content):
                    errors.append(f"Warning: {r_file.name} - Function '{func}' may lack documentation")

    # Check Python code
    py_files = list(SKILL_ROOT.glob("references/*.py"))
    for py_file in py_files:
        content = py_file.read_text()

        # Check docstring
        if not re.search(r'""".*?"""', content, re.DOTALL):
            errors.append(f"Warning: {py_file.name} - Missing module docstring")

        # Check function docstrings
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        for func in functions:
            if not re.search(rf'def\s+{func}\s*\([^)]*\)[^:]*:\s*"""', content, re.DOTALL):
                errors.append(f"Warning: {py_file.name} - Function '{func}' may lack docstring")

    success = len(errors) == 0 or all('Warning' in e for e in errors)
    return True, errors


def validate_path_naming() -> Tuple[bool, List[str]]:
    """Validate that paths and naming only contain English"""
    errors = []

    # Check all file paths
    for path in SKILL_ROOT.rglob("*"):
        if path.is_file():
            # Check path
            path_str = str(path)
            if any(ord(c) > 127 for c in path_str):
                errors.append(f"Non-ASCII characters in path: {path_str}")

            # Check filename
            if path.name and any(ord(c) > 127 for c in path.name):
                errors.append(f"Non-ASCII characters in filename: {path.name}")

    # Check meta.json description
    meta_path = SKILL_ROOT / "_meta.json"
    if meta_path.exists():
        import json
        try:
            data = json.loads(meta_path.read_text())
            for key, value in data.items():
                if isinstance(value, str) and any(ord(c) > 127 for c in value):
                    errors.append(f"Non-ASCII in _meta.json field '{key}'")
        except:
            pass

    success = len(errors) == 0
    return success, errors


# ============================================================================
# Main Validation
# ============================================================================

def run_validation() -> bool:
    """Run complete validation"""
    print("=" * 60)
    print("Bioinformatics Skill Validation")
    print("=" * 60)
    print()

    all_passed = True
    results = []

    # 1. Frontmatter validation
    print("Check 1: Frontmatter format...")
    skill_md = SKILL_ROOT / "SKILL.md"
    passed, errors = validate_frontmatter(skill_md)
    if passed:
        print("   PASS")
    else:
        print("   FAIL")
        for e in errors:
            print(f"      {e}")
        all_passed = False
    print()

    # 2. Meta JSON validation
    print("Check 2: _meta.json format...")
    meta_path = SKILL_ROOT / "_meta.json"
    passed, errors = validate_meta_json(meta_path)
    if passed:
        print("   PASS")
    else:
        print("   FAIL")
        for e in errors:
            print(f"      {e}")
        all_passed = False
    print()

    # 3. Directory structure validation
    print("Check 3: Directory structure...")
    passed, errors = validate_directory_structure()
    if passed:
        print("   PASS")
    else:
        print("   FAIL")
        for e in errors:
            print(f"      {e}")
        all_passed = False
    print()

    # 4. Code quality validation
    print("Check 4: Code quality...")
    passed, errors = validate_code_quality()
    if passed:
        print("   PASS")
    else:
        print("   PASS with warnings")
        for e in errors:
            print(f"      {e}")
    print()

    # 5. Path naming validation
    print("Check 5: Path and naming...")
    passed, errors = validate_path_naming()
    if passed:
        print("   PASS")
    else:
        print("   FAIL")
        for e in errors:
            print(f"      {e}")
        all_passed = False
    print()

    # Summary
    print("=" * 60)
    if all_passed:
        print("All validations passed! Skill is ready.")
    else:
        print("Some validations failed. Please fix the issues above.")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
