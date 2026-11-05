#!/usr/bin/env python3
"""
快递财务技能 - 快速验证脚本
验证SKILL.md的结构和内容完整性
"""

import os
import re
import json
from pathlib import Path

def validate_skill(skill_dir: str) -> tuple[bool, list[str]]:
    """验证技能文件的完整性和正确性"""
    errors = []
    skill_path = Path(skill_dir)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        file_path = skill_path / f
        if not file_path.exists():
            errors.append(f"缺少必需文件: {f}")

    if errors:
        return False, errors

    # 验证SKILL.md
    skill_md = skill_path / 'SKILL.md'
    content = skill_md.read_text(encoding='utf-8')

    # 检查frontmatter格式
    if not content.startswith('---'):
        errors.append("SKILL.md必须以frontmatter(---)开头")
    else:
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            errors.append("Frontmatter格式不正确")
        else:
            frontmatter = frontmatter_match.group(1)
            # 检查必需字段
            if 'name:' not in frontmatter:
                errors.append("Frontmatter缺少name字段")
            if 'description:' not in frontmatter:
                errors.append("Frontmatter缺少description字段")

            # 提取name值
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                # 验证name与文件夹名一致
                expected_name = skill_path.name
                if name != expected_name:
                    errors.append(f"name字段值('{name}')应与文件夹名('{expected_name}')一致")

    # 验证_meta.json
    meta_path = skill_path / '_meta.json'
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if 'id' not in meta:
            errors.append("_meta.json缺少id字段")
        if 'version' not in meta:
            errors.append("_meta.json缺少version字段")
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json格式错误: {e}")

    return len(errors) == 0, errors


def main():
    skill_dir = '/workspace/temp-skills/express-finance-accounting'
    valid, errors = validate_skill(skill_dir)

    if valid:
        print("✓ 验证通过：快递财务技能结构完整")
        print(f"  技能路径: {skill_dir}")
    else:
        print("✗ 验证失败：")
        for error in errors:
            print(f"  - {error}")

    return 0 if valid else 1


if __name__ == '__main__':
    exit(main())
