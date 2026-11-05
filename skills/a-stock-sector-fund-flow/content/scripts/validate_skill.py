#!/usr/bin/env python3
"""
A股板块资金流向技能验证脚本
验证SKILL.md和_meta.json的质量和格式
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证SKILL.md的frontmatter格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md文件不存在"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.strip().startswith("---"):
        return False, "SKILL.md必须以YAML frontmatter开头（---）"

    # 提取frontmatter
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == "---":
            break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = "\n".join(frontmatter_lines)

    # 解析frontmatter
    try:
        meta = {}
        for line in frontmatter_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
    except Exception as e:
        return False, f"Frontmatter解析失败: {e}"

    # 验证必填字段
    if "name" not in meta:
        return False, "Frontmatter缺少name字段"

    if "description" not in meta:
        return False, "Frontmatter缺少description字段"

    # 验证name格式（连字符）
    name = meta["name"]
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, f"name字段格式错误，应使用连字符格式: {name}"

    # 验证description包含触发短语
    desc = meta["description"]
    trigger_phrases = ["板块资金流向", "主力资金", "资金进出", "资金流", "资金净流入"]
    if not any(phrase in desc for phrase in trigger_phrases):
        return False, "description应包含触发短语，如'板块资金流向'、'主力资金'等"

    return True, "Frontmatter验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证_meta.json的格式和内容"""
    meta_json = skill_path / "_meta.json"

    if not meta_json.exists():
        return False, "_meta.json文件不存在"

    try:
        content = meta_json.read_text(encoding="utf-8")
        meta = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON解析失败: {e}"

    # 验证必填字段
    if "id" not in meta:
        return False, "_meta.json缺少id字段"

    if "version" not in meta:
        return False, "_meta.json缺少version字段"

    # 验证id是整数
    if not isinstance(meta["id"], int):
        return False, "_meta.json的id必须是整数"

    # 验证version格式
    version = meta["version"]
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"_meta.json的version格式错误，应为语义化版本: {version}"

    return True, "_meta.json验证通过"


def validate_directory_structure(skill_path: Path) -> tuple[bool, str]:
    """验证目录结构"""
    name = skill_path.name

    # 验证目录名使用连字符
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, f"目录名应使用连字符格式: {name}"

    # 验证必要的文件存在
    if not (skill_path / "SKILL.md").exists():
        return False, "缺少SKILL.md文件"

    if not (skill_path / "_meta.json").exists():
        return False, "缺少_meta.json文件"

    return True, "目录结构验证通过"


def validate_skill(skill_path: str) -> bool:
    """执行所有验证"""
    skill_path = Path(skill_path)

    print(f"正在验证技能: {skill_path.name}")
    print("-" * 50)

    all_passed = True

    # 1. 目录结构验证
    passed, msg = validate_directory_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 2. Frontmatter验证
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 3. _meta.json验证
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    print(f"验证结果: {'全部通过 ✓' if all_passed else '存在错误 ✗'}")

    return all_passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill_path>")
        sys.exit(1)

    success = validate_skill(sys.argv[1])
    sys.exit(0 if success else 1)
