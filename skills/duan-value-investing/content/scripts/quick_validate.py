#!/usr/bin/env python3
"""
段永平价值投资技能验证脚本
验证技能结构、frontmatter格式和命名规范
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证SKILL.md的frontmatter格式"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查frontmatter是否在文件开头
    if not content.startswith("---"):
        errors.append("Frontmatter必须从文件第一行开始（以---开头）")
        return False, errors

    # 提取frontmatter
    frontmatter_end = content.find("---", 3)
    if frontmatter_end == -1:
        errors.append("Frontmatter未正确闭合（缺少第二个---）")
        return False, errors

    frontmatter = content[3:frontmatter_end].strip()

    # 检查必填字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(f"^{field}:", frontmatter, re.MULTILINE):
            errors.append(f"缺少必填字段: {field}")

    # 验证name格式（连字符、英文）
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name字段格式错误，应使用小写字母和连字符: {name}")
        if len(name) > 64:
            errors.append(f"name字段长度不能超过64字符: {len(name)}")

    # 检查description是否包含触发短语
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("description字段内容过短，应包含详细的触发短语说明")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证_meta.json文件"""
    import json
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json文件不存在"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json格式错误: {e}"]

    # 检查必填字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"缺少必填字段: {field}")

    # 验证id类型
    if "id" in meta:
        if not isinstance(meta["id"], int):
            errors.append("id字段必须是整数类型")

    # 验证version格式
    if "version" in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            errors.append("version字段格式错误，应为x.y.z格式")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    skill_name = Path(skill_path).name

    # 验证技能文件夹名称为英文和连字符
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"技能文件夹名称应使用小写字母和连字符: {skill_name}")

    # 验证SKILL.md存在
    if not Path(skill_path, "SKILL.md").exists():
        errors.append("SKILL.md文件不存在")

    # 验证_meta.json存在
    if not Path(skill_path, "_meta.json").exists():
        errors.append("_meta.json文件不存在")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/duan-value-investing"
    else:
        skill_path = sys.argv[1]

    print(f"正在验证技能: {skill_path}")
    print("-" * 50)

    all_valid = True

    # 验证目录结构
    valid, errors = validate_directory_structure(skill_path)
    if not valid:
        all_valid = False
        print("❌ 目录结构验证失败:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✓ 目录结构验证通过")

    # 验证frontmatter
    valid, errors = validate_frontmatter(skill_path)
    if not valid:
        all_valid = False
        print("❌ Frontmatter验证失败:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✓ Frontmatter验证通过")

    # 验证_meta.json
    valid, errors = validate_meta_json(skill_path)
    if not valid:
        all_valid = False
        print("❌ _meta.json验证失败:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✓ _meta.json验证通过")

    print("-" * 50)
    if all_valid:
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 验证失败，请修复以上问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
