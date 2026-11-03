#!/usr/bin/env python3
"""
AI 新闻情报系统技能 - 快速验证脚本
验证 SKILL.md 结构和 frontmatter 格式
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 frontmatter 格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查第一行是否是 ---
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        errors.append("SKILL.md 第一行必须是 --- (frontmatter 开始)")
        return False, errors

    # 找到第二个 ---
    try:
        end_idx = lines.index("---", 1)
    except ValueError:
        errors.append("SKILL.md 缺少 closing ---")
        return False, errors

    # 提取 frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = "\n".join(frontmatter_lines)

    # 检查必需字段
    if not re.search(r"^name:\s*.+$", frontmatter_text, re.MULTILINE):
        errors.append("frontmatter 缺少 name 字段")

    if not re.search(r"^description:\s*.+$", frontmatter_text, re.MULTILINE):
        errors.append("frontmatter 缺少 description 字段")

    # 检查 name 格式（连字符）
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"name '{name}' 必须使用连字符格式 (kebab-case)")

    # 检查 description 是否包含触发短语
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("description 过短，应包含详细的触发短语")
        if "当用户" not in desc and "use when" not in desc.lower():
            errors.append("description 应包含触发短语 (当用户.../Use when...)")

    # 检查是否在 frontmatter 后有 markdown 标题
    if end_idx + 1 < len(lines):
        next_line = lines[end_idx + 1].strip()
        if next_line.startswith("#"):
            errors.append("frontmatter 后面不能直接跟 markdown 标题 (#)")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json 格式错误: {e}"]

    # 检查必需字段
    if "id" not in meta:
        errors.append("_meta.json 缺少 id 字段")
    elif not isinstance(meta["id"], (int, str)):
        errors.append("_meta.json id 必须是数字或字符串")

    if "version" not in meta:
        errors.append("_meta.json 缺少 version 字段")
    elif not re.match(r"^\d+\.\d+\.\d+$", meta.get("version", "")):
        errors.append("_meta.json version 必须符合语义化版本格式 (x.y.z)")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查必需的目录和文件
    required = ["SKILL.md", "_meta.json"]
    for item in required:
        if not (skill_path / item).exists():
            errors.append(f"缺少必需文件: {item}")

    # 检查可选目录
    optional_dirs = ["references", "scripts", "assets"]
    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{dir_name} 应该是目录而非文件")

    return len(errors) == 0, errors


def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """验证命名规范"""
    errors = []
    folder_name = skill_path.name

    # 检查文件夹名称是否为英文
    if not re.match(r"^[a-z0-9-]+$", folder_name):
        errors.append(f"文件夹名称 '{folder_name}' 必须使用英文连字符格式")

    # 检查是否有中文字符
    if re.search(r"[\u4e00-\u9fff]", folder_name):
        errors.append(f"文件夹名称 '{folder_name}' 包含中文字符")

    return len(errors) == 0, errors


def main():
    """主验证流程"""
    # 获取技能路径（默认为当前目录）
    skill_path = Path(__file__).parent.parent

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 执行所有验证
    validators = [
        ("目录结构", validate_structure),
        ("Frontmatter 格式", validate_frontmatter),
        ("_meta.json 格式", validate_meta_json),
        ("命名规范", validate_naming),
    ]

    for name, validator in validators:
        passed, errors = validator(skill_path)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

        if not passed:
            all_passed = False
            for error in errors:
                print(f"   • {error}")

    print("-" * 50)

    if all_passed:
        print("✅ 所有验证通过!")
        return 0
    else:
        print("❌ 验证失败，请修复上述问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
