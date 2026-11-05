#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能文件结构和内容规范
"""
import os
import re
import yaml
import json
from pathlib import Path

def validate_skill(path: str) -> dict:
    """验证技能结构和内容"""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }

    skill_path = Path(path)

    # 1. 检查目录结构
    if not skill_path.exists():
        results["failed"].append(f"技能目录不存在: {path}")
        return results

    # 2. 检查 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        results["failed"].append("SKILL.md 文件不存在")
    else:
        # 读取并验证 frontmatter
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查 frontmatter 位置（必须在第一行）
        if content.strip().startswith("#"):
            results["failed"].append("SKILL.md 不能以 markdown 标题(#) 开头，必须以 YAML frontmatter 开头")
        elif not content.startswith("---"):
            results["failed"].append("SKILL.md 必须以 YAML frontmatter (---) 开头")
        else:
            results["passed"].append("SKILL.md frontmatter 位置正确")

        # 解析 frontmatter
        try:
            # 提取 frontmatter 内容
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))

                # 检查必填字段
                if "name" not in frontmatter:
                    results["failed"].append("frontmatter 缺少 'name' 字段")
                elif not frontmatter["name"]:
                    results["failed"].append("frontmatter 'name' 字段不能为空")
                else:
                    results["passed"].append("frontmatter 'name' 字段存在")

                if "description" not in frontmatter:
                    results["failed"].append("frontmatter 缺少 'description' 字段")
                elif len(frontmatter["description"]) < 10:
                    results["failed"].append("frontmatter 'description' 字段内容过短（建议至少10字符）")
                else:
                    results["passed"].append("frontmatter 'description' 字段存在且长度符合要求")
            else:
                results["failed"].append("无法解析 YAML frontmatter")
        except yaml.YAMLError as e:
            results["failed"].append(f"YAML 解析错误: {str(e)}")

    # 3. 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        results["failed"].append("_meta.json 文件不存在")
    else:
        try:
            with open(meta_json, "r", encoding="utf-8") as f:
                meta = json.load(f)

            if "id" not in meta:
                results["failed"].append("_meta.json 缺少 'id' 字段")
            else:
                results["passed"].append("_meta.json 'id' 字段存在")

            if "version" not in meta:
                results["failed"].append("_meta.json 缺少 'version' 字段")
            else:
                results["passed"].append("_meta.json 'version' 字段存在")

        except json.JSONDecodeError as e:
            results["failed"].append(f"_meta.json JSON 解析错误: {str(e)}")

    # 4. 检查 references 目录
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        results["passed"].append("references 目录存在")
    else:
        results["warnings"].append("references 目录不存在（可选）")

    # 5. 检查 scripts 目录
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        results["passed"].append("scripts 目录存在")
    else:
        results["warnings"].append("scripts 目录不存在（可选）")

    return results

def main():
    import sys

    if len(sys.argv) < 2:
        # 验证当前技能
        skill_path = "/workspace/temp-skills/digital-service-data-analyst"
    else:
        skill_path = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"技能验证: {skill_path}")
    print(f"{'='*60}\n")

    results = validate_skill(skill_path)

    # 输出结果
    print("✅ 通过项:")
    for item in results["passed"]:
        print(f"   • {item}")

    if results["warnings"]:
        print("\n⚠️ 警告项:")
        for item in results["warnings"]:
            print(f"   • {item}")

    if results["failed"]:
        print("\n❌ 失败项:")
        for item in results["failed"]:
            print(f"   • {item}")

    print(f"\n{'='*60}")
    if not results["failed"]:
        print("验证结果: ✅ 全部通过")
        return 0
    else:
        print(f"验证结果: ❌ {len(results['failed'])} 项失败")
        return 1

if __name__ == "__main__":
    exit(main())