#!/usr/bin/env python3
"""
验证开源项目教程生成器技能的完整性和正确性
"""

import os
import re
import json
from pathlib import Path

def validate_skill_structure(base_path):
    """验证技能目录结构"""
    errors = []
    warnings = []

    required_files = [
        "SKILL.md",
        "_meta.json"
    ]

    required_dirs = [
        "references"
    ]

    # 检查必需文件
    for file in required_files:
        file_path = os.path.join(base_path, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    # 检查必需目录
    for dir_name in required_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.exists(dir_path):
            errors.append(f"缺少必需目录: {dir_name}")

    return errors, warnings

def validate_skill_md(base_path):
    """验证 SKILL.md 格式"""
    errors = []
    warnings = []

    skill_md_path = os.path.join(base_path, "SKILL.md")

    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md 文件不存在")
        return errors, warnings

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否存在
    if not content.startswith('---'):
        errors.append("SKILL.md 缺少 frontmatter（必须以 --- 开头）")
    else:
        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # 检查必需字段
            if 'name:' not in frontmatter:
                errors.append("frontmatter 缺少 name 字段")
            if 'description:' not in frontmatter:
                errors.append("frontmatter 缺少 description 字段")

            # 提取name值
            name_match = re.search(r'name:\s*(.+)', frontmatter)
            if name_match:
                name_value = name_match.group(1).strip()
                folder_name = os.path.basename(base_path)
                if name_value != folder_name:
                    warnings.append(f"name 值 '{name_value}' 与文件夹名 '{folder_name}' 不匹配")
        else:
            errors.append("无法解析 frontmatter")

    # 检查是否有 markdown 标题在 frontmatter 之前
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line == '---':
            if frontmatter_end == -1:
                frontmatter_end = i
                break

    if frontmatter_end > 1:
        for i in range(1, frontmatter_end):
            if lines[i].startswith('#'):
                errors.append(f"发现 markdown 标题在 frontmatter 之前 (行 {i+1})")
                break

    return errors, warnings

def validate_meta_json(base_path):
    """验证 _meta.json 格式"""
    errors = []
    warnings = []

    meta_path = os.path.join(base_path, "_meta.json")

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return errors, warnings

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json 缺少 id 字段")
        elif not isinstance(meta['id'], int):
            errors.append("_meta.json id 必须是整数")

        if 'version' not in meta:
            errors.append("_meta.json 缺少 version 字段")
        elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            warnings.append("_meta.json version 建议使用语义化版本格式 (x.y.z)")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json 格式错误: {e}")
    except Exception as e:
        errors.append(f"_meta.json 读取错误: {e}")

    return errors, warnings

def validate_references(base_path):
    """验证 references 目录内容"""
    errors = []
    warnings = []

    refs_path = os.path.join(base_path, "references")

    if not os.path.exists(refs_path):
        return errors, warnings

    ref_files = os.listdir(refs_path)
    if not ref_files:
        warnings.append("references 目录为空")

    return errors, warnings

def run_validation(base_path):
    """运行所有验证"""
    print("=" * 60)
    print("开源项目教程生成器 - 技能验证")
    print("=" * 60)
    print()

    all_errors = []
    all_warnings = []

    # 1. 目录结构验证
    print("检查目录结构...")
    errors, warnings = validate_skill_structure(base_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 2. SKILL.md 验证
    print("检查 SKILL.md...")
    errors, warnings = validate_skill_md(base_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 3. _meta.json 验证
    print("检查 _meta.json...")
    errors, warnings = validate_meta_json(base_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 4. references 验证
    print("检查 references...")
    errors, warnings = validate_references(base_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 输出结果
    print()
    print("=" * 60)

    if all_errors:
        print("❌ 验证失败 - 发现错误:")
        for error in all_errors:
            print(f"  - {error}")
        print()

    if all_warnings:
        print("⚠️  警告:")
        for warning in all_warnings:
            print(f"  - {warning}")
        print()

    if not all_errors and not all_warnings:
        print("✅ 验证通过！")
        print()

    return len(all_errors) == 0

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)

    success = run_validation(base_path)
    sys.exit(0 if success else 1)
