#!/usr/bin/env python3
"""
Quick Validation Script for OpenClaw + RunningHub Connector Skill

Validates:
1. SKILL.md exists and has valid frontmatter
2. _meta.json exists and has valid id/version
3. Required files are present
4. No secrets or credentials in files
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(content: str) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter"""
    pattern = r'^---\n(.*?)\n---'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return False, "Frontmatter not found or invalid format"

    frontmatter = match.group(1)

    # Check required fields
    if 'name:' not in frontmatter:
        return False, "Missing 'name' field in frontmatter"

    if 'description:' not in frontmatter:
        return False, "Missing 'description' field in frontmatter"

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            return False, f"Invalid name format: '{name}'. Use hyphen-case."

    return True, "OK"


def validate_meta_json(content: str) -> tuple[bool, str]:
    """Validate _meta.json"""
    import json

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    if 'id' not in data:
        return False, "Missing 'id' field"

    if 'version' not in data:
        return False, "Missing 'version' field"

    # Check id is a valid format (should be integer or string)
    if not isinstance(data['id'], (int, str)):
        return False, f"'id' should be integer or string, got {type(data['id'])}"

    # Check version format
    version = data['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"Invalid version format: '{version}'. Use semver (e.g., 1.0.0)"

    return True, "OK"


def check_for_secrets(filepath: str, content: str) -> list[str]:
    """Check for potential secrets or credentials in files"""
    issues = []

    # Patterns that might indicate secrets
    secret_patterns = [
        (r'api[_-]?key["\']?\s*[:=]\s*["\'][A-Za-z0-9_-]{20,}', 'Potential API key'),
        (r'password["\']?\s*[:=]\s*["\'][^"\']{8,}', 'Potential password'),
        (r'secret["\']?\s*[:=]\s*["\'][A-Za-z0-9_-]{20,}', 'Potential secret'),
        (r'bearer\s+[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'Potential JWT token'),
    ]

    for pattern, description in secret_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{filepath}: {description}")

    return issues


def validate_skill_directory(base_path: str) -> tuple[bool, list[str]]:
    """Validate the entire skill directory"""
    errors = []
    warnings = []

    base = Path(base_path)

    # Check required files exist
    required_files = [
        'SKILL.md',
        '_meta.json'
    ]

    for file in required_files:
        filepath = base / file
        if not filepath.exists():
            errors.append(f"Missing required file: {file}")

    # Validate SKILL.md
    skill_md = base / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')

        # Check frontmatter
        valid, msg = validate_frontmatter(content)
        if not valid:
            errors.append(f"SKILL.md: {msg}")

        # Check for title before frontmatter
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            errors.append("SKILL.md: Cannot have markdown title before frontmatter")

        # Check for secrets
        issues = check_for_secrets('SKILL.md', content)
        if issues:
            warnings.extend(issues)

    # Validate _meta.json
    meta_json = base / '_meta.json'
    if meta_json.exists():
        content = meta_json.read_text(encoding='utf-8')
        valid, msg = validate_meta_json(content)
        if not valid:
            errors.append(f"_meta.json: {msg}")

    # Check directory structure
    for subdir in ['scripts', 'references', 'assets']:
        dirpath = base / subdir
        if dirpath.exists() and not any(dirpath.iterdir()):
            warnings.append(f"Empty directory: {subdir}/")

    return len(errors) == 0, errors + warnings


def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Validating skill at: {skill_dir}")
    print("-" * 50)

    valid, issues = validate_skill_directory(skill_dir)

    if issues:
        print("\nIssues found:")
        for issue in issues:
            prefix = "⚠️  " if "Empty" in issue or "Potential" in issue else "✗ "
            print(f"  {prefix}{issue}")

    if valid:
        print("\n✓ Validation passed!")
        return 0
    else:
        print("\n✗ Validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
