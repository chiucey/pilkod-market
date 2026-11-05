#!/usr/bin/env python3
"""
技能验证脚本 - 验证SKILL.md和_meta.json的结构完整性
"""

import os
import json
import sys
from pathlib import Path

def validate_skill_structure(skill_dir):
    """验证技能目录结构"""
    errors = []
    warnings = []

    # 检查SKILL.md是否存在
    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return errors, warnings

    # 检查_meta.json是否存在
    meta_json = Path(skill_dir) / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json 文件不存在")
        return errors, warnings

    # 验证SKILL.md的frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter --- 开头")

    # 解析frontmatter
    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            errors.append("SKILL.md frontmatter 未正确闭合")
        else:
            frontmatter_text = content[3:frontmatter_end].strip()
            lines = frontmatter_text.split('\n')

            required_fields = ['name', 'description']
            for field in required_fields:
                if not any(line.strip().startswith(f'{field}:') for line in lines):
                    errors.append(f"Frontmatter 缺少必需字段: {field}")

    # 验证_meta.json
    try:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json 缺少 'id' 字段")
        if 'version' not in meta:
            errors.append("_meta.json 缺少 'version' 字段")
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON格式错误: {e}")

    return errors, warnings

def main():
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认当前目录
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        # 返回到父目录（scripts -> skill-name）
        skill_dir = os.path.dirname(skill_dir)

    print(f"验证技能目录: {skill_dir}")
    print("-" * 50)

    errors, warnings = validate_skill_structure(skill_dir)

    if warnings:
        print("\n警告:")
        for w in warnings:
            print(f"  ⚠️ {w}")

    if errors:
        print("\n错误:")
        for e in errors:
            print(f"  ❌ {e}")
        print("\n验证失败!")
        sys.exit(1)
    else:
        print("\n✅ 验证通过!")
        sys.exit(0)

if __name__ == "__main__":
    main()
