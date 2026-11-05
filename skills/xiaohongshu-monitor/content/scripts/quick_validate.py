#!/usr/bin/env python3
"""快速验证脚本 - 检查技能文件结构"""

import os
import json
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能文件结构和frontmatter"""

    skill_dir = Path(skill_path)
    errors = []

    # 检查 SKILL.md 是否存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("❌ SKILL.md 不存在")
        return False

    # 读取并验证 frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 是否在文件开头
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 --- 开头（frontmatter必须在第一行）")

    # 解析 frontmatter
    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            errors.append("❌ Frontmatter 未正确关闭")
        else:
            frontmatter = content[3:frontmatter_end].strip()

            # 检查必需字段
            if 'name:' not in frontmatter:
                errors.append("❌ Frontmatter 缺少 name 字段")
            if 'description:' not in frontmatter:
                errors.append("❌ Frontmatter 缺少 description 字段")

    # 检查 _meta.json
    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        errors.append("❌ _meta.json 不存在")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("❌ _meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("❌ _meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("❌ _meta.json 格式错误")

    # 输出结果
    if errors:
        print("❌ 验证失败：")
        for err in errors:
            print(f"  {err}")
        return False
    else:
        print("✅ 验证通过！")
        return True

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = validate_skill(skill_path)
    exit(0 if result else 1)