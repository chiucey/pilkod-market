#!/usr/bin/env python3
"""
Excel Format Optimizer - Quick Validation Script
验证 SKILL.md 和技能结构是否符合规范
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(path: str) -> tuple[bool, list[str]]:
    """验证技能结构和 frontmatter"""
    errors = []
    skill_path = Path(path)

    # 检查目录存在
    if not skill_path.exists():
        return False, [f"路径不存在: {path}"]

    # 检查 SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("缺少 SKILL.md 文件")
        return False, errors

    # 读取 SKILL.md
    content = skill_md.read_text(encoding='utf-8')

    # 验证1: frontmatter 必须在第一行
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 frontmatter '---' 开头")

    # 验证2: frontmatter 格式
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("❌ frontmatter 格式错误，应为 ---...--- 块")
    else:
        fm_content = frontmatter_match.group(1)

        # 检查必填字段
        if 'name:' not in fm_content:
            errors.append("❌ frontmatter 必须包含 name 字段")
        if 'description:' not in fm_content:
            errors.append("❌ frontmatter 必须包含 description 字段")

        # 检查 name 格式（连字符）
        name_match = re.search(r'name:\s*([a-z0-9-]+)', fm_content)
        if name_match:
            name = name_match.group(1)
            if name != skill_path.name:
                errors.append(f"❌ name '{name}' 应与目录名 '{skill_path.name}' 一致")

    # 验证3: 检查 markdown 标题位置（不应在 frontmatter 之前）
    lines = content.split('\n')
    first_content_line = None
    for i, line in enumerate(lines):
        if line.startswith('---') and i > 0:
            break
        if line.strip() and not line.startswith('#'):
            continue
        if line.strip().startswith('#'):
            first_content_line = i
            break

    # 验证4: _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("❌ 缺少 _meta.json 文件")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("❌ _meta.json 必须包含 id 字段")
            if 'version' not in meta:
                errors.append("❌ _meta.json 必须包含 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json JSON 格式错误: {e}")

    # 验证5: 目录结构建议
    if not (skill_path / "scripts").exists():
        errors.append("⚠️ 建议添加 scripts/ 目录")
    if not (skill_path / "references").exists():
        errors.append("⚠️ 建议添加 references/ 目录")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"🔍 验证技能: {skill_path}")
    print("=" * 50)

    valid, errors = validate_skill(skill_path)

    if errors:
        print("\n📋 检查结果:")
        for error in errors:
            print(f"  {error}")

    if valid:
        print("\n✅ 验证通过！")
        return 0
    else:
        print("\n❌ 验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
