#!/usr/bin/env python3
"""
技能验证脚本 - 检查SKILL.md的frontmatter和结构
"""

import os
import sys
import json
import re
from pathlib import Path

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    errors = []
    warnings = []
    passed = []

    skill_dir = Path(skill_path)
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'

    # 1. 检查SKILL.md存在
    if not skill_md.exists():
        errors.append(f"SKILL.md not found at {skill_md}")
        return False, errors, warnings

    # 2. 读取SKILL.md内容
    content = skill_md.read_text(encoding='utf-8')

    # 3. 检查frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")
    else:
        passed.append("Frontmatter starts correctly")

    # 提取frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_content = fm_match.group(1)
        fm_lines = fm_content.split('\n')

        # 检查必需字段
        has_name = any(line.strip().startswith('name:') for line in fm_lines)
        has_desc = any(line.strip().startswith('description:') for line in fm_lines)

        if not has_name:
            errors.append("Frontmatter missing 'name' field")
        else:
            passed.append("Frontmatter has 'name' field")

        if not has_desc:
            errors.append("Frontmatter missing 'description' field")
        else:
            passed.append("Frontmatter has 'description' field")

        # 检查description长度
        desc_match = re.search(r'description:\s*(.+)', fm_content)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append("Description is too short (< 20 chars)")
            elif len(desc) > 500:
                warnings.append("Description is very long (> 500 chars)")
    else:
        errors.append("Cannot parse frontmatter")

    # 4. 检查_meta.json
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            else:
                passed.append("_meta.json has 'id' field")

            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
            else:
                passed.append("_meta.json has 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is invalid JSON: {e}")

    # 5. 检查文件夹名称与name一致
    folder_name = skill_dir.name
    name_match = re.search(r'name:\s*(.+)', content)
    if name_match:
        frontmatter_name = name_match.group(1).strip()
        if folder_name != frontmatter_name:
            warnings.append(f"Folder name '{folder_name}' differs from frontmatter name '{frontmatter_name}'")

    # 6. 检查markdown内容不为空
    md_content = content[fm_match.end() if fm_match else 0:].strip()
    if len(md_content) < 100:
        warnings.append("Markdown content is very short (< 100 chars)")

    # 输出结果
    print("\n" + "="*50)
    print("技能验证报告")
    print("="*50)

    print(f"\n{GREEN}✓ 通过 ({len(passed)}){RESET}")
    for p in passed:
        print(f"  • {p}")

    if warnings:
        print(f"\n{YELLOW}⚠ 警告 ({len(warnings)}){RESET}")
        for w in warnings:
            print(f"  • {w}")

    if errors:
        print(f"\n{RED}✗ 错误 ({len(errors)}){RESET}")
        for e in errors:
            print(f"  • {e}")
        return False, errors, warnings

    print(f"\n{GREEN}✓ 所有检查通过！{RESET}")
    return True, errors, warnings

if __name__ == '__main__':
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    success, errors, warnings = validate_skill(skill_path)
    sys.exit(0 if success else 1)
