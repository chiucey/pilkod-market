#!/usr/bin/env python3
"""
技术交底书撰写技能 - 快速验证脚本
验证 SKILL.md 和 _meta.json 的基本完整性
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """验证技能文件结构和内容"""
    results = {
        "passed": True,
        "errors": [],
        "warnings": []
    }

    skill_dir = Path(skill_path)

    # 1. 检查 _meta.json
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        results["passed"] = False
        results["errors"].append("Missing _meta.json")
    else:
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "id" not in meta:
                results["passed"] = False
                results["errors"].append("_meta.json missing 'id' field")
            if "version" not in meta:
                results["passed"] = False
                results["errors"].append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            results["passed"] = False
            results["errors"].append(f"Invalid _meta.json: {e}")

    # 2. 检查 SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        results["passed"] = False
        results["errors"].append("Missing SKILL.md")
        return results

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查 frontmatter 是否在第一行
    if not content.startswith("---"):
        results["passed"] = False
        results["errors"].append("SKILL.md must start with frontmatter (---)")

    # 解析 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        results["passed"] = False
        results["errors"].append("Cannot parse frontmatter")
        return results

    frontmatter = frontmatter_match.group(1)
    lines = frontmatter.split("\n")

    # 检查必需字段
    has_name = any(line.strip().startswith("name:") for line in lines)
    has_description = any(line.strip().startswith("description:") for line in lines)

    if not has_name:
        results["passed"] = False
        results["errors"].append("Frontmatter missing 'name' field")

    if not has_description:
        results["passed"] = False
        results["errors"].append("Frontmatter missing 'description' field")

    # 提取 name 值进行验证
    name_match = re.search(r'^name:\s*(.+?)\s*$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # 检查是否为连字符格式
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            results["warnings"].append(f"name '{name}' should use hyphen-case format")

    # 检查工作流程章节
    required_sections = [
        "阶段1：材料阅读与理解",
        "阶段2：材料充分性评估",
        "阶段3：领域分析与关键信息识别",
        "阶段4：技术交底书撰写",
        "阶段5：质量评估与迭代修改",
        "阶段6：输出交付"
    ]

    for section in required_sections:
        if section not in content:
            results["warnings"].append(f"Missing recommended section: {section}")

    return results

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    results = validate_skill(skill_path)

    print(f"\n{'='*50}")
    print(f"技能验证结果: {'✓ 通过' if results['passed'] else '✗ 失败'}")
    print(f"{'='*50}\n")

    if results["errors"]:
        print("错误:")
        for err in results["errors"]:
            print(f"  - {err}")

    if results["warnings"]:
        print("\n警告:")
        for warn in results["warnings"]:
            print(f"  - {warn}")

    if results["passed"] and not results["warnings"]:
        print("所有检查项均已通过！")

    sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()
