#!/usr/bin/env python3
"""
离谱Case判定技能 - 快速验证脚本
验证 SKILL.md 和 _meta.json 的基本格式
"""

import json
import os
import sys
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md frontmatter 格式"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return False, errors

    content = skill_md.read_text(encoding="utf-8")

    # 检查第一行是否是 ---
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        errors.append("Frontmatter 必须从第一行开始（以 --- 开头）")
        return False, errors

    # 找到第二个 --- 的位置
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("Frontmatter 缺少结束标记 ---")
        return False, errors

    # 解析 frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = "\n".join(frontmatter_lines)

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if f"{field}:" not in frontmatter_text:
            errors.append(f"Frontmatter 缺少必需字段: {field}")

    # 检查 name 格式
    if "name:" in frontmatter_text:
        for line in frontmatter_lines:
            if line.strip().startswith("name:"):
                name_value = line.split(":", 1)[1].strip()
                if not name_value:
                    errors.append("name 字段不能为空")
                # 检查是否与文件夹名称匹配
                folder_name = Path(skill_path).name
                if name_value != folder_name:
                    errors.append(f"name ({name_value}) 应与文件夹名称 ({folder_name}) 匹配")

    return len(errors) == 0, errors


def validate_meta(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json 格式错误: {e}")
        return False, errors

    # 检查必需字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必需字段: {field}")

    # 检查 id 是否为数字
    if "id" in meta:
        if not isinstance(meta["id"], (int, str)):
            errors.append("id 应为数字或字符串")

    # 检查 version 格式（语义化版本）
    if "version" in meta:
        version = meta["version"]
        if not isinstance(version, str):
            errors.append("version 应为字符串格式 (如 1.0.0)")
        elif not version.replace(".", "").replace("-", "").replace("+", "").isdigit():
            errors.append(f"version 格式不正确: {version}")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查必要的目录和文件
    required = ["SKILL.md", "_meta.json"]
    for item in required:
        item_path = Path(skill_path) / item
        if not item_path.exists():
            errors.append(f"缺少必需文件: {item}")

    # 检查 references 目录（可选但推荐）
    references_dir = Path(skill_path) / "references"
    if references_dir.exists():
        # 检查是否为空
        refs = list(references_dir.iterdir())
        if len(refs) == 0:
            errors.append("references 目录为空，建议添加参考文档")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    # 解析绝对路径
    skill_path = str(Path(skill_path).resolve())

    print(f"正在验证技能: {skill_path}")
    print("=" * 50)

    all_passed = True

    # 验证结构
    print("\n[1] 验证目录结构...")
    passed, errors = validate_structure(skill_path)
    if passed:
        print("    ✓ 结构验证通过")
    else:
        print("    ✗ 结构验证失败:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # 验证 frontmatter
    print("\n[2] 验证 Frontmatter 格式...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("    ✓ Frontmatter 验证通过")
    else:
        print("    ✗ Frontmatter 验证失败:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # 验证 _meta.json
    print("\n[3] 验证 _meta.json 格式...")
    passed, errors = validate_meta(skill_path)
    if passed:
        print("    ✓ _meta.json 验证通过")
    else:
        print("    ✗ _meta.json 验证失败:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证错误，请修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
