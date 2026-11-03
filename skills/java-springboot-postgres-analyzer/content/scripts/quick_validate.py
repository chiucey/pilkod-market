#!/usr/bin/env python3
"""
Skill Validation Script for Java Spring Boot PostgreSQL Analyzer
Validates the skill structure, frontmatter, and content quality.
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate the skill structure and content."""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # Read SKILL.md content
    content = skill_md.read_text(encoding='utf-8')

    # Validate frontmatter (YAML block at the start)
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid YAML frontmatter format")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # Check required frontmatter fields
    if not re.search(r'^name:\s*.+$', frontmatter, re.MULTILINE):
        errors.append("Missing 'name' field in frontmatter")

    if not re.search(r'^description:\s*.+$', frontmatter, re.MULTILINE):
        errors.append("Missing 'description' field in frontmatter")

    # Check description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1)
        if len(description) < 50:
            warnings.append("Description is very short, may not have enough trigger phrases")

    # Check _meta.json exists
    meta_json = skill_dir / "_meta.json"
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
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is invalid JSON: {e}")

    # Check references directory
    references_dir = skill_dir / "references"
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if len(ref_files) < 2:
            warnings.append(f"Only {len(ref_files)} reference files found, consider adding more")

    # Check skill name matches folder name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        skill_name = name_match.group(1).strip()
        expected_name = skill_dir.name
        if skill_name != expected_name:
            errors.append(f"Skill name '{skill_name}' does not match folder name '{expected_name}'")

    # Validate markdown structure
    if '# ' not in content:
        warnings.append("SKILL.md should have a main title heading (#)")

    # Check for code examples
    code_blocks = re.findall(r'```[\w]*', content)
    if len(code_blocks) < 5:
        warnings.append(f"Only {len(code_blocks)} code blocks found, consider adding more code examples")

    return len(errors) == 0, errors + warnings

def main():
    skill_dir = Path(__file__).parent.parent

    print(f"Validating skill at: {skill_dir}")
    print("-" * 50)

    is_valid, messages = validate_skill(skill_dir)

    for msg in messages:
        prefix = "ERROR" if msg.startswith("ERROR:") else "WARNING" if "Warning" in msg else "INFO"
        print(f"  [{prefix}] {msg}")

    print("-" * 50)

    if is_valid:
        print("✓ Validation passed!")
        return 0
    else:
        print("✗ Validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
