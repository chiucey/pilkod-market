#!/usr/bin/env python3
"""
Aegis Studios 技能验证脚本
验证技能结构、frontmatter 和内容完整性
"""

import json
import os
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 SKILL.md frontmatter"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return False, errors

    content = skill_md.read_text(encoding="utf-8")
    lines = content.split("\n")

    # 检查第一行是否是 ---
    if not lines[0].strip() == "---":
        errors.append(f"Frontmatter 必须从第一行开始，当前第一行: {lines[0]}")
        return False, errors

    # 找到 frontmatter 结束
    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        errors.append("未找到 frontmatter 结束标记 ---")
        return False, errors

    # 解析 frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = "\n".join(frontmatter_lines)

    try:
        fm = {}
        for line in frontmatter_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                fm[key.strip()] = value.strip()
    except Exception as e:
        errors.append(f"Frontmatter 解析错误: {e}")
        return False, errors

    # 检查必填字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in fm:
            errors.append(f"缺少必填字段: {field}")

    # 检查 name 格式
    if "name" in fm:
        name = fm["name"]
        if " " in name:
            errors.append(f"name 不能包含空格，当前值: {name}")
        if len(name) > 64:
            errors.append(f"name 长度超过64字符: {len(name)}")

    # 检查 description
    if "description" in fm:
        desc = fm["description"]
        if len(desc) < 20:
            errors.append("description 太短，需要至少20字符")
        if "Use when" not in desc and "使用" not in desc:
            errors.append("description 应包含触发条件说明 (Use when / 使用)")

    return len(errors) == 0, errors


def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 解析错误: {e}")
        return False, errors

    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"缺少必填字段: {field}")

    # 验证 id 是数字
    if "id" in meta:
        try:
            int(meta["id"])
        except ValueError:
            errors.append(f"id 必须是数字，当前值: {meta['id']}")

    # 验证 version 格式
    if "version" in meta:
        version = meta["version"]
        parts = version.split(".")
        if len(parts) != 3:
            errors.append(f"version 格式错误，应为 x.y.z，当前值: {version}")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查技能名称（目录名）
    name = skill_path.name
    if not name.replace("-", "").replace("_", "").isalnum():
        errors.append(f"目录名包含非法字符: {name}")

    if not name.isascii():
        errors.append(f"目录名必须为英文: {name}")

    # 检查资源路径
    for subdir in ["scripts", "references", "assets"]:
        subdir_path = skill_path / subdir
        if subdir_path.exists():
            for file in subdir_path.rglob("*"):
                if file.is_file() and not str(file).encode("ascii", errors="ignore"):
                    errors.append(f"非ASCII文件路径: {file}")

    return len(errors) == 0, errors


def main():
    skill_path = Path(__file__).parent.parent.resolve()

    print(f"验证技能: {skill_path.name}")
    print("=" * 50)

    all_errors = []

    # 验证 frontmatter
    print("\n[1/3] 验证 Frontmatter...")
    valid, errors = validate_frontmatter(skill_path)
    if valid:
        print("  ✓ Frontmatter 验证通过")
    else:
        print("  ✗ Frontmatter 验证失败:")
        for e in errors:
            print(f"    - {e}")
        all_errors.extend(errors)

    # 验证 meta
    print("\n[2/3] 验证 _meta.json...")
    valid, errors = validate_meta(skill_path)
    if valid:
        print("  ✓ _meta.json 验证通过")
    else:
        print("  ✗ _meta.json 验证失败:")
        for e in errors:
            print(f"    - {e}")
        all_errors.extend(errors)

    # 验证结构
    print("\n[3/3] 验证目录结构...")
    valid, errors = validate_structure(skill_path)
    if valid:
        print("  ✓ 目录结构验证通过")
    else:
        print("  ✗ 目录结构验证失败:")
        for e in errors:
            print(f"    - {e}")
        all_errors.extend(errors)

    print("\n" + "=" * 50)
    if all_errors:
        print(f"验证失败，共 {len(all_errors)} 个错误")
        sys.exit(1)
    else:
        print("✓ 所有验证通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
