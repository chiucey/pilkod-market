#!/usr/bin/env python3
"""
PPT内容工作流技能验证脚本
检查SKILL.md的结构和内容是否符合规范
"""

import os
import sys
import re
from pathlib import Path


def validate_frontmatter(skill_path):
    """验证Frontmatter格式"""
    errors = []
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md文件不存在")
        return errors, warnings

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.strip().startswith("---"):
        errors.append("SKILL.md必须以---开头（Frontmatter必须在第一行）")
        return errors, warnings

    # 提取frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 0:
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter未正确闭合（缺少结束---）")
        return errors, warnings

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(f"^{field}:", frontmatter_text, re.MULTILINE):
            errors.append(f"Frontmatter缺少必需字段: {field}")

    # 检查name格式
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name字段格式错误：'{name}'，必须为连字符格式（a-z, 0-9, -）")

    return errors, warnings


def validate_structure(skill_path):
    """验证目录结构"""
    errors = []
    warnings = []

    # 检查_meta.json
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        errors.append("_meta.json文件不存在")
    else:
        import json
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json缺少id字段")
            if "version" not in meta:
                errors.append("_meta.json缺少version字段")
        except json.JSONDecodeError:
            errors.append("_meta.json格式错误（不是有效的JSON）")

    # 检查SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 检查禁止项：frontmatter前有markdown标题
        lines = content.split("\n")
        frontmatter_start = -1
        for i, line in enumerate(lines):
            if line.strip() == "---" and i == 0:
                frontmatter_start = 0
                break

        if frontmatter_start == -1:
            errors.append("未找到有效的frontmatter")

        # 检查核心铁律是否存在
        if "绝对忠实" not in content:
            warnings.append("缺少'绝对忠实'核心规则")
        if "架构锁定" not in content:
            warnings.append("缺少'架构锁定'核心规则")

    return errors, warnings


def validate_content_rules(skill_path):
    """验证内容规则完整性"""
    errors = []
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return errors, warnings

    content = skill_md.read_text(encoding="utf-8")

    # 检查关键章节
    required_sections = [
        "第一阶段",
        "第二阶段",
        "禁止行为清单",
        "异常输入处理"
    ]

    for section in required_sections:
        if section not in content:
            warnings.append(f"缺少关键章节：{section}")

    return errors, warnings


def main():
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        # 默认检查当前目录下的skill
        script_dir = Path(__file__).parent.parent
        skill_path = script_dir

    print(f"正在验证技能: {skill_path}")
    print("=" * 60)

    all_errors = []
    all_warnings = []

    # 执行各项验证
    errors, warnings = validate_frontmatter(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_structure(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_content_rules(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 输出结果
    if all_errors:
        print("\n❌ 错误：")
        for e in all_errors:
            print(f"  - {e}")

    if all_warnings:
        print("\n⚠️  警告：")
        for w in all_warnings:
            print(f"  - {w}")

    if not all_errors and not all_warnings:
        print("\n✅ 验证通过！")
        return 0
    elif not all_errors:
        print("\n✅ 验证通过（有警告）")
        return 0
    else:
        print("\n❌ 验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())