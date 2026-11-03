#!/usr/bin/env python3
"""
政策投资机会雷达技能验证脚本
验证 SKILL.md 的 frontmatter 和结构完整性
"""

import os
import re
import sys

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 frontmatter 格式"""
    errors = []
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return False, ["SKILL.md 文件不存在"]

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查文件是否以 --- 开头
    if not content.strip().startswith("---"):
        errors.append("SKILL.md 必须以 frontmatter --- 开头")
        return False, errors

    # 提取 frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 frontmatter")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf"^{field}:", frontmatter, re.MULTILINE):
            errors.append(f"缺少必需字段: {field}")

    # 检查 name 格式
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"name 必须使用小写字母、数字和连字符: {name}")

    # 检查 description 不为空
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            errors.append("description 必须至少包含 10 个字符")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, ["_meta.json 文件不存在"]

    import json
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON 解析错误: {e}"]

    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"缺少必需字段: {field}")

    return len(errors) == 0, errors


def validate_naming(skill_path: str) -> tuple[bool, list[str]]:
    """验证文件夹名称与 frontmatter name 一致"""
    errors = []

    # 读取 frontmatter
    skill_md = os.path.join(skill_path, "SKILL.md")
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        if name_match:
            frontmatter_name = name_match.group(1).strip()

            # 获取文件夹名称
            folder_name = os.path.basename(skill_path)
            if frontmatter_name != folder_name:
                errors.append(f"名称不匹配: folder='{folder_name}', frontmatter name='{frontmatter_name}'")

    return len(errors) == 0, errors


def main():
    # 默认技能路径
    default_path = "/workspace/temp-skills/policy-investment-radar"

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    elif __name__ == "__main__":
        # 脚本自身在 scripts/ 下，需要回退一级
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_path = os.path.dirname(script_dir)
    else:
        skill_path = default_path

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_valid = True

    # 验证 frontmatter
    valid, errors = validate_frontmatter(skill_path)
    if valid:
        print("✓ Frontmatter 验证通过")
    else:
        print("✗ Frontmatter 验证失败:")
        for err in errors:
            print(f"  - {err}")
        all_valid = False

    # 验证 _meta.json
    valid, errors = validate_meta_json(skill_path)
    if valid:
        print("✓ _meta.json 验证通过")
    else:
        print("✗ _meta.json 验证失败:")
        for err in errors:
            print(f"  - {err}")
        all_valid = False

    # 验证命名一致性
    valid, errors = validate_naming(skill_path)
    if valid:
        print("✓ 命名一致性验证通过")
    else:
        print("✗ 命名一致性验证失败:")
        for err in errors:
            print(f"  - {err}")
        all_valid = False

    print("-" * 50)
    if all_valid:
        print("✅ 所有验证通过")
        return 0
    else:
        print("❌ 验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
