"""
Max-RDT 快速验证脚本

验证技能结构和代码语法
"""

import os
import sys
import re
from pathlib import Path


def validate_skill_structure(base_path: Path) -> tuple[bool, list]:
    """验证技能目录结构"""
    errors = []
    required_files = ['SKILL.md', '_meta.json']
    required_dirs = ['scripts', 'references']

    # 检查必需文件
    for f in required_files:
        if not (base_path / f).exists():
            errors.append(f"Missing required file: {f}")

    # 检查必需目录
    for d in required_dirs:
        if not (base_path / d).is_dir():
            errors.append(f"Missing required directory: {d}")

    return len(errors) == 0, errors


def validate_frontmatter(skill_md_path: Path, base_path: Path) -> tuple[bool, list]:
    """验证SKILL.md的frontmatter"""
    errors = []

    if not skill_md_path.exists():
        errors.append("SKILL.md does not exist")
        return False, errors

    content = skill_md_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # 检查第一行必须是---
    if lines[0].strip() != '---':
        errors.append("SKILL.md must start with --- (YAML frontmatter)")
        return False, errors

    # 找到第二个---
    try:
        end_idx = lines.index('---', 1)
    except ValueError:
        errors.append("Missing closing --- for frontmatter")
        return False, errors

    # 解析frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"Missing required field in frontmatter: {field}")

    # 检查name格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"Invalid name format: '{name_value}' - must be hyphen-case")
        if base_path.name != name_value:
            errors.append(f"Folder name '{base_path.name}' does not match frontmatter name '{name_value}'")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: Path) -> tuple[bool, list]:
    """验证_meta.json"""
    errors = []

    if not meta_path.exists():
        errors.append("_meta.json does not exist")
        return False, errors

    import json
    try:
        content = meta_path.read_text(encoding='utf-8')
        data = json.loads(content)

        # 检查必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field in _meta.json: {field}")

        # 检查version格式
        if 'version' in data:
            if not re.match(r'^\d+\.\d+\.\d+$', data['version']):
                errors.append(f"Invalid version format: {data['version']} - use semver (e.g., 1.0.0)")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors


def validate_python_syntax(scripts_path: Path) -> tuple[bool, list]:
    """验证Python脚本语法"""
    errors = []

    if not scripts_path.exists():
        return True, []  # 没有脚本目录也不算错

    for py_file in scripts_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue

        try:
            content = py_file.read_text(encoding='utf-8')
            compile(content, str(py_file), 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error in {py_file.name}:{e.lineno} - {e.msg}")

    return len(errors) == 0, errors


def validate_paths_english(base_path: Path) -> tuple[bool, list]:
    """验证路径和名称是否为英文"""
    errors = []

    # 检查文件夹名称
    if not re.match(r'^[a-z0-9-]+$', base_path.name):
        errors.append(f"Folder name contains non-English characters: {base_path.name}")

    # 检查SKILL.md中的name字段
    skill_md = base_path / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name_value):
                errors.append(f"name field contains non-English: {name_value}")

    return len(errors) == 0, errors


def main():
    """主验证函数"""
    skill_path = Path(__file__).parent.parent

    print("=" * 50)
    print("Max-RDT Skill Validation")
    print("=" * 50)
    print(f"Path: {skill_path}")
    print()

    all_valid = True
    results = []

    # 1. 目录结构验证
    print("[1/5] Validating skill structure...")
    valid, errors = validate_skill_structure(skill_path)
    if valid:
        print("    ✓ Structure valid")
    else:
        print("    ✗ Structure invalid")
        for e in errors:
            print(f"      - {e}")
        all_valid = False

    # 2. Frontmatter验证
    print("\n[2/5] Validating frontmatter...")
    valid, errors = validate_frontmatter(skill_path / 'SKILL.md', skill_path)
    if valid:
        print("    ✓ Frontmatter valid")
    else:
        print("    ✗ Frontmatter invalid")
        for e in errors:
            print(f"      - {e}")
        all_valid = False

    # 3. Meta JSON验证
    print("\n[3/5] Validating _meta.json...")
    valid, errors = validate_meta_json(skill_path / '_meta.json')
    if valid:
        print("    ✓ _meta.json valid")
    else:
        print("    ✗ _meta.json invalid")
        for e in errors:
            print(f"      - {e}")
        all_valid = False

    # 4. Python语法验证
    print("\n[4/5] Validating Python syntax...")
    valid, errors = validate_python_syntax(skill_path / 'scripts')
    if valid:
        print("    ✓ Python syntax valid")
    else:
        print("    ✗ Python syntax errors found")
        for e in errors:
            print(f"      - {e}")
        all_valid = False

    # 5. 路径英文验证
    print("\n[5/5] Validating paths are English...")
    valid, errors = validate_paths_english(skill_path)
    if valid:
        print("    ✓ All paths are English")
    else:
        print("    ✗ Path validation failed")
        for e in errors:
            print(f"      - {e}")
        all_valid = False

    print("\n" + "=" * 50)
    if all_valid:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
