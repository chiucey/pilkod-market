# -*- coding: utf-8 -*-
"""
验货比对技能验证脚本
验证SKILL.md和_meta.json格式是否正确
"""

import os
import json
import re

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    errors = []
    
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否以---开头
    if not content.strip().startswith('---'):
        errors.append("❌ SKILL.md必须以---开头")
        return errors
    
    # 提取frontmatter
    parts = content.split('---')
    if len(parts) < 3:
        errors.append("❌ frontmatter格式错误，需要---开头和结尾")
        return errors
    
    frontmatter = parts[1]
    
    # 检查必填字段
    if 'name:' not in frontmatter:
        errors.append("❌ frontmatter缺少name字段")
    
    if 'description:' not in frontmatter:
        errors.append("❌ frontmatter缺少description字段")
    
    # 验证name格式（连字符、小写）
    name_match = re.search(r'name:\s*([a-z0-9-]+)', frontmatter)
    if name_match:
        name = name_match.group(1)
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"❌ name '{name}' 格式错误，应使用小写字母、数字和连字符")
    
    return errors

def validate_meta(meta_path):
    """验证_meta.json格式"""
    errors = []
    
    if not os.path.exists(meta_path):
        errors.append("❌ _meta.json文件不存在")
        return errors
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json JSON格式错误: {e}")
        return errors
    
    # 检查必填字段
    if 'id' not in meta:
        errors.append("❌ _meta.json缺少id字段")
    elif not isinstance(meta['id'], int):
        errors.append("❌ _meta.json的id必须是整数")
    
    if 'version' not in meta:
        errors.append("❌ _meta.json缺少version字段")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        errors.append("❌ _meta.json的version格式错误，应为x.y.z格式")
    
    return errors

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []
    
    required_dirs = []
    optional_dirs = ['references', 'scripts', 'assets']
    
    for d in optional_dirs:
        path = os.path.join(skill_dir, d)
        if os.path.exists(path):
            print(f"  ✅ 目录存在: {d}")
    
    return errors

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(skill_dir)  # 回到skill根目录
    
    print("="*60)
    print("验货比对技能验证")
    print("="*60)
    print(f"\n技能目录: {skill_dir}\n")
    
    all_errors = []
    
    # 验证SKILL.md
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        print("【SKILL.md验证】")
        errors = validate_frontmatter(skill_md)
        if errors:
            all_errors.extend(errors)
            for e in errors:
                print(f"  {e}")
        else:
            print("  ✅ frontmatter格式正确")
    else:
        print("  ❌ SKILL.md不存在")
        all_errors.append("SKILL.md不存在")
    
    # 验证_meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    print("\n【_meta.json验证】")
    errors = validate_meta(meta_json)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  {e}")
    else:
        print("  ✅ _meta.json格式正确")
    
    # 验证目录结构
    print("\n【目录结构验证】")
    validate_directory_structure(skill_dir)
    
    # 总结
    print("\n" + "="*60)
    if all_errors:
        print(f"❌ 验证失败，发现 {len(all_errors)} 个错误")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    else:
        print("✅ 所有验证通过！")
        return 0

if __name__ == "__main__":
    exit(main())
