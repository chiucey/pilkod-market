#!/usr/bin/env python3
"""
ERP知识优化技能 - 快速验证脚本
验证SKILL.md的结构和内容是否符合规范
"""

import os
import re
import json
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证frontmatter是否正确"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.strip().startswith("---"):
        errors.append("SKILL.md必须以---开头（frontmatter必须在第一行）")
        return False, errors

    # 提取frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("无法解析frontmatter块")
        return False, errors

    fm_content = match.group(1)

    # 检查必需字段
    if not re.search(r'^name:\s*\S+', fm_content, re.MULTILINE):
        errors.append("缺少name字段")
    if not re.search(r'^description:\s*\S+', fm_content, re.MULTILINE):
        errors.append("缺少description字段")

    return len(errors) == 0, errors

def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """验证_meta.json"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json文件不存在"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        if "id" not in meta:
            errors.append("缺少id字段")
        if "version" not in meta:
            errors.append("缺少version字段")
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json格式错误: {e}")

    return len(errors) == 0, errors

def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_path / f).exists():
            errors.append(f"缺少必需文件: {f}")

    # 检查可选目录
    optional_dirs = ["scripts", "references", "assets"]
    for d in optional_dirs:
        dir_path = skill_path / d
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{d}应该是目录而非文件")

    return len(errors) == 0, errors

def validate_content(skill_path: Path) -> tuple[bool, list[str]]:
    """验证内容完整性"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查五个优化标准部分是否都在
    required_sections = [
        "反馈问题",
        "解决方案原因及概述",
        "解决方案步骤",
        "整体规范性",
        "专业性"
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"缺少优化标准部分: {section}")

    # 检查关键要求是否存在
    key_requirements = [
        ("三要素", "反馈问题三要素（界面/功能、操作/场景、问题/诉求）"),
        ("不确定性词汇", "禁止使用的不确定性词汇（可能/应该/估计等）"),
        ("操作对象", "步骤必须包含的要素（操作对象、入口、检查点、处理动作）"),
        ("敏感信息", "敏感信息处理要求"),
        ("金蝶", "金蝶云星空标准术语")
    ]

    for keyword, desc in key_requirements:
        if keyword not in content:
            errors.append(f"缺少关键内容: {desc}")

    return len(errors) == 0, errors

def validate_quality_checklist(skill_path: Path) -> tuple[bool, list[str]]:
    """验证质量检查清单是否完整"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查清单是否包含所有必要的检查项
    checklist_items = [
        "质量检查清单",
        "反馈问题",
        "解决方案原因及概述",
        "解决方案步骤",
        "整体规范性",
        "专业性"
    ]

    for item in checklist_items:
        if item not in content:
            errors.append(f"质量检查清单缺少: {item}")

    return len(errors) == 0, errors

def main():
    skill_path = Path(__file__).parent.parent

    print("=" * 60)
    print("ERP知识优化技能 - 结构验证")
    print("=" * 60)

    all_valid = True

    # 验证frontmatter
    valid, errors = validate_frontmatter(skill_path)
    print(f"\n[1] Frontmatter验证: {'✓ 通过' if valid else '✗ 失败'}")
    if not valid:
        all_valid = False
        for e in errors:
            print(f"    - {e}")

    # 验证_meta.json
    valid, errors = validate_meta(skill_path)
    print(f"[2] _meta.json验证: {'✓ 通过' if valid else '✗ 失败'}")
    if not valid:
        all_valid = False
        for e in errors:
            print(f"    - {e}")

    # 验证结构
    valid, errors = validate_structure(skill_path)
    print(f"[3] 目录结构验证: {'✓ 通过' if valid else '✗ 失败'}")
    if not valid:
        all_valid = False
        for e in errors:
            print(f"    - {e}")

    # 验证内容
    valid, errors = validate_content(skill_path)
    print(f"[4] 内容完整性验证: {'✓ 通过' if valid else '✗ 失败'}")
    if not valid:
        all_valid = False
        for e in errors:
            print(f"    - {e}")

    # 验证质量清单
    valid, errors = validate_quality_checklist(skill_path)
    print(f"[5] 质量检查清单验证: {'✓ 通过' if valid else '✗ 失败'}")
    if not valid:
        all_valid = False
        for e in errors:
            print(f"    - {e}")

    print("\n" + "=" * 60)
    if all_valid:
        print("✓ 所有验证通过！技能结构符合规范")
        print("\n技能包含的优化标准:")
        print("  - 反馈问题优化标准（三要素、错误代码）")
        print("  - 解决方案原因及概述优化标准（确定性表述）")
        print("  - 解决方案步骤优化标准（操作四要素）")
        print("  - 整体规范性优化标准（敏感信息、口语化）")
        print("  - 专业性优化标准（金蝶术语、菜单路径）")
    else:
        print("✗ 验证失败，请修复上述问题")
    print("=" * 60)

    return 0 if all_valid else 1

if __name__ == "__main__":
    exit(main())
