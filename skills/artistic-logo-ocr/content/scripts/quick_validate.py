#!/usr/bin/env python3
"""
艺术字Logo OCR Skill 验证脚本
Quick validation script for Artistic Logo OCR Skill
"""

import os
import json
import sys

def validate_skill_structure(skill_path: str) -> tuple[bool, list]:
    """验证skill目录结构"""
    errors = []
    required_files = ['SKILL.md', '_meta.json']
    required_dirs = ['scripts', 'references']

    # 检查顶层文件
    for f in required_files:
        path = os.path.join(skill_path, f)
        if not os.path.exists(path):
            errors.append(f"Missing required file: {f}")

    # 检查目录
    for d in required_dirs:
        path = os.path.join(skill_path, d)
        if not os.path.isdir(path):
            errors.append(f"Missing required directory: {d}")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list]:
    """验证_meta.json"""
    errors = []
    meta_path = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_path):
        errors.append("_meta.json not found")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        required_fields = ['id', 'version', 'name']
        for field in required_fields:
            if field not in meta:
                errors.append(f"Missing required field in _meta.json: {field}")

        # 检查id是否为整数
        if 'id' in meta and not isinstance(meta['id'], int):
            errors.append("Field 'id' must be an integer")

        # 检查version格式
        if 'version' in meta:
            parts = meta['version'].split('.')
            if len(parts) != 3:
                errors.append("Version must follow semantic versioning (x.y.z)")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors


def validate_skill_md(skill_path: str) -> tuple[bool, list]:
    """验证SKILL.md"""
    errors = []
    skill_md_path = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md not found")
        return False, errors

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否存在
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter not properly closed with ---")
        return False, errors

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if f"{field}:" not in frontmatter_text:
            errors.append(f"Missing required frontmatter field: {field}")

    return len(errors) == 0, errors


def validate_scripts(skill_path: str) -> tuple[bool, list]:
    """验证脚本文件"""
    errors = []
    scripts_dir = os.path.join(skill_path, 'scripts')

    if os.path.isdir(scripts_dir):
        # 检查主脚本
        main_script = os.path.join(scripts_dir, 'artistic_logo_ocr.py')
        if not os.path.exists(main_script):
            errors.append("Missing main script: artistic_logo_ocr.py")

        # 检查是否有shebang
        if os.path.exists(main_script):
            with open(main_script, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if not first_line.startswith('#!'):
                    errors.append("Main script should have a shebang line")

    return len(errors) == 0, errors


def run_validation(skill_path: str) -> bool:
    """运行所有验证"""
    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    all_passed = True

    # 结构验证
    print("\n[1/4] Checking structure...")
    passed, errors = validate_skill_structure(skill_path)
    if passed:
        print("    ✓ Structure OK")
    else:
        print("    ✗ Structure errors:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # Meta JSON验证
    print("\n[2/4] Checking _meta.json...")
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("    ✓ _meta.json OK")
    else:
        print("    ✗ _meta.json errors:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # SKILL.md验证
    print("\n[3/4] Checking SKILL.md...")
    passed, errors = validate_skill_md(skill_path)
    if passed:
        print("    ✓ SKILL.md OK")
    else:
        print("    ✗ SKILL.md errors:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # 脚本验证
    print("\n[4/4] Checking scripts...")
    passed, errors = validate_scripts(skill_path)
    if passed:
        print("    ✓ Scripts OK")
    else:
        print("    ✗ Script errors:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return True
    else:
        print("✗ Some validations failed.")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = '.'

    success = run_validation(skill_path)
    sys.exit(0 if success else 1)
