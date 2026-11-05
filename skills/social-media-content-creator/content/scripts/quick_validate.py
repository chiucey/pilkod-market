#!/usr/bin/env python3
"""
技能验证脚本 - 验证 SKILL.md 和 _meta.json 的结构和格式
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_skill_md(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证 SKILL.md 文件"""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查文件是否以 --- 开头（frontmatter）
    if not content.startswith("---"):
        errors.append("SKILL.md 必须以 --- 开头（frontmatter）")
        return False, errors

    # 提取 frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 frontmatter，请检查格式")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # 解析 YAML frontmatter
    try:
        # 简单的 YAML 解析
        frontmatter = {}
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()
    except Exception as e:
        errors.append(f"Frontmatter 解析失败: {e}")
        return False, errors

    # 检查必填字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Frontmatter 缺少必填字段: {field}")

    # 检查 name 格式（连字符格式）
    name = frontmatter.get("name", "")
    if name and not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(f"name 必须使用连字符格式（小写+中划线）: '{name}'")

    # 检查 name 与文件夹名是否匹配
    expected_name = skill_dir.name
    if name and name != expected_name:
        errors.append(f"name ('{name}') 与文件夹名 ('{expected_name}') 不匹配")

    # 检查 description 是否包含触发短语
    description = frontmatter.get("description", "")
    trigger_keywords = ["当用户", "触发", "使用", "请求", "说", "ask", "when"]
    has_trigger = any(keyword in description.lower() for keyword in trigger_keywords)
    if not has_trigger:
        errors.append("description 应包含触发短语（如'当用户说...'或'Use when...'）")

    # 检查 frontmatter 后是否是 H1 标题（不应以 # 标题开头，可用 H2 替代）
    body_start = content.find("\n---", 3) + 4
    body = content[body_start:].lstrip()
    if body.startswith("# "):
        errors.append("Frontmatter 后的第一个内容不应是 H1 标题（建议使用 H2）")

    return len(errors) == 0, errors


def validate_meta_json(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json 文件"""
    errors = []
    meta_json = skill_dir / "_meta.json"

    if not meta_json.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON 解析失败: {e}"]

    # 检查必填字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必填字段: {field}")

    # 检查 version 格式（语义化版本）
    version = meta.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append(f"version 应使用语义化版本格式 (x.y.z): '{version}'")

    # 检查 id 格式（应为十六进制字符串）
    skill_id = meta.get("id", "")
    if skill_id and not re.match(r"^[a-f0-9]{32}$", skill_id):
        errors.append(f"id 应为32位十六进制字符串: '{skill_id}'")

    return len(errors) == 0, errors


def validate_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查目录名是否为英文
    dir_name = skill_dir.name
    if not re.match(r"^[a-z0-9\-]+$", dir_name):
        errors.append(f"文件夹名应使用英文（连字符格式）: '{dir_name}'")

    # 检查是否有非法文件
    forbidden_patterns = [r"\.pem$", r"\.key$", r"\.env$", r"secret"]
    for file_path in skill_dir.rglob("*"):
        if file_path.is_file():
            for pattern in forbidden_patterns:
                if re.search(pattern, str(file_path), re.IGNORECASE):
                    errors.append(f"发现潜在敏感文件: {file_path}")

    return len(errors) == 0, errors


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_dir = Path.cwd()
    else:
        skill_dir = Path(sys.argv[1])

    print(f"验证技能目录: {skill_dir}")
    print("=" * 50)

    all_passed = True

    # 1. 验证 SKILL.md
    print("\n[1/3] 验证 SKILL.md...")
    passed, errors = validate_skill_md(skill_dir)
    if passed:
        print("  ✓ SKILL.md 验证通过")
    else:
        print("  ✗ SKILL.md 验证失败:")
        for error in errors:
            print(f"    - {error}")
        all_passed = False

    # 2. 验证 _meta.json
    print("\n[2/3] 验证 _meta.json...")
    passed, errors = validate_meta_json(skill_dir)
    if passed:
        print("  ✓ _meta.json 验证通过")
    else:
        print("  ✗ _meta.json 验证失败:")
        for error in errors:
            print(f"    - {error}")
        all_passed = False

    # 3. 验证目录结构
    print("\n[3/3] 验证目录结构...")
    passed, errors = validate_structure(skill_dir)
    if passed:
        print("  ✓ 目录结构验证通过")
    else:
        print("  ✗ 目录结构验证失败:")
        for error in errors:
            print(f"    - {error}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证错误，请修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
