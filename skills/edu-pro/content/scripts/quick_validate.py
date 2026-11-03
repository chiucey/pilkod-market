#!/usr/bin/env python3
"""
EduPro Quick Validation Script
快速验证脚本 - 检查技能结构完整性

Usage:
    python quick_validate.py [skill_path]
"""

import os
import sys
import json
import re
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def validate_frontmatter(skill_path):
    """验证 SKILL.md 的 frontmatter"""
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        print_error(f"SKILL.md not found at {skill_md}")
        return False
    
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file starts with ---
    if not content.strip().startswith('---'):
        print_error("SKILL.md must start with --- (frontmatter delimiter)")
        return False
    
    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print_error("Cannot parse frontmatter from SKILL.md")
        return False
    
    try:
        frontmatter = {}
        for line in frontmatter_match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        # Check required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                print_error(f"Missing required frontmatter field: {field}")
                return False
        
        # Validate name format (hyphen-case, English only)
        name = frontmatter.get('name', '')
        if not re.match(r'^[a-z0-9-]+$', name):
            print_error(f"Name must be hyphen-case and English only: '{name}'")
            return False
        
        # Validate name length
        if len(name) > 64:
            print_error(f"Name must be <= 64 characters: '{name}' ({len(name)} chars)")
            return False
        
        # Validate description length
        desc = frontmatter.get('description', '')
        if len(desc) < 10:
            print_error(f"Description too short (< 10 chars): '{desc}'")
            return False
        
        print_success(f"Frontmatter valid: name={name}")
        return True
        
    except Exception as e:
        print_error(f"Error parsing frontmatter: {e}")
        return False

def validate_meta_json(skill_path):
    """验证 _meta.json"""
    meta_json = skill_path / "_meta.json"
    
    if not meta_json.exists():
        print_error("_meta.json not found")
        return False
    
    try:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # Check required fields
        if 'id' not in meta:
            print_error("Missing 'id' in _meta.json")
            return False
        
        if 'version' not in meta:
            print_error("Missing 'version' in _meta.json")
            return False
        
        # Validate version format
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            print_error(f"Invalid version format: {version} (expected x.y.z)")
            return False
        
        print_success(f"Meta valid: id={meta['id']}, version={version}")
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in _meta.json: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading _meta.json: {e}")
        return False

def validate_directory_structure(skill_path):
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']
    
    # Check scripts directory
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        print_success("scripts/ directory exists")
        
        # Check for required scripts
        required_scripts = ['quick_validate.py', 'package_skill.py']
        for script in required_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                print_success(f"  └── {script} found")
            else:
                print_warning(f"  └── {script} not found (optional)")
    
    # Check references directory
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        print_success("references/ directory exists")
        for md_file in refs_dir.glob("*.md"):
            print_success(f"  └── {md_file.name} found")
    
    # Check assets directory
    assets_dir = skill_path / "assets"
    if assets_dir.exists():
        print_success("assets/ directory exists")
        for file in assets_dir.rglob("*"):
            if file.is_file():
                print_success(f"  └── {file.name} found")
    
    return True

def validate_file_naming(skill_path):
    """验证文件命名（仅英文）"""
    issues = []
    
    # Check directory name
    dir_name = skill_path.name
    if not re.match(r'^[a-z0-9-]+$', dir_name):
        issues.append(f"Directory name not English: {dir_name}")
    
    # Check all files
    for file in skill_path.rglob("*"):
        if file.is_file():
            name = file.name
            if not re.match(r'^[a-zA-Z0-9_.-]+$', name):
                issues.append(f"Non-English filename: {name}")
    
    if issues:
        for issue in issues:
            print_error(issue)
        return False
    
    print_success("All file/directory names are English")
    return True

def validate_skill_md_content(skill_path):
    """验证 SKILL.md 内容完整性"""
    skill_md = skill_path / "SKILL.md"
    
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required sections
    required_sections = [
        ('# ', 'Heading (skill title)'),
        ('触发', 'Trigger keywords section'),
        ('功能', 'Function modules section'),
        ('变现', 'Monetization section'),
    ]
    
    missing = []
    for pattern, desc in required_sections:
        if pattern not in content:
            missing.append(f"{desc} ({pattern})")
    
    if missing:
        for m in missing:
            print_warning(f"Missing section: {m}")
    else:
        print_success("SKILL.md content structure complete")
    
    return True

def main():
    print(f"\n{Colors.BOLD}🔍 EduPro Skill Quick Validation{Colors.RESET}\n")
    
    # Get skill path from argument or use default
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        # Default to current directory
        skill_path = Path(__file__).parent.parent
    
    print_info(f"Validating skill at: {skill_path}\n")
    
    # Run validations
    results = []
    
    print(f"{Colors.BOLD}1. Checking Frontmatter...{Colors.RESET}")
    results.append(validate_frontmatter(skill_path))
    
    print(f"\n{Colors.BOLD}2. Checking _meta.json...{Colors.RESET}")
    results.append(validate_meta_json(skill_path))
    
    print(f"\n{Colors.BOLD}3. Checking Directory Structure...{Colors.RESET}")
    results.append(validate_directory_structure(skill_path))
    
    print(f"\n{Colors.BOLD}4. Checking File Naming...{Colors.RESET}")
    results.append(validate_file_naming(skill_path))
    
    print(f"\n{Colors.BOLD}5. Checking SKILL.md Content...{Colors.RESET}")
    results.append(validate_skill_md_content(skill_path))
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print_success(f"All checks passed! ({passed}/{total})")
        return 0
    else:
        print_error(f"Some checks failed! ({passed}/{total} passed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())