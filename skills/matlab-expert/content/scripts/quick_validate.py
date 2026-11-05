#!/usr/bin/env python3
"""
MATLAB技能验证脚本
检查技能结构和frontmatter是否符合规范
"""

import os
import re
import sys
from pathlib import Path


def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能结构"""
    errors = []
    skill_path = Path(skill_path)

    # 检查目录结构
    if not skill_path.exists():
        return False, [f"技能目录不存在: {skill_path}"]

    # 检查SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("缺少SKILL.md文件")
        return False, errors

    # 读取SKILL.md内容
    content = skill_md.read_text(encoding='utf-8')

    # 验证frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("SKILL.md缺少有效的YAML frontmatter")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # 检查必填字段
    if not re.search(r'^name:\s*.+$', frontmatter_text, re.MULTILINE):
        errors.append("frontmatter缺少name字段")

    if not re.search(r'^description:\s*.+$', frontmatter_text, re.MULTILINE):
        errors.append("frontmatter缺少description字段")

    # 检查description长度
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            errors.append("description内容过短，应至少包含10个字符")

    # 检查_meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("缺少_meta.json文件")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json格式错误: {e}")

    # 检查目录名称与name是否匹配
    dir_name = skill_path.name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        frontmatter_name = name_match.group(1).strip()
        if dir_name != frontmatter_name:
            errors.append(f"目录名称 '{dir_name}' 与frontmatter name '{frontmatter_name}' 不匹配")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    valid, errors = validate_skill(skill_path)

    if valid:
        print(f"✓ 技能验证通过: {skill_path}")
        sys.exit(0)
    else:
        print(f"✗ 技能验证失败: {skill_path}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
