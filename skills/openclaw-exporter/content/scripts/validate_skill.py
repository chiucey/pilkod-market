#!/usr/bin/env python3
"""快速验证脚本 - 检查导出器技能结构"""

import os
import json
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """验证技能结构"""
    skill_dir = Path(skill_path)
    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        file_path = skill_dir / filename
        if not file_path.exists():
            results["valid"] = False
            results["errors"].append(f"缺少必需文件: {filename}")

    # 验证 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            results["valid"] = False
            results["errors"].append("SKILL.md 必须以 frontmatter 开头")
        else:
            lines = content.split('\n')
            if len(lines) < 3 or '---' not in content[3:]:
                results["valid"] = False
                results["errors"].append("frontmatter 格式不正确")

    # 验证 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if "id" not in meta:
                results["warnings"].append("_meta.json 缺少 'id' 字段")
            if "version" not in meta:
                results["warnings"].append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            results["valid"] = False
            results["errors"].append(f"_meta.json 格式错误: {e}")

    # 检查目录结构
    for subdir in ["scripts", "references", "assets"]:
        subdir_path = skill_dir / subdir
        if subdir_path.exists() and not list(subdir_path.iterdir()):
            results["warnings"].append(f"{subdir}/ 目录为空")

    return results

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    results = validate_skill(skill_path)

    if results["valid"]:
        print("✓ 验证通过")
    else:
        print("✗ 验证失败")
        for error in results["errors"]:
            print(f"  错误: {error}")

    if results["warnings"]:
        print("\n警告:")
        for warning in results["warnings"]:
            print(f"  - {warning}")

    sys.exit(0 if results["valid"] else 1)
