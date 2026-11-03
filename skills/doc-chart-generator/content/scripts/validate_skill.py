#!/usr/bin/env python3
"""
技能验证脚本 - 检查 SKILL.md 和 _meta.json 的格式正确性
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 SKILL.md frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.strip().startswith("---"):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter
    lines = content.split("\n")
    if len(lines) < 3:
        return False, "Frontmatter 格式不正确"

    # 解析 frontmatter
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

    # 检查必需的字段
    frontmatter_text = "\n".join(frontmatter_lines)
    if "name:" not in frontmatter_text:
        return False, "Frontmatter 必须包含 name 字段"

    if "description:" not in frontmatter_text:
        return False, "Frontmatter 必须包含 description 字段"

    # 检查 name 格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 必须使用小写字母和连字符: {name}"

    return True, "Frontmatter 验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 格式"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json 格式错误: {e}"

    # 检查必需字段
    if "id" not in meta:
        return False, "_meta.json 必须包含 id 字段"

    if "version" not in meta:
        return False, "_meta.json 必须包含 version 字段"

    # 验证 id 是数字字符串
    if not isinstance(meta["id"], (int, str)):
        return False, "id 必须是数字或字符串"

    # 验证 version 格式
    version = meta["version"]
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"version 必须符合语义化版本格式: {version}"

    return True, "_meta.json 验证通过"


def validate_structure(skill_path: Path) -> tuple[bool, str]:
    """验证目录结构"""
    # 检查基本目录
    expected_dirs = ["scripts", "references", "assets"]
    for dir_name in expected_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            # 这些是可选的，所以只记录
            pass

    return True, "目录结构验证通过"


def validate_readme_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 SKILL.md 中没有在 frontmatter 前有标题"""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # 检查在第一个 --- 之前是否有 markdown 标题
    first_dash = content.find("---")
    if first_dash == -1:
        return False, "未找到 frontmatter 分隔符 ---"

    before_frontmatter = content[:first_dash]

    # 检查是否有 # 标题
    if re.search(r'^#+\s+\w+', before_frontmatter, re.MULTILINE):
        return False, "Frontmatter 之前不能有 markdown 标题 (#)"

    return True, "无前导标题验证通过"


def main():
    """主函数"""
    # 默认检查当前目录下的技能
    skill_path = Path(__file__).parent.parent

    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 1. 验证 frontmatter
    passed, msg = validate_frontmatter(skill_path)
    status = "✓" if passed else "✗"
    print(f"{status} Frontmatter: {msg}")
    all_passed = all_passed and passed

    # 2. 验证无前导标题
    passed, msg = validate_readme_frontmatter(skill_path)
    status = "✓" if passed else "✗"
    print(f"{status} 前导标题检查: {msg}")
    all_passed = all_passed and passed

    # 3. 验证 _meta.json
    passed, msg = validate_meta_json(skill_path)
    status = "✓" if passed else "✗"
    print(f"{status} _meta.json: {msg}")
    all_passed = all_passed and passed

    # 4. 验证目录结构
    passed, msg = validate_structure(skill_path)
    status = "✓" if passed else "✗"
    print(f"{status} 目录结构: {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1


if __name__ == "__main__":
    sys.exit(main())
