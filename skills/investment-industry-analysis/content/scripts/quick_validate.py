#!/usr/bin/env python3
"""
技能验证脚本 - 验证SKILL.md的frontmatter和结构
"""

import os
import re
import sys

def validate_frontmatter(skill_path):
    """验证frontmatter格式"""
    skill_md = os.path.join(skill_path, "SKILL.md")

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在第一行开始
    if not content.startswith('---'):
        print("❌ SKILL.md必须以---开头，不能有markdown标题")
        return False

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print("❌ Frontmatter格式错误，缺少结束标记---")
        return False

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter, re.MULTILINE):
            print(f"❌ 缺少必需字段: {field}")
            return False

    # 检查name字段格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            print(f"❌ name字段格式错误，应使用小写字母、数字和连字符: {name}")
            return False
        if len(name) > 64:
            print(f"❌ name字段长度超过64字符限制")
            return False

    print("✅ Frontmatter格式验证通过")
    return True

def validate_meta_json(skill_path):
    """验证_meta.json格式"""
    import json

    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        print("❌ 缺少_meta.json文件")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ _meta.json JSON格式错误: {e}")
        return False

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            print(f"❌ _meta.json缺少必需字段: {field}")
            return False

    # 验证version格式
    version = meta.get('version', '')
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print(f"❌ version格式错误，应为语义化版本(x.y.z): {version}")
        return False

    print("✅ _meta.json格式验证通过")
    return True

def validate_naming(skill_path):
    """验证文件命名"""
    folder_name = os.path.basename(skill_path)
    if not re.match(r'^[a-z0-9-]+$', folder_name):
        print(f"❌ 技能文件夹名称格式错误: {folder_name}")
        return False

    print("✅ 文件命名验证通过")
    return True

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"🔍 验证技能: {skill_path}")
    print("-" * 50)

    results = []
    results.append(validate_naming(skill_path))
    results.append(validate_frontmatter(skill_path))
    results.append(validate_meta_json(skill_path))

    print("-" * 50)

    if all(results):
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 验证失败，请修复以上问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
