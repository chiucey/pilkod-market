#!/usr/bin/env python3
"""
龙头股票识别技能 - 快速验证脚本
用于验证技能结构和Frontmatter格式
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证Frontmatter格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md not found"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # 提取frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        return False, "Frontmatter too short"

    # 找到结束标记
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "Frontmatter missing closing ---"

    # 提取并解析frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    # 检查name格式（连字符）
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"name '{name}' should use hyphen-case (lowercase with hyphens)"

    # 检查name长度
    if len(name) > 64:
        return False, f"name '{name}' exceeds 64 characters"

    # 检查description是否包含触发短语
    desc = frontmatter['description']
    trigger_phrases = ['龙头', '板块', '识别', '分析']
    has_trigger = any(phrase in desc for phrase in trigger_phrases)
    if not has_trigger:
        return False, "description should contain trigger phrases like '龙头', '板块', '识别', '分析'"

    return True, "Frontmatter validation passed"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证_meta.json格式"""
    import json

    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    # 验证id是整数
    if not isinstance(meta['id'], int):
        return False, "id must be an integer"

    # 验证version格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, "version must follow semantic versioning (e.g., 1.0.0)"

    return True, "Meta validation passed"


def validate_structure(skill_path: Path) -> tuple[bool, str]:
    """验证技能目录结构"""
    name = skill_path.name

    # 检查name与目录名匹配
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Directory name '{name}' should use hyphen-case (English only)"

    # 检查SKILL.md存在
    if not (skill_path / "SKILL.md").exists():
        return False, "SKILL.md not found in skill directory"

    return True, "Structure validation passed"


def main():
    """主验证函数"""
    skill_path = Path(__file__).parent.parent

    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    all_passed = True

    # 1. 验证目录结构
    passed, msg = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] Structure: {msg}")
    all_passed &= passed

    # 2. 验证frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] Frontmatter: {msg}")
    all_passed &= passed

    # 3. 验证meta.json
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta JSON: {msg}")
    all_passed &= passed

    print("=" * 50)

    if all_passed:
        print("✅ All validations passed!")
        return 0
    else:
        print("❌ Validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())