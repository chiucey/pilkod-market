#!/usr/bin/env python3
"""
Skill Validator — 质量门槛验证脚本
检查 SKILL.md frontmatter、结构和命名规范
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能质量和规范"""

    errors = []
    skill_path = Path(skill_path)

    # 1. 检查 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"❌ SKILL.md 不存在: {skill_md}")
        return False, errors

    # 2. 读取内容
    content = skill_md.read_text(encoding="utf-8")

    # 3. 检查 frontmatter 是否在第一行
    lines = content.split('\n')
    if not lines[0].strip().startswith('---'):
        errors.append("❌ SKILL.md 必须以 --- (frontmatter) 开头，不能有标题在前面")
        return False, errors

    # 4. 解析 frontmatter
    try:
        frontmatter_end = content.index('---', 3)
        frontmatter = content[3:frontmatter_end].strip()
    except ValueError:
        errors.append("❌ Frontmatter 未正确闭合（缺少结束 ---）")
        return False, errors

    # 5. 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter, re.MULTILINE):
            errors.append(f"❌ Frontmatter 缺少必需字段: {field}")

    # 6. 提取 name 字段
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        skill_name = name_match.group(1).strip()
        # 检查名称格式（连字符）
        if not re.match(r'^[a-z0-9-]+$', skill_name):
            errors.append(f"❌ name 必须是连字符格式 (kebab-case): {skill_name}")
        # 检查名称与文件夹名匹配
        if skill_name != skill_path.name:
            errors.append(f"❌ name ({skill_name}) 与文件夹名 ({skill_path.name}) 不匹配")

    # 7. 检查 description 长度
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE | re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append(f"⚠️ description 太短 ({len(desc)}字符)，建议至少20字符")

    # 8. 检查 _meta.json
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            for field in ['id', 'version']:
                if field not in meta:
                    errors.append(f"❌ _meta.json 缺少必需字段: {field}")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json JSON格式错误: {e}")
    else:
        errors.append("❌ _meta.json 不存在")

    # 9. 检查触发短语（description 中应有触发条件）
    if desc_match:
        desc = desc_match.group(1).strip()
        trigger_keywords = ['when', '触发', 'use when', 'say']
        if not any(kw.lower() in desc.lower() for kw in trigger_keywords):
            errors.append("⚠️ description 缺少触发短语，建议包含 'when' 或 '触发'")

    passed = len(errors) == 0
    return passed, errors


def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("用法: python validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    passed, errors = validate_skill(skill_path)

    print(f"\n{'='*60}")
    print(f"技能验证结果: {skill_path}")
    print(f"{'='*60}\n")

    if passed:
        print("✅ 验证通过！")
    else:
        print("❌ 验证失败：")
        for error in errors:
            print(f"  {error}")

    print()
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
