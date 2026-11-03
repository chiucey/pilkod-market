#!/usr/bin/env python3
"""
初中生试卷分析技能 - 快速验证脚本
验证技能结构和Frontmatter格式
"""

import os
import re
import json
from pathlib import Path

def validate_skill():
    """验证技能结构和格式"""
    results = []
    skill_dir = Path("/workspace/temp-skills/middle-school-paper-analyzer")

    # 检查必要文件
    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        file_path = skill_dir / file
        if file_path.exists():
            results.append(f"✅ {file} 存在")
        else:
            results.append(f"❌ {file} 缺失")

    # 验证SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 检查frontmatter是否在文件开头
        if content.startswith("---"):
            results.append("✅ Frontmatter 在文件开头")

            # 提取frontmatter
            frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)

                # 检查必需字段
                if "name:" in frontmatter:
                    results.append("✅ name 字段存在")
                else:
                    results.append("❌ name 字段缺失")

                if "description:" in frontmatter:
                    results.append("✅ description 字段存在")
                else:
                    results.append("❌ description 字段缺失")

                # 检查是否有触发短语
                if "当用户" in frontmatter or "使用" in frontmatter.lower():
                    results.append("✅ 包含触发短语")
                else:
                    results.append("⚠️ 建议添加明确的触发短语")
        else:
            results.append("❌ SKILL.md 必须以 frontmatter (---) 开头")

        # 检查是否有markdown标题在frontmatter之前
        lines = content.split("\n")
        for i, line in enumerate(lines[:5]):
            if line.startswith("#") and i > 2:
                results.append("❌ Markdown 标题不能出现在 frontmatter 之前")
                break
    else:
        results.append("❌ SKILL.md 不存在")

    # 验证_meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" in meta:
                results.append(f"✅ _meta.json id: {meta['id']}")
            else:
                results.append("❌ _meta.json 缺少 id 字段")

            if "version" in meta:
                results.append(f"✅ _meta.json version: {meta['version']}")
            else:
                results.append("❌ _meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            results.append("❌ _meta.json 格式错误")

    # 验证目录结构
    directories = ["references", "scripts", "assets"]
    for directory in directories:
        dir_path = skill_dir / directory
        if dir_path.exists() and dir_path.is_dir():
            results.append(f"✅ {directory}/ 目录存在")
        else:
            results.append(f"⚠️ {directory}/ 目录不存在（可选）")

    return results

def main():
    print("=" * 50)
    print("初中生试卷分析技能 - 验证报告")
    print("=" * 50)

    results = validate_skill()
    for result in results:
        print(result)

    print("=" * 50)
    passed = sum(1 for r in results if r.startswith("✅"))
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("🎉 所有验证通过！")
        return 0
    else:
        print("⚠️ 存在需要修复的问题")
        return 1

if __name__ == "__main__":
    exit(main())
