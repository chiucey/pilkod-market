#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能基本结构和格式
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_skill(skill_dir):
    """验证技能目录结构和内容"""
    errors = []
    warnings = []
    passed = []

    skill_dir = Path(skill_dir)

    # 1. 检查 SKILL.md 存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("❌ SKILL.md 文件不存在")
        return errors, warnings, passed

    passed.append("✓ SKILL.md 存在")

    # 2. 读取 SKILL.md 内容
    content = skill_md.read_text(encoding='utf-8')

    # 3. 检查 frontmatter
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 frontmatter (---) 开头")
    else:
        passed.append("✓ SKILL.md 以 frontmatter 开头")

    # 4. 提取 frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_content = fm_match.group(1)
        fm_lines = fm_content.split('\n')

        # 检查必需字段
        has_name = any(line.strip().startswith('name:') for line in fm_lines)
        has_desc = any(line.strip().startswith('description:') for line in fm_lines)

        if not has_name:
            errors.append("❌ frontmatter 缺少 'name' 字段")
        else:
            passed.append("✓ frontmatter 包含 'name' 字段")

        if not has_desc:
            errors.append("❌ frontmatter 缺少 'description' 字段")
        else:
            passed.append("✓ frontmatter 包含 'description' 字段")

        # 检查 name 格式
        name_match = re.search(r'^name:\s*(.+)$', fm_content, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if ' ' in name:
                warnings.append(f"⚠️ name 包含空格，建议使用连字符格式: '{name.replace(' ', '-')}'")
            if not re.match(r'^[a-z0-9-]+$', name):
                warnings.append(f"⚠️ name 应只包含小写字母、数字和连字符: '{name}'")
            passed.append(f"✓ name 格式正确: '{name}'")
    else:
        errors.append("❌ 无法解析 frontmatter")

    # 5. 检查 _meta.json
    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        warnings.append("⚠️ _meta.json 不存在（建议添加）")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            required_keys = ['id', 'version']
            for key in required_keys:
                if key not in meta:
                    errors.append(f"❌ _meta.json 缺少 '{key}' 字段")
                else:
                    passed.append(f"✓ _meta.json 包含 '{key}'")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json JSON 格式错误: {e}")

    # 6. 检查 references/ 目录
    refs_dir = skill_dir / "references"
    if refs_dir.exists() and refs_dir.is_dir():
        ref_files = list(refs_dir.glob("*.md"))
        passed.append(f"✓ references/ 目录存在，包含 {len(ref_files)} 个文件")
    else:
        warnings.append("⚠️ references/ 目录不存在或为空")

    # 7. 检查目录名称一致性
    dir_name = skill_dir.name
    if name_match:
        expected_name = name_match.group(1).strip()
        if dir_name != expected_name:
            warnings.append(f"⚠️ 目录名 '{dir_name}' 与 frontmatter name '{expected_name}' 不一致")

    # 8. 检查内容长度
    lines = content.split('\n')
    code_blocks = content.count('```')
    if len(lines) > 300:
        warnings.append(f"⚠️ SKILL.md 较长 ({len(lines)} 行)，考虑将详细文档移至 references/")

    # 9. 检查触发短语
    if 'trigger' not in content.lower() and '激活' not in content:
        warnings.append("⚠️ 建议添加激活触发词说明")

    return errors, warnings, passed

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    errors, warnings, passed = validate_skill(skill_dir)

    print("=" * 60)
    print("技能验证报告")
    print("=" * 60)

    if passed:
        print("\n✅ 通过项目:")
        for item in passed:
            print(f"  {item}")

    if warnings:
        print("\n⚠️ 警告:")
        for item in warnings:
            print(f"  {item}")

    if errors:
        print("\n❌ 错误:")
        for item in errors:
            print(f"  {item}")
        print("\n验证失败！请修复上述错误。")
        sys.exit(1)
    else:
        print("\n✅ 验证通过！")

if __name__ == "__main__":
    main()
