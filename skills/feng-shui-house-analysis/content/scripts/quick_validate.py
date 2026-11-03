#!/usr/bin/env python3
"""风水技能验证脚本"""

import os
import re
import json
import sys
from pathlib import Path

def validate_feng_shui_skill(base_path: str) -> dict:
    """验证风水技能结构和内容"""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }

    base = Path(base_path)

    # 检查必要文件
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        file_path = base / f
        if file_path.exists():
            results["passed"].append(f"✓ 必要文件存在: {f}")
        else:
            results["failed"].append(f"✗ 缺少必要文件: {f}")

    # 检查_meta.json
    meta_path = base / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if "id" in meta and "version" in meta:
                results["passed"].append("✓ _meta.json 包含 id 和 version")
            else:
                results["failed"].append("✗ _meta.json 缺少 id 或 version")

            # 验证id是整数
            if "id" in meta:
                try:
                    int(meta["id"])
                    results["passed"].append(f"✓ _meta.json id 格式正确: {meta['id']}")
                except ValueError:
                    results["failed"].append(f"✗ _meta.json id 不是整数: {meta['id']}")
        except json.JSONDecodeError as e:
            results["failed"].append(f"✗ _meta.json JSON 解析错误: {e}")
    else:
        results["failed"].append("✗ _meta.json 不存在")

    # 检查SKILL.md
    skill_path = base / "SKILL.md"
    if skill_path.exists():
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end != -1:
                frontmatter = content[3:frontmatter_end].strip()

                # 检查name字段
                if 'name:' in frontmatter:
                    name_match = re.search(r'name:\s*([^\n]+)', frontmatter)
                    if name_match:
                        name = name_match.group(1).strip()
                        # 验证name与目录名匹配
                        expected_name = base.name
                        if name == expected_name:
                            results["passed"].append(f"✓ SKILL.md name 与目录名匹配: {name}")
                        else:
                            results["failed"].append(f"✗ SKILL.md name 与目录名不匹配: {name} vs {expected_name}")
                else:
                    results["failed"].append("✗ SKILL.md frontmatter 缺少 name 字段")

                # 检查description字段
                if 'description:' in frontmatter:
                    desc_match = re.search(r'description:\s*([^\n]+)', frontmatter)
                    if desc_match:
                        results["passed"].append("✓ SKILL.md frontmatter 包含 description")
                    else:
                        results["failed"].append("✗ SKILL.md description 格式错误")
                else:
                    results["failed"].append("✗ SKILL.md frontmatter 缺少 description 字段")

                results["passed"].append("✓ SKILL.md frontmatter 格式正确")
            else:
                results["failed"].append("✗ SKILL.md frontmatter 格式错误")
        else:
            results["failed"].append("✗ SKILL.md 必须以 YAML frontmatter 开头")

        # 检查内容
        required_sections = [
            "工作流程",
            "步骤",
            "化解",
            "报告"
        ]

        for section in required_sections:
            if section in content:
                results["passed"].append(f"✓ SKILL.md 包含必要内容: {section}")
            else:
                results["warnings"].append(f"⚠ SKILL.md 建议添加: {section}")
    else:
        results["failed"].append("✗ SKILL.md 不存在")

    # 检查目录结构
    if (base / "references").exists():
        results["passed"].append("✓ 包含 references 目录")
        ref_files = list((base / "references").glob("*"))
        if ref_files:
            results["passed"].append(f"✓ references 包含 {len(ref_files)} 个文件")
    else:
        results["warnings"].append("⚠ 建议添加 references 目录")

    return results

def print_results(results: dict):
    """打印验证结果"""
    print("\n" + "="*50)
    print("风水技能验证结果")
    print("="*50 + "\n")

    if results["passed"]:
        print("✅ 通过项:")
        for item in results["passed"]:
            print(f"  {item}")

    if results["warnings"]:
        print("\n⚠️ 警告项:")
        for item in results["warnings"]:
            print(f"  {item}")

    if results["failed"]:
        print("\n❌ 失败项:")
        for item in results["failed"]:
            print(f"  {item}")

    print("\n" + "="*50)
    total = len(results["passed"]) + len(results["failed"])
    if results["failed"]:
        print(f"❌ 验证失败: {len(results['failed'])}/{total} 项")
        return False
    else:
        print(f"✅ 验证通过!")
        return True

if __name__ == "__main__":
    skill_path = "/workspace/temp-skills/feng-shui-house-analysis"
    results = validate_feng_shui_skill(skill_path)
    success = print_results(results)
    sys.exit(0 if success else 1)
