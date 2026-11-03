#!/usr/bin/env python3
"""
快速验证脚本 - 检查科学家代理技能的结构和质量
"""
import os
import re
import json
from pathlib import Path

def validate_skill(path: str) -> dict:
    """验证技能结构"""
    results = {
        "passed": True,
        "errors": [],
        "warnings": []
    }

    skill_path = Path(path)

    # 1. 检查目录结构
    if not skill_path.exists():
        results["passed"] = False
        results["errors"].append("技能目录不存在")
        return results

    # 2. 检查 SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        results["passed"] = False
        results["errors"].append("SKILL.md 不存在")
        return results

    content = skill_md.read_text(encoding="utf-8")

    # 3. Frontmatter 必须在第一行
    if not content.startswith("---"):
        results["passed"] = False
        results["errors"].append("SKILL.md 必须以 frontmatter (---) 开头，不能有标题在前面")

    # 4. 解析 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        results["passed"] = False
        results["errors"].append("无法解析 frontmatter")
        return results

    frontmatter_text = frontmatter_match.group(1)

    # 5. 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            results["passed"] = False
            results["errors"].append(f"Frontmatter 缺少必需字段: {field}")

    # 6. 验证 name 格式（连字符，小写）
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            results["passed"] = False
            results["errors"].append(f"name 必须使用小写字母和连字符: {name_value}")
        if len(name_value) > 64:
            results["passed"] = False
            results["errors"].append(f"name 长度不能超过64字符")

    # 7. 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        results["passed"] = False
        results["errors"].append("_meta.json 不存在")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                results["passed"] = False
                results["errors"].append("_meta.json 缺少 id 字段")
            if "version" not in meta:
                results["passed"] = False
                results["errors"].append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            results["passed"] = False
            results["errors"].append("_meta.json 格式错误")

    # 8. 检查内容是否包含核心特质
    if "唯物辩证" not in content:
        results["warnings"].append("SKILL.md 未包含唯物辩证法相关描述")
    if "冷静" not in content and "克制" not in content:
        results["warnings"].append("SKILL.md 未包含情绪特征相关描述")
    if "严谨" not in content and "客观" not in content:
        results["warnings"].append("SKILL.md 未包含语言风格相关描述")

    return results

if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/scientist-agent"
    result = validate_skill(path)

    print("=" * 50)
    print("科学家代理技能验证结果")
    print("=" * 50)

    if result["errors"]:
        print("\n❌ 错误:")
        for err in result["errors"]:
            print(f"  - {err}")

    if result["warnings"]:
        print("\n⚠️ 警告:")
        for warn in result["warnings"]:
            print(f"  - {warn}")

    if result["passed"]:
        print("\n✅ 验证通过!")
    else:
        print("\n❌ 验证失败")
        sys.exit(1)
