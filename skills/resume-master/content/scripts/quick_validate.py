#!/usr/bin/env python3
"""
简历大师技能验证脚本
验证SKILL.md的结构和内容是否符合规范
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证frontmatter格式和必填字段"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查frontmatter是否在文件开头
    if not content.startswith("---"):
        errors.append("Frontmatter must start at the beginning of the file (first line must be '---')")
        return False, errors

    # 提取frontmatter
    lines = content.split("\n")
    # 第一行应该是 ---
    if len(lines) < 4 or lines[0].strip() != "---":
        errors.append("Frontmatter must start with '---' at first line")
        return False, errors

    # 找到closing ---
    end_idx = -1
    for i, line in enumerate(lines[2:], start=2):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("Frontmatter missing closing '---'")
        return False, errors

    frontmatter_text = "\n".join(lines[1:end_idx+1])

    # 检查必填字段
    if 'name:' not in frontmatter_text:
        errors.append("Frontmatter missing 'name' field")

    if 'description:' not in frontmatter_text:
        errors.append("Frontmatter missing 'description' field")

    # 检查name格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"name should use hyphen-case format: {name_value}")

    # 检查description是否包含触发短语
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append("description should be at least 20 characters for good trigger matching")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []

    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        file_path = Path(skill_path) / file
        if not file_path.exists():
            errors.append(f"Required file missing: {file}")

    # 检查_meta.json格式
    meta_path = Path(skill_path) / "_meta.json"
    if meta_path.exists():
        import json
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    return len(errors) == 0, errors


def validate_content(skill_path: str) -> tuple[bool, list[str]]:
    """验证SKILL.md内容质量"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否有markdown标题
    if not re.search(r'^#\s+', content, re.MULTILINE):
        errors.append("SKILL.md should contain at least one markdown heading")

    # 检查是否有工作流程说明
    if "工作流程" not in content and "workflow" not in content.lower():
        errors.append("SKILL.md should contain workflow description")

    return len(errors) == 0, errors


def main():
    skill_path = "/workspace/temp-skills/resume-master"

    print("=" * 50)
    print("简历大师技能 - 验证检查")
    print("=" * 50)

    all_passed = True

    # 验证frontmatter
    print("\n[1] 验证 Frontmatter...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("    ✓ Frontmatter 格式正确")
    else:
        print("    ✗ Frontmatter 验证失败:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # 验证结构
    print("\n[2] 验证目录结构...")
    passed, errors = validate_structure(skill_path)
    if passed:
        print("    ✓ 目录结构正确")
    else:
        print("    ✗ 目录结构验证失败:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    # 验证内容
    print("\n[3] 验证内容质量...")
    passed, errors = validate_content(skill_path)
    if passed:
        print("    ✓ 内容质量符合要求")
    else:
        print("    ✗ 内容质量验证失败:")
        for e in errors:
            print(f"      - {e}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
