#!/usr/bin/env python3
"""
PPT视频生成技能验证脚本
验证技能文件的完整性和格式正确性
"""

import os
import json
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # 提取frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---':
        return False, "Invalid frontmatter structure"

    # 找到结束标记
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return False, "Frontmatter missing closing ---"

    # 解析frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 验证必需字段
    required_fields = ['name', 'description']
    missing_fields = [f for f in required_fields if f not in frontmatter]
    if missing_fields:
        return False, f"Missing required frontmatter fields: {missing_fields}"

    # 验证name格式（连字符）
    name = frontmatter.get('name', '')
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, f"Invalid name format: '{name}'. Use hyphen-case (e.g., 'my-skill')"

    # frontmatter从第一行开始，所以前面应该为空
    # 检查frontmatter之后是否有markdown标题
    content_after_frontmatter = '\n'.join(lines[end_idx+1:]).strip()
    if not content_after_frontmatter.startswith('#'):
        return False, "Content after frontmatter should start with markdown heading"

    # 验证frontmatter之前没有其他内容
    if len(lines) > 0 and lines[0].strip() == '---':
        pass  # 正确：第一行是---
    else:
        return False, "SKILL.md must start with ---"

    return True, "Frontmatter validated successfully"

def validate_meta_json(meta_path):
    """验证_meta.json的格式"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_fields = ['id', 'version']
        missing_fields = [f for f in required_fields if f not in meta]
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"

        # 验证id是数字
        if not isinstance(meta['id'], (int, str)):
            return False, f"Invalid id type: {type(meta['id'])}"

        # 验证version格式
        version = str(meta['version'])
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            return False, f"Invalid version format: {version}. Use semantic versioning (e.g., '1.0.0')"

        return True, "_meta.json validated successfully"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading _meta.json: {e}"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    missing_files = []

    for f in required_files:
        if not (skill_dir / f).exists():
            missing_files.append(f)

    if missing_files:
        return False, f"Missing required files: {missing_files}"

    return True, "Directory structure validated"

def validate_skill_description(skill_md_path):
    """验证description包含触发短语"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查description是否包含触发短语
    if 'Use when' not in content and '当用户' not in content:
        return False, "Description should include trigger phrases like 'Use when...' or '当用户...'"

    return True, "Description trigger phrases validated"

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md_path = skill_dir / 'SKILL.md'
    meta_path = skill_dir / '_meta.json'

    all_passed = True
    results = []

    # 运行所有验证
    validations = [
        ("Frontmatter Format", lambda: validate_frontmatter(skill_md_path)),
        ("Meta JSON Format", lambda: validate_meta_json(meta_path)),
        ("Directory Structure", lambda: validate_directory_structure(skill_dir)),
        ("Trigger Phrases", lambda: validate_skill_description(skill_md_path)),
    ]

    for name, validator in validations:
        passed, message = validator()
        results.append((name, passed, message))
        if not passed:
            all_passed = False
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {message}")

    print("\n" + "="*50)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
