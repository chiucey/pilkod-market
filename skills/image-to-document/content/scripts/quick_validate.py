#!/usr/bin/env python3
"""快速验证脚本 - 检查 SKILL.md 和 _meta.json 格式"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> list[str]:
    """验证 frontmatter 格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return errors

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头（忽略 BOM 和空白）
    stripped = content.lstrip('\ufeff').strip()
    if not stripped.startswith("---"):
        errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")
        return errors

    # 提取 frontmatter
    lines = stripped.split("\n")
    if len(lines) < 3 or lines[0] != "---":
        errors.append("frontmatter 格式错误，需要 --- 分隔符")
        return errors

    # 找到结束分隔符
    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("frontmatter 缺少结束分隔符 ---")
        return errors

    # 解析 YAML - 解析 lines[1:end_idx]（name和description行）
    try:
        frontmatter = {}
        for line in lines[1:end_idx]:
            # 跳过注释和空行
            if line.strip().startswith('#') or not line.strip():
                continue
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                value = line.split(":", 1)[1].strip()
                frontmatter[key] = value
    except Exception as e:
        errors.append(f"frontmatter 解析错误: {e}")
        return errors

    # 必填字段检查
    if "name" not in frontmatter:
        errors.append("frontmatter 缺少必填字段: name")
    else:
        name = frontmatter["name"]
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 必须使用连字符格式 (a-z, 0-9, -): {name}")
        if len(name) > 64:
            errors.append(f"name 长度不能超过 64 字符: {name}")

    if "description" not in frontmatter:
        errors.append("frontmatter 缺少必填字段: description")
    elif len(frontmatter.get("description", "")) < 10:
        errors.append("description 长度不足，至少需要 10 个字符")

    return errors


def validate_meta_json(skill_path: Path) -> list[str]:
    """验证 _meta.json 格式"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append("_meta.json 文件不存在")
        return errors

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 解析错误: {e}")
        return errors

    # 必填字段检查
    if "id" not in meta:
        errors.append("_meta.json 缺少必填字段: id")
    elif not isinstance(meta["id"], (int, str)):
        errors.append("_meta.json 的 id 必须是数字或字符串")

    if "version" not in meta:
        errors.append("_meta.json 缺少必填字段: version")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta.get("version", "")):
        errors.append("_meta.json 的 version 必须符合语义化版本格式 (如 1.0.0)")

    return errors


def validate_directory_structure(skill_path: Path) -> list[str]:
    """验证目录结构"""
    errors = []
    folder_name = skill_path.name

    # name 应与文件夹名匹配
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if name != folder_name:
                errors.append(f"frontmatter 的 name ({name}) 与文件夹名 ({folder_name}) 不一致")

    return errors


def main():
    skill_path = Path("/workspace/temp-skills/image-to-document")

    print("=" * 50)
    print("技能验证检查")
    print("=" * 50)

    all_errors = []

    # 1. Frontmatter 验证
    print("\n[1/3] 检查 frontmatter 格式...")
    fm_errors = validate_frontmatter(skill_path)
    if fm_errors:
        all_errors.extend(fm_errors)
        for err in fm_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ frontmatter 格式正确")

    # 2. _meta.json 验证
    print("\n[2/3] 检查 _meta.json...")
    meta_errors = validate_meta_json(skill_path)
    if meta_errors:
        all_errors.extend(meta_errors)
        for err in meta_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ _meta.json 格式正确")

    # 3. 目录结构验证
    print("\n[3/3] 检查目录结构...")
    struct_errors = validate_directory_structure(skill_path)
    if struct_errors:
        all_errors.extend(struct_errors)
        for err in struct_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ 目录结构正确")

    # 总结
    print("\n" + "=" * 50)
    if all_errors:
        print(f"验证失败: {len(all_errors)} 个错误")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("验证通过!")
        sys.exit(0)


if __name__ == "__main__":
    main()