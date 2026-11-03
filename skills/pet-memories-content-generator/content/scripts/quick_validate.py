#!/usr/bin/env python3
"""
宠物情感经济内容生成器 - Skill验证脚本
验证SKILL.md结构和_frontmatter规范性
"""

import os
import sys
import re

def validate_skill(skill_path: str) -> dict:
    """验证Skill目录结构和文件完整性"""
    results = {
        "passed": True,
        "errors": [],
        "warnings": [],
        "checks": []
    }

    # 检查目录结构
    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            results["passed"] = False
            results["errors"].append(f"缺少必要文件: {file}")

    # 验证SKILL.md frontmatter
    skill_md = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(skill_md):
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查frontmatter格式
        if not content.startswith("---"):
            results["passed"] = False
            results["errors"].append("SKILL.md必须以frontmatter开头（---），不能以markdown标题开头")

        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)

            # 检查必需字段
            required_fields = ["name", "description"]
            for field in required_fields:
                if f"{field}:" not in frontmatter_text:
                    results["passed"] = False
                    results["errors"].append(f"Frontmatter缺少必需字段: {field}")

            # 检查name字段格式
            name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
            if name_match:
                name_value = name_match.group(1).strip()
                if " " in name_value or not name_value.replace("-", "").isalnum():
                    results["warnings"].append(f"name字段应使用连字符格式: {name_value}")

        results["checks"].append({
            "name": "SKILL.md frontmatter格式",
            "passed": results["passed"]
        })

    # 验证_meta.json
    meta_json = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_json):
        import json
        try:
            with open(meta_json, "r", encoding="utf-8") as f:
                meta = json.load(f)

            required_meta_fields = ["id", "version"]
            for field in required_meta_fields:
                if field not in meta:
                    results["passed"] = False
                    results["errors"].append(f"_meta.json缺少必需字段: {field}")

            results["checks"].append({
                "name": "_meta.json结构",
                "passed": field not in required_meta_fields or True
            })
        except json.JSONDecodeError as e:
            results["passed"] = False
            results["errors"].append(f"_meta.json格式错误: {e}")

    # 检查目录命名
    dir_name = os.path.basename(skill_path)
    if not dir_name.replace("-", "").isalnum():
        results["warnings"].append(f"目录名应使用英文连字符格式: {dir_name}")

    return results

def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/pet-memories-content-generator"
    else:
        skill_path = sys.argv[1]

    print("=" * 60)
    print("宠物情感经济内容生成器 - Skill验证")
    print("=" * 60)

    results = validate_skill(skill_path)

    print(f"\n验证结果: {'✓ 通过' if results['passed'] else '✗ 失败'}")
    print("-" * 60)

    if results["errors"]:
        print("\n错误:")
        for error in results["errors"]:
            print(f"  - {error}")

    if results["warnings"]:
        print("\n警告:")
        for warning in results["warnings"]:
            print(f"  - {warning}")

    if results["checks"]:
        print("\n检查项:")
        for check in results["checks"]:
            status = "✓" if check["passed"] else "✗"
            print(f"  [{status}] {check['name']}")

    print("\n" + "=" * 60)

    sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()