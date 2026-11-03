#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能驗證腳本
驗證 A股量化因子挖掘技能的核心功能
"""

import os
import sys
import json
from pathlib import Path

def validate_skill_structure(skill_path):
    """驗證技能目錄結構"""
    print("驗證技能目錄結構...")

    required_files = [
        "SKILL.md",
        "_meta.json"
    ]

    required_dirs = [
        "scripts",
        "references"
    ]

    missing = []
    for f in required_files:
        if not (skill_path / f).exists():
            missing.append(f)

    for d in required_dirs:
        if not (skill_path / d).is_dir():
            missing.append(d)

    if missing:
        print(f"  ✗ 缺少文件/目錄: {missing}")
        return False

    print("  ✓ 目錄結構完整")
    return True


def validate_frontmatter(skill_path):
    """驗證 SKILL.md frontmatter"""
    print("驗證 SKILL.md frontmatter...")

    skillee_md = skill_path / "SKILL.md"
    if not skillee_md.exists():
        print("  ✗ SKILL.md 不存在")
        return False

    content = skillee_md.read_text()

    # 檢查是否以 --- 開頭
    if not content.strip().startswith('---'):
        print("  ✗ SKILL.md 必須以 YAML frontmatter 開頭")
        return False

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == '---' and not in_frontmatter:
            in_frontmatter = True
            continue
        elif line.strip() == '---' and in_frontmatter:
            break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 檢查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not any(line.strip().startswith(field + ':') for line in frontmatter_lines):
            print(f"  ✗ 缺少必填字段: {field}")
            return False

    print("  ✓ frontmatter 格式正確")
    print(f"  - name: {extract_field(frontmatter_lines, 'name')}")
    print(f"  - description: {extract_field(frontmatter_lines, 'description')[:50]}...")
    return True


def extract_field(lines, field_name):
    """提取 frontmatter 字段值"""
    for line in lines:
        if line.strip().startswith(field_name + ':'):
            return line.split(':', 1)[1].strip()
    return ""


def validate_meta_json(skill_path):
    """驗證 _meta.json"""
    print("驗證 _meta.json...")

    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        print("  ✗ _meta.json 不存在")
        return False

    try:
        meta = json.loads(meta_file.read_text())
    except json.JSONDecodeError as e:
        print(f"  ✗ _meta.json 格式錯誤: {e}")
        return False

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            print(f"  ✗ 缺少必填字段: {field}")
            return False

    print("  ✓ _meta.json 格式正確")
    print(f"  - id: {meta['id']}")
    print(f"  - version: {meta['version']}")
    return True


def validate_scripts(skill_path):
    """驗證腳本文件"""
    print("驗證腳本文件...")

    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        print("  ⚠ scripts 目錄不存在")
        return True

    python_files = list(scripts_dir.glob("*.py"))
    if not python_files:
        print("  ⚠ 沒有 Python 腳本文件")
        return True

    for py_file in python_files:
        if py_file.stat().st_size < 100:
            print(f"  ⚠ {py_file.name} 文件過小，可能不完整")
        else:
            print(f"  ✓ {py_file.name}")

    return True


def validate_references(skill_path):
    """驗證參考文檔"""
    print("驗證參考文檔...")

    refs_dir = skill_path / "references"
    if not refs_dir.exists():
        print("  ⚠ references 目錄不存在")
        return True

    md_files = list(refs_dir.glob("*.md"))
    if not md_files:
        print("  ⚠ 沒有 Markdown 參考文檔")
        return True

    for md_file in md_files:
        content = md_file.read_text()
        if len(content) < 100:
            print(f"  ⚠ {md_file.name} 內容過少")
        else:
            print(f"  ✓ {md_file.name} ({len(content)} 字符)")

    return True


def run_validation(skill_path_str):
    """執行完整驗證"""
    skill_path = Path(skill_path_str)

    print("=" * 50)
    print(f"驗證技能: {skill_path.name}")
    print("=" * 50)

    results = []

    results.append(validate_skill_structure(skill_path))
    results.append(validate_frontmatter(skill_path))
    results.append(validate_meta_json(skill_path))
    results.append(validate_scripts(skill_path))
    results.append(validate_references(skill_path))

    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有驗證通過！")
        return 0
    else:
        print("✗ 部分驗證失敗")
        return 1


if __name__ == "__main__":
    skill_path = "/workspace/temp-skills/a-stock-quant-factor-mining"
    sys.exit(run_validation(skill_path))
