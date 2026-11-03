#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能验证脚本 - 快速质量检查

检查项目：
1. SKILL.md frontmatter 格式正确性
2. _meta.json 必要字段
3. 文件路径和命名规范
4. 资源文件完整性
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Tuple


class ValidationError:
    def __init__(self, level: str, message: str, file_path: str = ""):
        self.level = level  # error, warning, info
        self.message = message
        self.file_path = file_path

    def __str__(self):
        prefix = f"[{self.level.upper()}]"
        if self.file_path:
            return f"{prefix} {self.file_path}: {self.message}"
        return f"{prefix} {self.message}"


def validate_frontmatter(skill_md_path: str) -> List[ValidationError]:
    """验证 SKILL.md frontmatter 格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append(ValidationError(
            "error",
            "SKILL.md must start with YAML frontmatter delimiter '---'",
            skill_md_path
        ))
        return errors

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        errors.append(ValidationError(
            "error",
            "Frontmatter too short, missing content",
            skill_md_path
        ))
        return errors

    # 找到结束 delimiter
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        errors.append(ValidationError(
            "error",
            "Missing closing '---' delimiter for frontmatter",
            skill_md_path
        ))
        return errors

    # 解析 YAML
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必要字段
    if 'name:' not in frontmatter_text:
        errors.append(ValidationError(
            "error",
            "Missing required field 'name' in frontmatter",
            skill_md_path
        ))

    if 'description:' not in frontmatter_text:
        errors.append(ValidationError(
            "error",
            "Missing required field 'description' in frontmatter",
            skill_md_path
        ))

    # 检查是否有 markdown 标题在 frontmatter 之前
    if len(lines) > end_idx + 1:
        next_line = lines[end_idx + 1].strip()
        if next_line.startswith('#'):
            errors.append(ValidationError(
                "error",
                "Markdown heading found before frontmatter end delimiter",
                skill_md_path
            ))

    return errors


def validate_meta_json(meta_path: str) -> List[ValidationError]:
    """验证 _meta.json 格式"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append(ValidationError(
            "error",
            "_meta.json not found",
            meta_path
        ))
        return errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append(ValidationError(
                "error",
                "Missing required field 'id' in _meta.json",
                meta_path
            ))

        if 'version' not in meta:
            errors.append(ValidationError(
                "error",
                "Missing required field 'version' in _meta.json",
                meta_path
            ))
        elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append(ValidationError(
                "warning",
                "Version should follow semantic versioning (e.g., 1.0.0)",
                meta_path
            ))

    except json.JSONDecodeError as e:
        errors.append(ValidationError(
            "error",
            f"Invalid JSON format: {e}",
            meta_path
        ))

    return errors


def validate_naming(path: str) -> List[ValidationError]:
    """检查路径和文件名是否为英文"""
    errors = []

    # 检查文件夹名称
    folder_name = os.path.basename(path)
    if not re.match(r'^[a-z0-9\-_]+$', folder_name):
        errors.append(ValidationError(
            "warning",
            f"Folder name should use English lowercase with hyphens: '{folder_name}'",
            path
        ))

    # 检查 SKILL.md frontmatter 中的 name 字段
    skill_md = os.path.join(path, 'SKILL.md')
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 frontmatter
        lines = content.split('\n')
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx > 0:
            frontmatter = '\n'.join(lines[1:end_idx])

            # 提取 name 值
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
            if name_match:
                name_value = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9\-_]+$', name_value):
                    errors.append(ValidationError(
                        "warning",
                        f"Frontmatter 'name' should use English lowercase with hyphens: '{name_value}'",
                        skill_md
                    ))

    return errors


def validate_structure(path: str) -> List[ValidationError]:
    """验证目录结构"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        fpath = os.path.join(path, fname)
        if not os.path.exists(fpath):
            errors.append(ValidationError(
                "error",
                f"Required file missing: {fname}",
                path
            ))

    return errors


def validate_skill(skill_path: str) -> Tuple[bool, List[ValidationError]]:
    """
    执行完整验证
    返回: (是否通过, 错误列表)
    """
    all_errors = []

    # 检查路径是否存在
    if not os.path.exists(skill_path):
        return False, [ValidationError("error", f"Path does not exist: {skill_path}")]

    # 执行各项验证
    all_errors.extend(validate_structure(skill_path))
    all_errors.extend(validate_meta_json(os.path.join(skill_path, '_meta.json')))
    all_errors.extend(validate_frontmatter(os.path.join(skill_path, 'SKILL.md')))
    all_errors.extend(validate_naming(skill_path))

    # 过滤出 error 级别
    errors_only = [e for e in all_errors if e.level == "error"]

    return len(errors_only) == 0, all_errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]

    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    passed, errors = validate_skill(skill_path)

    # 按级别分组显示
    by_level = {"error": [], "warning": [], "info": []}
    for e in errors:
        by_level[e.level].append(e)

    for level in ["error", "warning", "info"]:
        if by_level[level]:
            print(f"\n[{level.upper()}S]")
            for e in by_level[level]:
                print(f"  {e}")

    print("=" * 50)

    if passed:
        print("✓ Validation PASSED")
        return 0
    else:
        print("✗ Validation FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
