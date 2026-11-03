#!/usr/bin/env python3
"""
技能验证脚本 - 验证 SKILL.md 和 _meta.json 的格式和内容
"""
import json
import os
import re
import sys

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查文件是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头（frontmatter 开始标记）"

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 4:
        return False, "SKILL.md frontmatter 不完整"

    # 检查是否有结束标记 ---
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "SKILL.md 缺少 frontmatter 结束标记 ---"

    # 解析 frontmatter
    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    if not re.search(r'^name:\s*\S', frontmatter_text, re.MULTILINE):
        return False, "frontmatter 缺少 name 字段"

    if not re.search(r'^description:\s*\S', frontmatter_text, re.MULTILINE):
        return False, "frontmatter 缺少 description 字段"

    # 检查 markdown 标题不在 frontmatter 之前
    if '#' in '\n'.join(lines[:frontmatter_end]):
        return False, "frontmatter 内不能包含 markdown 标题"

    # 检查 markdown 标题在 frontmatter 之后
    after_frontmatter = '\n'.join(lines[frontmatter_end+1:])
    if not re.search(r'^#{1,6}\s+', after_frontmatter, re.MULTILINE):
        return False, "SKILL.md 应包含至少一个 markdown 标题"

    return True, "Frontmatter 验证通过"

def validate_meta(meta_path):
    """验证 _meta.json 的格式"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError:
            return False, "_meta.json 格式错误（JSON 解析失败）"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少必需字段: {field}"

    # 验证 id 格式（应为数字字符串）
    if not str(meta['id']).isdigit():
        return False, "_meta.json 的 id 必须是数字"

    # 验证 version 格式（语义化版本）
    version_pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(version_pattern, meta['version']):
        return False, "_meta.json 的 version 应符合语义化版本格式 (如 1.0.0)"

    return True, "_meta.json 验证通过"

def validate_naming(skill_dir):
    """验证命名规范"""
    # 处理相对路径如 "."
    abs_path = os.path.abspath(skill_dir)
    dir_name = os.path.basename(abs_path)

    # 检查目录名是否为英文和连字符
    if not re.match(r'^[a-z0-9-]+$', dir_name):
        return False, f"目录名 '{dir_name}' 应只包含小写字母、数字和连字符"

    if len(dir_name) > 64:
        return False, f"目录名长度不能超过 64 字符"

    return True, "命名规范验证通过"

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print("=" * 50)
    print("技能验证开始")
    print("=" * 50)

    all_passed = True

    # 验证命名
    passed, msg = validate_naming(skill_dir)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证 SKILL.md
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        passed, msg = validate_frontmatter(skill_md)
        print(f"[{'✓' if passed else '✗'}] {msg}")
        all_passed = all_passed and passed
    else:
        print("[✗] SKILL.md 文件不存在")
        all_passed = False

    # 验证 _meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    passed, msg = validate_meta(meta_json)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    print("=" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        sys.exit(0)
    else:
        print("✗ 存在验证失败项")
        sys.exit(1)

if __name__ == '__main__':
    main()
