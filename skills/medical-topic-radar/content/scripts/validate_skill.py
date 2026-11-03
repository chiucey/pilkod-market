#!/usr/bin/env python3
"""
医疗科普选题雷达技能验证脚本
验证SKILL.md的结构和内容是否符合规范
"""

import os
import re
import json
import sys

def validate_skill(skill_path):
    """验证技能文件结构"""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }

    # 读取SKILL.md
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        results["failed"].append("SKILL.md 文件不存在")
        return results

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 验证1: Frontmatter必须在第一行
    if not content.startswith("---"):
        results["failed"].append("Frontmatter必须从第一行开始（以---开头）")
    else:
        results["passed"].append("Frontmatter格式正确")

    # 验证2: Frontmatter必须有name和description
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)

    if not name_match:
        results["failed"].append("Frontmatter缺少name字段")
    else:
        results["passed"].append(f"name字段存在: {name_match.group(1)}")

    if not desc_match:
        results["failed"].append("Frontmatter缺少description字段")
    else:
        results["passed"].append("description字段存在")

    # 验证3: 不能以markdown标题开头（frontmatter之后的第一行可以是标题）
    # frontmatter从第一行---开始，到第二个---结束
    lines = content.split("\n")
    frontmatter_end = -1
    first_dash_count = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            first_dash_count += 1
            if first_dash_count == 1:
                continue  # 跳过开始的---
            elif first_dash_count == 2:
                frontmatter_end = i
                break

    # 检查frontmatter之后的第一行（index > frontmatter_end）是否包含标题
    # 这是正确的行为，不需要检查

    # 验证4: 包含5大选题来源
    required_sources = [
        "大众社会热点",
        "医疗学术热点",
        "季节性疾病趋势",
        "中高净值人群健康焦虑",
        "Longevity"
    ]
    for source in required_sources:
        if source in content:
            results["passed"].append(f"包含选题来源: {source}")
        else:
            results["failed"].append(f"缺少选题来源: {source}")

    # 验证5: 包含输出结构
    required_fields = [
        "【热点事件】",
        "【医学切入点】",
        "【内容标题建议】",
        "【传播评分】",
        "【建议动作】"
    ]
    for field in required_fields:
        if field in content:
            results["passed"].append(f"包含输出字段: {field}")
        else:
            results["failed"].append(f"缺少输出字段: {field}")

    # 验证6: _meta.json存在且有效
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        results["failed"].append("_meta.json文件不存在")
    else:
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "id" in meta and "version" in meta:
                results["passed"].append("_meta.json包含id和version")
            else:
                results["failed"].append("_meta.json缺少id或version字段")
        except json.JSONDecodeError:
            results["failed"].append("_meta.json格式无效")

    return results

def print_results(results):
    """打印验证结果"""
    print("\n" + "="*50)
    print("验证结果")
    print("="*50)

    if results["passed"]:
        print("\n✅ 通过项:")
        for item in results["passed"]:
            print(f"  ✓ {item}")

    if results["warnings"]:
        print("\n⚠️ 警告项:")
        for item in results["warnings"]:
            print(f"  ⚠ {item}")

    if results["failed"]:
        print("\n❌ 失败项:")
        for item in results["failed"]:
            print(f"  ✗ {item}")
        return False
    else:
        print("\n🎉 所有验证项通过!")
        return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    results = validate_skill(skill_path)
    success = print_results(results)
    sys.exit(0 if success else 1)
