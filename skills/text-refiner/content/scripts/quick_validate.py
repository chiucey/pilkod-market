#!/usr/bin/env python3
"""
文本精炼助手技能验证脚本
验证 SKILL.md 结构和 frontmatter 规范
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        return False, "SKILL.md 必须以 frontmatter --- 开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter"

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            return False, f"frontmatter 缺少必需字段: {field}"

    # 验证 name 格式（连字符、小写）
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 格式错误: {name}（应使用小写字母和连字符）"

    # 验证 description 包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
        if len(description) < 20:
            return False, "description 内容过短，应详细描述技能用途"

    return True, "frontmatter 验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 文件"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))

        # 检查必需字段
        if "id" not in meta:
            return False, "_meta.json 缺少 id 字段"

        if "version" not in meta:
            return False, "_meta.json 缺少 version 字段"

        # 验证 id 为整数
        if not isinstance(meta["id"], int):
            return False, "_meta.json 的 id 必须为整数"

        # 验证 version 格式
        if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            return False, "_meta.json 的 version 格式错误（应为 semver 格式）"

        return True, "_meta.json 验证通过"

    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 解析错误: {e}"


def validate_naming(skill_path: Path) -> tuple[bool, str]:
    """验证目录和文件命名"""
    # 检查目录名是否为英文
    dir_name = skill_path.name
    if not re.match(r'^[a-z0-9-]+$', dir_name):
        return False, f"目录名包含非英文字符: {dir_name}"

    # 检查 SKILL.md 中的 name 字段是否与目录名匹配
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)

    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if name != dir_name:
                return False, f"name 字段 ({name}) 与目录名 ({dir_name}) 不匹配"

    return True, "命名验证通过"


def main():
    # 默认检查当前目录下的技能
    skill_path = Path(__file__).parent.parent

    print(f"正在验证技能: {skill_path.name}")
    print("-" * 50)

    all_passed = True

    # 验证 frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证 _meta.json
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证命名
    passed, msg = validate_naming(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
