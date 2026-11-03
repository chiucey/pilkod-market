#!/usr/bin/env python3
"""
医学PPT技能验证脚本
验证SKILL.md和_meta.json的结构完整性
"""

import json
import os
import re
import sys
from pathlib import Path

def validate_skill(skill_dir: str) -> tuple[bool, list[str]]:
    """验证技能结构和内容"""
    errors = []
    skill_path = Path(skill_dir)

    # 1. 检查_meta.json
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        errors.append("❌ _meta.json 不存在")
    else:
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("❌ _meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("❌ _meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json JSON格式错误: {e}")

    # 2. 检查SKILL.md
    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        errors.append("❌ SKILL.md 不存在")
    else:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter位置
        if not content.startswith('---'):
            errors.append("❌ SKILL.md 必须以 YAML frontmatter (---) 开头")

        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # 检查必需字段
            if 'name:' not in frontmatter:
                errors.append("❌ frontmatter 缺少 'name' 字段")
            if 'description:' not in frontmatter:
                errors.append("❌ frontmatter 缺少 'description' 字段")

            # 检查name格式（连字符）
            name_match = re.search(r'^name:\s*([a-z0-9-]+)', frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1)
                if name != skill_path.name:
                    errors.append(f"⚠️ name '{name}' 与文件夹名 '{skill_path.name}' 不一致")
        else:
            errors.append("❌ 无法解析frontmatter")

    # 3. 检查目录结构
    required_dirs = []
    for d in required_dirs:
        if not (skill_path / d).exists():
            errors.append(f"⚠️ 建议目录 '{d}' 不存在")

    # 4. 检查references目录内容
    ref_dir = skill_path / "references"
    if ref_dir.exists():
        ref_files = list(ref_dir.glob("*.md"))
        if len(ref_files) == 0:
            errors.append("⚠️ references/ 目录为空")

    return len(errors) == 0, errors


def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"🔍 验证技能目录: {skill_dir}")
    print("=" * 50)

    success, errors = validate_skill(skill_dir)

    if errors:
        print("\n❌ 验证失败:")
        for err in errors:
            print(f"  {err}")
    else:
        print("✅ 验证通过!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()