#!/usr/bin/env python3
"""
快速验证脚本 - 检查SKILL.md的格式和内容
"""
import os
import re
import json
import sys

def validate_frontmatter(skill_path):
    """验证frontmatter格式"""
    skill_md_path = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md_path):
        return False, "SKILL.md文件不存在"

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在第一行
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头（frontmatter必须在第一行）"

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

    # 检查必填字段
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        return False, f"Frontmatter缺少必填字段: {', '.join(missing_fields)}"

    # 检查description长度
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            return False, "description字段过短（建议至少20个字符）"

    return True, "Frontmatter验证通过"

def validate_meta_json(skill_path):
    """验证_meta.json格式"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        return False, "_meta.json格式无效（JSON解析失败）"

    # 检查必填字段
    required_fields = ['id', 'version']
    missing_fields = []

    for field in required_fields:
        if field not in meta:
            missing_fields.append(field)

    if missing_fields:
        return False, f"_meta.json缺少必填字段: {', '.join(missing_fields)}"

    # 验证id是整数
    if not isinstance(meta['id'], int):
        return False, "_meta.json中的id必须是整数"

    # 验证version格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, "_meta.json中的version必须符合语义化版本格式（如1.0.0）"

    return True, "_meta.json验证通过"

def validate_structure(skill_path):
    """验证目录结构"""
    # SKILL.md是必填的
    if not os.path.exists(os.path.join(skill_path, "SKILL.md")):
        return False, "缺少SKILL.md文件"

    # _meta.json是必填的
    if not os.path.exists(os.path.join(skill_path, "_meta.json")):
        return False, "缺少_meta.json文件"

    return True, "目录结构验证通过"

def validate_naming(skill_path):
    """验证命名规范"""
    skill_name = os.path.basename(skill_path)

    # 检查是否使用连字符格式
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', skill_name):
        return False, f"文件夹名称'{skill_name}'必须使用小写字母和连字符（kebab-case）"

    # 检查长度
    if len(skill_name) > 64:
        return False, f"文件夹名称过长（{len(skill_name)}字符，要求≤64字符）"

    return True, "命名规范验证通过"

def run_validation(skill_path):
    """运行所有验证"""
    print(f"\n{'='*60}")
    print(f"开始验证技能: {os.path.basename(skill_path)}")
    print('='*60 + '\n')

    checks = [
        ("目录结构", validate_structure),
        ("命名规范", validate_naming),
        ("Frontmatter", validate_frontmatter),
        ("元数据文件", validate_meta_json),
    ]

    all_passed = True
    results = []

    for check_name, check_func in checks:
        try:
            passed, message = check_func(skill_path)
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"[{status}] {check_name}: {message}")
            results.append((check_name, passed, message))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"[✗ 错误] {check_name}: {str(e)}")
            results.append((check_name, False, str(e)))
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("✓ 所有验证通过！")
    else:
        print("✗ 存在验证失败项，请修复后重试")
    print('='*60 + '\n')

    return all_passed, results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    passed, _ = run_validation(skill_path)
    sys.exit(0 if passed else 1)
