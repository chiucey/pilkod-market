#!/usr/bin/env python3
"""
酒店平面布置图技能验证脚本
验证 SKILL.md frontmatter、结构、元数据等是否符合规范
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能结构和内容"""
    skill_path = Path(skill_path)
    errors = []
    warnings = []

    # 1. 检查 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("❌ SKILL.md 文件不存在")
        return False

    # 2. 读取 SKILL.md 内容
    content = skill_md.read_text(encoding='utf-8')

    # 3. 检查 frontmatter 必须在第一行
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 frontmatter (---) 开头，不能以 markdown 标题 (#) 开头")
    else:
        # 4. 检查 frontmatter 结构
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            errors.append("❌ Frontmatter 格式错误，无法解析")
        else:
            frontmatter = frontmatter_match.group(1)

            # 检查必需字段
            if 'name:' not in frontmatter:
                errors.append("❌ Frontmatter 缺少 'name' 字段")
            if 'description:' not in frontmatter:
                errors.append("❌ Frontmatter 缺少 'description' 字段")

            # 检查 name 格式
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    errors.append(f"❌ name 格式错误：'{name}'，应使用连字符格式（hyphen-case）且仅包含小写字母、数字和连字符")
                if len(name) > 64:
                    errors.append(f"❌ name 长度超过 64 字符：'{name}'")

            # 检查 description 包含触发短语
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
            if desc_match:
                desc = desc_match.group(1).strip()
                if '当用户' not in desc and 'Use when' not in desc.lower():
                    warnings.append(f"⚠️ description 建议包含触发短语（如 '当用户...' 或 'Use when...'）")

    # 5. 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("❌ _meta.json 文件不存在")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("❌ _meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("❌ _meta.json 缺少 'version' 字段")
            if 'version' in meta:
                if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                    errors.append(f"❌ version 格式错误：'{meta['version']}'，应使用语义化版本（x.y.z）")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json JSON 格式错误：{e}")

    # 6. 检查目录结构
    required_dirs = ['references']
    for dirname in required_dirs:
        dir_path = skill_path / dirname
        if not dir_path.exists():
            warnings.append(f"⚠️ 建议添加 '{dirname}/' 目录")

    # 7. 检查是否有重复内容
    if '# ' in content[:200]:
        warnings.append("⚠️ SKILL.md 开头可能有 markdown 标题，应在 frontmatter 之后")

    # 输出结果
    print("\n" + "="*60)
    print("🔍 技能验证报告")
    print("="*60)

    if errors:
        print("\n❌ 错误：")
        for err in errors:
            print(f"   {err}")

    if warnings:
        print("\n⚠️ 警告：")
        for warn in warnings:
            print(f"   {warn}")

    if not errors and not warnings:
        print("\n✅ 验证通过！所有检查项均符合要求。")
        return True
    elif not errors:
        print("\n✅ 核心验证通过，警告项不影响使用。")
        return True
    else:
        print("\n❌ 验证失败，请修复上述错误。")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/hotel-floor-plan-prompt"
    else:
        skill_path = sys.argv[1]

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)