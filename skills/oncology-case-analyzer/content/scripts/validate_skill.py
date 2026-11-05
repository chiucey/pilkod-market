#!/usr/bin/env python3
"""
Oncology Case Analyzer Skill - Quality Validator
Validates SKILL.md structure and frontmatter compliance
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path: str) -> dict:
    """Validate SKILL.md frontmatter"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter
    if not content.startswith('---'):
        errors.append("❌ SKILL.md must start with YAML frontmatter (---)")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("❌ Cannot parse YAML frontmatter")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    frontmatter_text = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"❌ Missing required frontmatter field: {field}")

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"❌ name '{name}' should be hyphen-case (lowercase with hyphens)")
        if name != os.path.basename(os.path.dirname(skill_md_path)):
            warnings.append(f"⚠️ name '{name}' should match folder name")

    # Check description
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("❌ description is too short (minimum 20 characters)")
        if not any(keyword in desc.lower() for keyword in ['recist', 'oncology', 'clinical', 'tumor', 'cancer', 'mdt']):
            warnings.append("⚠️ description should include medical/oncology keywords for proper routing")

    # Check for markdown headings before frontmatter
    lines_before = content.split('---')[0]
    if lines_before.strip():
        errors.append("❌ No content should appear before frontmatter (---)")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def validate_structure(skill_md_path: str) -> dict:
    """Validate SKILL.md content structure"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Required output sections
    required_sections = [
        '# 1 患者基本信息',
        '# 2 肿瘤基本情况',
        '# 3 病理与分子检测',
        '# 4 影像学分析',
        '# 5 RECIST评估',
        '# 6 治疗史',
        '# 7 实验室检查',
        '# 8 指标计算',
        '# 9 疾病评估',
        '# 10 临床试验筛选',
        '# 11 MDT总结',
        '# 12 Sponsor Case Brief',
        '# 13 Clinical Development Summary'
    ]

    for section in required_sections:
        if section not in content:
            errors.append(f"❌ Missing required section: {section}")

    # Check for medical rules sections
    medical_sections = [
        'RECIST',
        'TNM',
        '治疗线',
        '贫血分级'
    ]

    for section in medical_sections:
        if section not in content:
            warnings.append(f"⚠️ Missing medical reference: {section}")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def validate_meta(meta_path: str) -> dict:
    """Validate _meta.json"""
    errors = []
    warnings = []

    import json

    if not os.path.exists(meta_path):
        errors.append("❌ _meta.json not found")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    with open(meta_path, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"❌ Invalid JSON in _meta.json: {e}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"❌ Missing required field in _meta.json: {field}")

    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append("❌ version should follow semver format (x.y.z)")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(skill_dir)

    skill_md_path = os.path.join(parent_dir, 'SKILL.md')
    meta_path = os.path.join(parent_dir, '_meta.json')

    print("=" * 60)
    print("Oncology Case Analyzer - Skill Quality Validator")
    print("=" * 60)

    all_valid = True
    all_errors = []
    all_warnings = []

    # Validate frontmatter
    print("\n📋 Frontmatter Validation:")
    fm_result = validate_frontmatter(skill_md_path)
    for error in fm_result['errors']:
        print(f"  {error}")
        all_errors.append(error)
        all_valid = False
    for warning in fm_result['warnings']:
        print(f"  {warning}")
        all_warnings.append(warning)
    if fm_result['valid']:
        print("  ✅ Frontmatter is valid")

    # Validate structure
    print("\n📊 Content Structure Validation:")
    struct_result = validate_structure(skill_md_path)
    for error in struct_result['errors']:
        print(f"  {error}")
        all_errors.append(error)
        all_valid = False
    for warning in struct_result['warnings']:
        print(f"  {warning}")
        all_warnings.append(warning)
    if struct_result['valid']:
        print("  ✅ All required sections present")

    # Validate meta
    print("\n⚙️ Meta File Validation:")
    meta_result = validate_meta(meta_path)
    for error in meta_result['errors']:
        print(f"  {error}")
        all_errors.append(error)
        all_valid = False
    for warning in meta_result['warnings']:
        print(f"  {warning}")
        all_warnings.append(warning)
    if meta_result['valid']:
        print("  ✅ Meta file is valid")

    # Check references
    print("\n📚 References Validation:")
    refs_dir = os.path.join(parent_dir, 'references')
    if os.path.exists(refs_dir):
        ref_files = [f for f in os.listdir(refs_dir) if f.endswith('.md')]
        if ref_files:
            print(f"  ✅ Found {len(ref_files)} reference files")
            for rf in ref_files:
                print(f"     - {rf}")
        else:
            print("  ⚠️ No reference files found")
    else:
        print("  ⚠️ references/ directory not found")

    # Summary
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ VALIDATION PASSED - Skill is ready")
        return 0
    else:
        print("❌ VALIDATION FAILED - Please fix errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())
