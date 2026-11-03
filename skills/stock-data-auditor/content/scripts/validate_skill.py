#!/usr/bin/env python3
"""
股票数据审计技能验证脚本
验证技能文件结构和内容是否符合标准
"""

import json
import os
from pathlib import Path

def validate_frontmatter(skill_md_path: str) -> dict:
    """验证SKILL.md的frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return {"valid": False, "error": "SKILL.md必须以---开头"}

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not any(line.strip().startswith(f'{field}:') for line in frontmatter_lines):
            return {"valid": False, "error": f"缺少必需字段: {field}"}

    # 检查name与description不为空
    for line in frontmatter_lines:
        if line.strip().startswith('name:'):
            name_value = line.split(':', 1)[1].strip()
            if not name_value:
                return {"valid": False, "error": "name字段不能为空"}
        if line.strip().startswith('description:'):
            desc_value = line.split(':', 1)[1].strip()
            if not desc_value:
                return {"valid": False, "error": "description字段不能为空"}

    return {"valid": True, "frontmatter": frontmatter_text}

def validate_meta(meta_path: str) -> dict:
    """验证_meta.json"""
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return {"valid": False, "error": f"缺少必需字段: {field}"}

    return {"valid": True, "meta": meta}

def validate_structure(base_path: str) -> dict:
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(base_path, file)
        if not os.path.exists(file_path):
            return {"valid": False, "error": f"缺少必需文件: {file}"}

    return {"valid": True}

def main():
    skill_path = "/workspace/temp-skills/stock-data-auditor"

    print("=" * 50)
    print("股票数据审计技能 - 验证报告")
    print("=" * 50)

    all_valid = True

    # 1. 验证目录结构
    print("\n[1] 目录结构验证...")
    structure_result = validate_structure(skill_path)
    if structure_result['valid']:
        print("    ✓ 目录结构验证通过")
    else:
        print(f"    ✗ {structure_result['error']}")
        all_valid = False

    # 2. 验证frontmatter
    print("\n[2] Frontmatter验证...")
    frontmatter_result = validate_frontmatter(os.path.join(skill_path, 'SKILL.md'))
    if frontmatter_result['valid']:
        print("    ✓ Frontmatter验证通过")
    else:
        print(f"    ✗ {frontmatter_result['error']}")
        all_valid = False

    # 3. 验证_meta.json
    print("\n[3] _meta.json验证...")
    meta_result = validate_meta(os.path.join(skill_path, '_meta.json'))
    if meta_result['valid']:
        print(f"    ✓ 技能ID: {meta_result['meta']['id']}")
        print(f"    ✓ 版本: {meta_result['meta']['version']}")
    else:
        print(f"    ✗ {meta_result['error']}")
        all_valid = False

    # 4. 验证references目录
    print("\n[4] references目录验证...")
    references_path = os.path.join(skill_path, 'references')
    if os.path.exists(references_path):
        ref_files = os.listdir(references_path)
        print(f"    ✓ references目录存在，包含 {len(ref_files)} 个文件")
    else:
        print("    ! references目录不存在（可选）")

    # 5. 验证scripts目录
    print("\n[5] scripts目录验证...")
    scripts_path = os.path.join(skill_path, 'scripts')
    if os.path.exists(scripts_path):
        script_files = os.listdir(scripts_path)
        print(f"    ✓ scripts目录存在，包含 {len(script_files)} 个脚本")
    else:
        print("    ! scripts目录不存在（可选）")

    print("\n" + "=" * 50)
    if all_valid:
        print("✓ 所有验证通过！技能符合发布标准。")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试。")
        return 1

if __name__ == "__main__":
    exit(main())
