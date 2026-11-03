#!/usr/bin/env python3
"""
Quick validation script for video-soundtrack skill
Validates SKILL.md frontmatter, _meta.json, and structure
"""

import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def validate_frontmatter():
    """Validate SKILL.md frontmatter"""
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        print(f"{RED}✗ SKILL.md not found{RESET}")
        return False
    
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check frontmatter starts at line 0
    if not content.startswith('---'):
        print(f"{RED}✗ SKILL.md must start with --- (frontmatter delimiter){RESET}")
        return False
    
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        print(f"{RED}✗ Invalid frontmatter format{RESET}")
        return False
    
    fm_lines = match.group(1).split('\n')
    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip()
    
    # Check required fields
    required = ['name', 'description']
    missing = [f for f in required if f not in fm_dict]
    if missing:
        print(f"{RED}✗ Missing required frontmatter fields: {', '.join(missing)}{RESET}")
        return False
    
    # Validate name format (hyphen-case)
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', fm_dict['name']):
        print(f"{YELLOW}⚠ name should be hyphen-case (e.g., 'video-soundtrack'){RESET}")
    
    # Validate description
    if len(fm_dict['description']) < 20:
        print(f"{YELLOW}⚠ description should be at least 20 characters{RESET}")
    
    # Check for trigger phrases
    trigger_keywords = ['配乐', '音乐', 'BGM', '背景音乐', 'soundtrack', 'background music', 'video']
    has_trigger = any(kw.lower() in fm_dict['description'].lower() for kw in trigger_keywords)
    if not has_trigger:
        print(f"{YELLOW}⚠ description should include trigger keywords for routing{RESET}")
    
    print(f"{GREEN}✓ Frontmatter validation passed{RESET}")
    return True

def validate_meta():
    """Validate _meta.json"""
    meta_file = SKILL_DIR / "_meta.json"
    if not meta_file.exists():
        print(f"{RED}✗ _meta.json not found{RESET}")
        return False
    
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    required = ['id', 'version']
    missing = [f for f in required if f not in meta]
    if missing:
        print(f"{RED}✗ Missing required _meta.json fields: {', '.join(missing)}{RESET}")
        return False
    
    # Validate id is integer
    if not isinstance(meta['id'], int):
        print(f"{RED}✗ 'id' must be an integer{RESET}")
        return False
    
    # Validate version format (semver)
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        print(f"{YELLOW}⚠ version should follow semantic versioning (e.g., '1.0.0'){RESET}")
    
    print(f"{GREEN}✓ _meta.json validation passed{RESET}")
    return True

def validate_structure():
    """Validate directory structure"""
    required_dirs = ['scripts', 'references']
    for d in required_dirs:
        if not (SKILL_DIR / d).is_dir():
            print(f"{YELLOW}⚠ Optional directory '{d}' not found (optional){RESET}")
    
    print(f"{GREEN}✓ Structure validation passed{RESET}")
    return True

def main():
    print("=" * 50)
    print("Video Soundtrack Skill Validation")
    print("=" * 50)
    
    results = []
    results.append(validate_frontmatter())
    results.append(validate_meta())
    results.append(validate_structure())
    
    print("=" * 50)
    if all(results):
        print(f"{GREEN}✓ All validations passed!{RESET}")
        return 0
    else:
        print(f"{RED}✗ Some validations failed{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
