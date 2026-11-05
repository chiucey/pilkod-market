#!/usr/bin/env python3
"""
A股短线量化分析技能 - 快速验证脚本
验证 SKILL.md frontmatter 和结构完整性
"""

import json
import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能文件的完整性和正确性"""
    errors = []
    warnings = []

    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    meta_json = skill_path / "_meta.json"

    # 检查1: SKILL.md 存在
    if not skill_md.exists():
        errors.append("❌ SKILL.md 文件不存在")
        return False, errors, warnings

    # 检查2: _meta.json 存在
    if not meta_json.exists():
        errors.append("❌ _meta.json 文件不存在")
        return False, errors, warnings

    # 读取文件内容
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(meta_json, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 检查3: Frontmatter 必须在第一行
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 --- 开头 (frontmatter)")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter_text:
            errors.append("❌ frontmatter 缺少 'name' 字段")

        if 'description:' not in frontmatter_text:
            errors.append("❌ frontmatter 缺少 'description' 字段")

        # 验证 name 格式（连字符）
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"❌ name 格式错误，应使用小写字母和连字符: {name}")
            if name != skill_path.name:
                warnings.append(f"⚠️ name ({name}) 与文件夹名称 ({skill_path.name}) 不一致")
    else:
        errors.append("❌ 无法解析 frontmatter")

    # 检查4: _meta.json 必需字段
    if 'id' not in meta:
        errors.append("❌ _meta.json 缺少 'id' 字段")
    if 'version' not in meta:
        errors.append("❌ _meta.json 缺少 'version' 字段")

    # 检查5: 禁止在 frontmatter 前有 markdown 标题
    before_frontmatter = content[:content.find('---')]
    if '#' in before_frontmatter or '```' in before_frontmatter:
        errors.append("❌ frontmatter 之前不能有 markdown 内容")

    # 检查6: 检查是否有不必要的敏感信息
    sensitive_patterns = ['password', 'secret', 'api_key', 'token', 'credentials']
    for pattern in sensitive_patterns:
        if re.search(rf'{pattern}\s*[:=]\s*["\']?[\w-]+["\']?', content, re.IGNORECASE):
            warnings.append(f"⚠️ 可能包含敏感信息: {pattern}")

    # 检查7: 目录结构合理性
    required_dirs = ['references']
    for dir_name in required_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            warnings.append(f"⚠️ 建议添加 {dir_name}/ 目录")

    return len(errors) == 0, errors, warnings


def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    print(f"\n🔍 验证技能: {skill_path}")
    print("=" * 50)

    success, errors, warnings = validate_skill(skill_path)

    for warning in warnings:
        print(warning)

    for error in errors:
        print(error)

    if success:
        print("\n✅ 验证通过!")
        return 0
    else:
        print(f"\n❌ 验证失败 ({len(errors)} 个错误)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
