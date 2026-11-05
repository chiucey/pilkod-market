#!/usr/bin/env python3
"""
Skill Validator - validates a skill directory before packaging.
Checks SKILL.md frontmatter structure, required fields, and constraints.
"""

import sys
import re
import yaml
from pathlib import Path


ALLOWED_FRONTMATTER_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}


def validate_skill(skill_path):
    skill_path = Path(skill_path)

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith('---'):
        return False, "No YAML frontmatter found — SKILL.md must start with ---"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter — closing --- not found"

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        return False, (
            f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )

    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = str(frontmatter['name']).strip()
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' must be kebab-case (lowercase letters, digits, hyphens only)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or have consecutive hyphens"
    if len(name) > 64:
        return False, f"Name too long: {len(name)} chars (max 64)"

    description = str(frontmatter['description']).strip()
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description too long: {len(description)} chars (max 1024)"

    body = content[match.end():].strip()
    if len(body) < 50:
        return False, "SKILL.md body is too short — add instructions"

    return True, f"✅ Skill '{name}' is valid!"


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_skill.py <skill-directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
