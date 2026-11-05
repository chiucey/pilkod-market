#!/usr/bin/env python3
"""
技能验证脚本 - 快速检查技能结构和格式
"""
import os
import re
import json
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """验证技能目录结构和内容"""
    results = {
        "passed": True,
        "errors": [],
        "warnings": []
    }

    skill_path = Path(skill_path)

    # 1. 检查目录结构
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_path / f).exists():
            results["errors"].append(f"缺少必需文件: {f}")
            results["passed"] = False

    # 2. 验证SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 检查frontmatter格式
        if not content.startswith("---"):
            results["errors"].append("SKILL.md必须以frontmatter开头（---）")
            results["passed"] = False

        # 提取frontmatter
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx > 0:
                fm_text = content[3:end_idx].strip()
                fm = {}
                for line in fm_text.split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        fm[key.strip()] = val.strip()

                # 检查必需字段
                for field in ["name", "description"]:
                    if field not in fm:
                        results["errors"].append(f"frontmatter缺少必需字段: {field}")
                        results["passed"] = False
            else:
                results["errors"].append("frontmatter格式错误（未找到闭合---）")
                results["passed"] = False
        else:
            # 尝试另一种方式
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                results["errors"].append("无法解析frontmatter")
                results["passed"] = False

        # 检查name格式
        if "name" in fm:
            if not re.match(r'^[a-z0-9-]+$', fm["name"]):
                results["errors"].append(f"name格式错误: {fm['name']}（应使用小写字母、数字、连字符）")
                results["passed"] = False
            if fm["name"] != skill_path.name:
                results["warnings"].append(f"name字段与目录名不一致: {fm['name']} vs {skill_path.name}")
    else:
        results["warnings"].append("SKILL.md不存在，跳过内容验证")

    # 3. 验证_meta.json
    meta_json = skill_path / "_meta.json"
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            for field in ["id", "version"]:
                if field not in meta:
                    results["errors"].append(f"_meta.json缺少字段: {field}")
                    results["passed"] = False
            if "version" in meta:
                if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
                    results["errors"].append(f"version格式错误: {meta['version']}（应为x.y.z）")
                    results["passed"] = False
        except json.JSONDecodeError as e:
            results["errors"].append(f"_meta.json解析失败: {e}")
            results["passed"] = False

    return results

def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    results = validate_skill(skill_path)

    print(f"\n{'='*50}")
    print(f"验证结果: {'✓ 通过' if results['passed'] else '✗ 失败'}")
    print(f"{'='*50}")

    if results["errors"]:
        print("\n错误:")
        for e in results["errors"]:
            print(f"  - {e}")

    if results["warnings"]:
        print("\n警告:")
        for w in results["warnings"]:
            print(f"  - {w}")

    sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()
