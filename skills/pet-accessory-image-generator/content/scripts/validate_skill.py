#!/usr/bin/env python3
"""
技能验证脚本 - 检查 SKILL.md 和 _meta.json 的格式规范
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter 格式"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.strip().startswith("---"):
        errors.append("❌ SKILL.md 必须以 --- 开头（frontmatter 必须在第一行）")
        return False, errors

    # 提取 frontmatter
    lines = content.split("\n")
    if len(lines) < 3:
        errors.append("❌ frontmatter 格式不完整")
        return False, errors

    # 解析 frontmatter
    try:
        frontmatter_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if in_frontmatter:
                frontmatter_lines.append(line)

        frontmatter_text = "\n".join(frontmatter_lines)

        # 检查必需字段
        if not re.search(r"^name:\s*\S+", frontmatter_text, re.MULTILINE):
            errors.append("❌ frontmatter 缺少 name 字段")

        if not re.search(r"^description:\s*>?", frontmatter_text, re.MULTILINE):
            errors.append("❌ frontmatter 缺少 description 字段")

    except Exception as e:
        errors.append(f"❌ frontmatter 解析错误: {str(e)}")

    return len(errors) == 0, errors


def validate_meta(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []
    meta_json = Path(skill_path) / "_meta.json"

    if not meta_json.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_json.read_text(encoding="utf-8"))

        # 检查必需字段
        if "id" not in meta:
            errors.append("❌ _meta.json 缺少 id 字段")
        if "version" not in meta:
            errors.append("❌ _meta.json 缺少 version 字段")

        # 检查 id 是否为有效格式
        if "id" in meta:
            if not str(meta["id"]).isdigit():
                errors.append("❌ id 必须是数字")

        # 检查 version 格式
        if "version" in meta:
            if not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
                errors.append("❌ version 格式必须是 x.y.z")

    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json JSON 解析错误: {str(e)}")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        errors.append("❌ SKILL.md 不存在")

    return len(errors) == 0, errors


def validate_naming(skill_path: str) -> tuple[bool, list[str]]:
    """验证文件命名规范"""
    errors = []
    skill_name = Path(skill_path).name

    # 检查名称格式（连字符、不含中文）
    if not re.match(r"^[a-z0-9-]+$", skill_name):
        errors.append("❌ 技能目录名称必须使用英文小写、连字符分隔（kebab-case）")

    if len(skill_name) > 64:
        errors.append("❌ 技能名称不能超过 64 个字符")

    return len(errors) == 0, errors


def main():
    """主验证流程"""
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]

    print("=" * 50)
    print("技能验证报告")
    print("=" * 50)
    print(f"路径: {skill_path}")
    print()

    all_passed = True

    # 1. 目录结构验证
    print("📁 目录结构检查...")
    passed, errors = validate_structure(skill_path)
    if passed:
        print("   ✅ 通过")
    else:
        for err in errors:
            print(f"   {err}")
        all_passed = False
    print()

    # 2. 命名规范验证
    print("🏷️ 命名规范检查...")
    passed, errors = validate_naming(skill_path)
    if passed:
        print("   ✅ 通过")
    else:
        for err in errors:
            print(f"   {err}")
        all_passed = False
    print()

    # 3. Frontmatter 验证
    print("📝 SKILL.md Frontmatter 检查...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("   ✅ 通过")
    else:
        for err in errors:
            print(f"   {err}")
        all_passed = False
    print()

    # 4. _meta.json 验证
    print("📋 _meta.json 检查...")
    passed, errors = validate_meta(skill_path)
    if passed:
        print("   ✅ 通过")
    else:
        for err in errors:
            print(f"   {err}")
        all_passed = False
    print()

    # 总结
    print("=" * 50)
    if all_passed:
        print("✅ 所有验证通过！")
        sys.exit(0)
    else:
        print("❌ 存在验证错误，请修复后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
