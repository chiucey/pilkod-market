#!/usr/bin/env python3
"""验证错题本技能的SKILL.md质量"""

import sys
import os
import re

def validate_frontmatter(skill_path):
    """验证frontmatter格式"""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "Frontmatter必须以---开头"

    # 检查frontmatter结束
    end_match = re.search(r'^---$', content, re.MULTILINE)
    if not end_match:
        return False, "Frontmatter缺少结束标记---"

    # 提取frontmatter内容
    frontmatter = content[3:content.index('---', 3)]

    # 检查必需字段
    if 'name:' not in frontmatter:
        return False, "缺少name字段"
    if 'description:' not in frontmatter:
        return False, "缺少description字段"

    return True, "Frontmatter验证通过"

def validate_structure(skill_path):
    """验证文件结构"""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查标题不在frontmatter之前
    lines = content.split('\n')
    for i, line in enumerate(lines[:10]):
        if line.startswith('# ') and i > 0:
            return False, "标题不能出现在frontmatter之前"

    return True, "结构验证通过"

def main():
    skill_path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
    skill_path = os.path.abspath(skill_path)

    errors = []

    # 验证frontmatter
    valid, msg = validate_frontmatter(skill_path)
    if not valid:
        errors.append(msg)
    else:
        print(f"✓ {msg}")

    # 验证结构
    valid, msg = validate_structure(skill_path)
    if not valid:
        errors.append(msg)
    else:
        print(f"✓ {msg}")

    if errors:
        print("\n验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n所有验证通过!")

if __name__ == '__main__':
    main()