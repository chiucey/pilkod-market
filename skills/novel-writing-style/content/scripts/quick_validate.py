#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能文件的结构和内容
"""
import os
import re
import sys
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def validate_frontmatter(skill_path):
    """验证 SKILL.md 的 frontmatter"""
    skill_file = Path(skill_path) / "SKILL.md"

    if not skill_file.exists():
        print_error(f"SKILL.md not found at {skill_file}")
        return False

    content = skill_file.read_text(encoding='utf-8')

    # 检查是否以 frontmatter 开始
    if not content.startswith('---'):
        print_error("SKILL.md must start with YAML frontmatter (---)")
        return False

    # 提取 frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        print_error("Invalid frontmatter format")
        return False

    frontmatter = parts[1]

    # 检查必需字段
    if 'name:' not in frontmatter:
        print_error("Missing 'name:' in frontmatter")
        return False

    if 'description:' not in frontmatter:
        print_error("Missing 'description:' in frontmatter")
        return False

    # 检查 name 格式（连字符格式）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            print_error(f"Name '{name}' must be lowercase with hyphens only")
            return False
        print_success(f"Frontmatter name: {name}")

    # 检查 description 不为空
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            print_error("Description too short (minimum 10 characters)")
            return False
        print_success(f"Frontmatter description: {desc[:50]}...")

    return True

def validate_meta_json(skill_path):
    """验证 _meta.json 文件"""
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        print_error("_meta.json not found")
        return False

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in _meta.json: {e}")
        return False

    # 检查必需字段
    if 'id' not in meta:
        print_error("Missing 'id' in _meta.json")
        return False

    if 'version' not in meta:
        print_error("Missing 'version' in _meta.json")
        return False

    # 验证版本格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print_error(f"Version '{version}' must be in semver format (x.y.z)")
        return False

    print_success(f"_meta.json valid: id={meta['id']}, version={version}")
    return True

def validate_structure(skill_path):
    """验证目录结构"""
    skill_path = Path(skill_path)
    name = skill_path.name

    # 检查技能名称是否为英文
    if not re.match(r'^[a-z0-9-]+$', name):
        print_error(f"Skill folder name '{name}' must be lowercase with hyphens only")
        return False

    print_success(f"Skill folder name valid: {name}")

    # 检查 SKILL.md 存在
    if not (skill_path / "SKILL.md").exists():
        print_error("SKILL.md not found in skill root")
        return False

    print_success("SKILL.md exists")
    return True

def validate_no_secrets(skill_path):
    """检查是否有敏感信息"""
    forbidden_patterns = [
        r'password\s*[:=]',
        r'api_key\s*[:=]',
        r'secret\s*[:=]',
        r'AKIA[0-9A-Z]{16}',
    ]

    for py_file in Path(skill_path).rglob("*.py"):
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        for pattern in forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print_error(f"Potential secret found in {py_file}: {pattern}")
                return False

    print_success("No secrets detected")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]

    print_info(f"Validating skill at: {skill_path}")
    print("-" * 50)

    checks = [
        ("Structure", lambda: validate_structure(skill_path)),
        ("Frontmatter", lambda: validate_frontmatter(skill_path)),
        ("Meta JSON", lambda: validate_meta_json(skill_path)),
        ("Security", lambda: validate_no_secrets(skill_path)),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{Colors.BLUE}[{name}]{Colors.END}")
        results.append(check_func())

    print("\n" + "=" * 50)
    if all(results):
        print_success("All validations passed!")
        sys.exit(0)
    else:
        print_error("Some validations failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
