#!/usr/bin/env python3
"""
技能验证脚本 - 验证SKILL.md结构和元数据
"""
import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证frontmatter格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        errors.append("Frontmatter必须以'---'开头")
        return errors

    # 提取frontmatter
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        errors.append("Frontmatter未正确闭合")
        return errors

    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"缺少必需字段: {field}")

    # 检查name格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"name字段格式错误: '{name_value}' - 应使用小写字母、数字和连字符")
        if len(name_value) > 64:
            errors.append(f"name字段长度超过64字符限制: {len(name_value)}")

    # 检查description存在且非空
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 10:
            errors.append("description字段内容过短(应至少10字符)")

    return errors

def validate_meta_json(meta_path):
    """验证_meta.json格式"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json文件不存在")
        return errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json格式错误: {e}")
        return errors

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json缺少必需字段: {field}")

    # 验证id
    if 'id' in meta:
        if not isinstance(meta['id'], (int, str)):
            errors.append("_meta.json的id必须是数字或字符串")
        else:
            # 如果是字符串，尝试转为整数验证
            try:
                int(meta['id'])
            except (ValueError, TypeError):
                errors.append(f"_meta.json的id格式无效: {meta['id']}")

    # 验证version格式 (semver)
    if 'version' in meta:
        version = str(meta['version'])
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"_meta.json的version格式不符合semver: {version}")

    return errors

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []

    # 检查SKILL.md存在
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_md):
        errors.append("SKILL.md文件不存在")

    # 检查_meta.json存在
    meta_json = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_json):
        errors.append("_meta.json文件不存在")

    # 检查references目录
    refs_dir = os.path.join(skill_dir, 'references')
    if os.path.exists(refs_dir):
        if not os.path.isdir(refs_dir):
            errors.append("references应为目录而非文件")

    return errors

def validate_naming(skill_dir):
    """验证名称一致性"""
    errors = []

    skill_md = os.path.join(skill_dir, 'SKILL.md')

    # 获取文件夹名称
    dir_name = os.path.basename(skill_dir)

    # 检查frontmatter中的name
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取frontmatter
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx:
        frontmatter_text = '\n'.join(lines[1:end_idx])
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if name_value != dir_name:
                errors.append(f"name字段('{name_value}')与文件夹名称('{dir_name}')不一致")

    # 检查非英文字符
    if not re.match(r'^[a-z0-9-]+$', dir_name):
        errors.append(f"文件夹名称包含非英文字符: {dir_name}")

    return errors

def main():
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)

    all_errors = []

    # 执行所有验证
    all_errors.extend(validate_directory_structure(skill_dir))
    all_errors.extend(validate_naming(skill_dir))
    all_errors.extend(validate_frontmatter(os.path.join(skill_dir, 'SKILL.md')))
    all_errors.extend(validate_meta_json(os.path.join(skill_dir, '_meta.json')))

    if all_errors:
        print("验证失败:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        sys.exit(1)
    else:
        print("验证通过!")
        print(f"  目录结构: OK")
        print(f"  命名一致性: OK")
        print(f"  Frontmatter格式: OK")
        print(f"  元数据格式: OK")
        sys.exit(0)

if __name__ == '__main__':
    main()
