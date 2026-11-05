#!/usr/bin/env python3
"""
AutoLearn&Refine_Claw 技能验证脚本
验证 SKILL.md 和 _meta.json 的结构完整性
"""

import json
import os
import sys
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md frontmatter"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith("---"):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头（第一行为 ---）")
        return False, errors

    # 解析 frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("SKILL.md frontmatter 未正确闭合（缺少结束 ---）")
        return False, errors

    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter_text = "\n".join(frontmatter_lines)

    # 检查必填字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if f"{field}:" not in frontmatter_text:
            errors.append(f"Frontmatter 缺少必填字段: {field}")

    # 检查 name 格式
    for line in frontmatter_lines:
        if line.strip().startswith("name:"):
            name_value = line.split(":", 1)[1].strip()
            if " " in name_value:
                errors.append("name 字段必须使用连字符格式（hyphen-case），不能包含空格")
            break

    # 检查 description 是否包含触发短语
    has_trigger = any(phrase in frontmatter_text for phrase in [
        "复盘", "学习优化", "迭代", "效果评估", "模拟验证"
    ])
    if not has_trigger:
        errors.append("description 必须包含触发短语以确保正确路由")

    return len(errors) == 0, errors


def validate_meta(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON 解析失败: {e}"]

    # 检查必填字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必填字段: {field}")

    # 验证 id 格式（应为数字字符串）
    if "id" in meta and not str(meta["id"]).isdigit():
        errors.append("id 必须为纯数字字符串")

    # 验证 version 格式（语义化版本）
    if "version" in meta:
        version = meta["version"]
        if not all(part.isdigit() for part in version.split(".")):
            errors.append("version 必须遵循语义化版本格式（如 1.0.0）")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查目录命名
    skill_name = Path(skill_path).name
    if " " in skill_name or not skill_name.islower():
        errors.append("技能文件夹名称必须为小写并使用连字符格式")

    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for fname in required_files:
        fpath = Path(skill_path) / fname
        if not fpath.exists():
            errors.append(f"缺少必需文件: {fname}")

    return len(errors) == 0, errors


def main():
    skill_path = os.environ.get("SKILL_PATH", "/workspace/temp-skills/auto-learn-refine-claw")

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证结构
    passed, errors = validate_structure(skill_path)
    if not passed:
        all_passed = False
        print(f"[FAIL] 目录结构验证:")
        for e in errors:
            print(f"  - {e}")
    else:
        print(f"[PASS] 目录结构验证")

    # 验证 frontmatter
    passed, errors = validate_frontmatter(skill_path)
    if not passed:
        all_passed = False
        print(f"[FAIL] Frontmatter 验证:")
        for e in errors:
            print(f"  - {e}")
    else:
        print(f"[PASS] Frontmatter 验证")

    # 验证 _meta.json
    passed, errors = validate_meta(skill_path)
    if not passed:
        all_passed = False
        print(f"[FAIL] _meta.json 验证:")
        for e in errors:
            print(f"  - {e}")
    else:
        print(f"[PASS] _meta.json 验证")

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 验证失败，请修复上述问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
