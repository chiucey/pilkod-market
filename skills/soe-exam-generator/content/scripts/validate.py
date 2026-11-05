#!/usr/bin/env python3
"""
国企笔试备考资料生成器 - 技能验证脚本
验证SKILL.md的结构和内容是否符合规范
"""

import os
import re
import json
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """验证技能结构和内容"""
    results = {
        "passed": True,
        "errors": [],
        "warnings": [],
        "checks": []
    }

    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    meta_json = skill_path / "_meta.json"

    # 检查1：SKILL.md是否存在
    if not skill_md.exists():
        results["passed"] = False
        results["errors"].append("SKILL.md 文件不存在")
        return results

    # 检查2：_meta.json是否存在
    if not meta_json.exists():
        results["passed"] = False
        results["errors"].append("_meta.json 文件不存在")
        return results

    # 检查3：读取并验证SKILL.md
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 3.1 验证frontmatter格式
    if not content.startswith("---"):
        results["passed"] = False
        results["errors"].append("SKILL.md 必须以 YAML frontmatter (---) 开头")

    # 提取frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 检查必需字段
        if "name:" not in frontmatter:
            results["passed"] = False
            results["errors"].append("frontmatter 必须包含 name 字段")

        if "description:" not in frontmatter:
            results["passed"] = False
            results["errors"].append("frontmatter 必须包含 description 字段")

        # 验证description长度
        desc_match = re.search(r"description:\s*(.+?)(?:\n|$)", frontmatter)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                results["warnings"].append("description 建议至少20字符以确保触发准确性")

        # 验证name格式（连字符）
        name_match = re.search(r"name:\s*(.+?)(?:\n|$)", frontmatter)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                results["warnings"].append("name 建议使用小写字母和连字符格式")
    else:
        results["passed"] = False
        results["errors"].append("无法解析 YAML frontmatter")

    # 检查4：验证_meta.json格式
    try:
        with open(meta_json, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if "id" not in meta:
            results["passed"] = False
            results["errors"].append("_meta.json 必须包含 id 字段")

        if "version" not in meta:
            results["passed"] = False
            results["errors"].append("_meta.json 必须包含 version 字段")
    except json.JSONDecodeError as e:
        results["passed"] = False
        results["errors"].append(f"_meta.json 格式错误: {e}")

    # 检查5：验证内容结构
    required_sections = [
        "工作流程",
        "第一",
        "第二",
        "第三",
        "第四",
        "第五",
        "第六",
        "第七",
        "质量检查清单"
    ]

    for section in required_sections:
        if section not in content:
            results["warnings"].append(f"建议包含 '{section}' 相关内容")

    # 检查6：验证触发描述
    if "当用户" not in content and "when" not in content.lower():
        results["warnings"].append("建议在description中说明触发条件")

    results["checks"].append({
        "name": "SKILL.md存在",
        "passed": skill_md.exists()
    })
    results["checks"].append({
        "name": "_meta.json存在",
        "passed": meta_json.exists()
    })
    results["checks"].append({
        "name": "frontmatter格式正确",
        "passed": frontmatter_match is not None
    })
    results["checks"].append({
        "name": "必需字段完整",
        "passed": "name:" in frontmatter and "description:" in frontmatter
    })
    results["checks"].append({
        "name": "_meta.json格式正确",
        "passed": "id" in meta and "version" in meta
    })

    return results

def main():
    import sys

    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print("=" * 50)
    print("国企笔试备考资料生成器 - 技能验证")
    print("=" * 50)
    print()

    results = validate_skill(skill_path)

    print(f"技能路径: {skill_path}")
    print(f"验证结果: {'✓ 通过' if results['passed'] else '✗ 失败'}")
    print()

    if results["checks"]:
        print("检查项:")
        for check in results["checks"]:
            status = "✓" if check["passed"] else "✗"
            print(f"  {status} {check['name']}")
        print()

    if results["errors"]:
        print("错误:")
        for error in results["errors"]:
            print(f"  ✗ {error}")
        print()

    if results["warnings"]:
        print("警告:")
        for warning in results["warnings"]:
            print(f"  ! {warning}")
        print()

    sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()