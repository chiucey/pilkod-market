#!/usr/bin/env python3
"""
股票量化资金参与度分析技能 - 验证脚本
验证 SKILL.md 的 frontmatter 和结构完整性
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证 frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, f"SKILL.md 不存在: {skill_md}"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter --- 开头"

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "SKILL.md 缺少结束 --- 分隔符"

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        pattern = rf'^{field}:\s*.+$'
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        return False, f"Frontmatter 缺少必需字段: {', '.join(missing_fields)}"

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            return False, f"name 字段格式错误，应为小写连字符: {name_value}"

    # 检查 description 是否包含触发关键词
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            return False, "description 太短，应至少包含20个字符"

    return True, "Frontmatter 验证通过"

def validate_meta_json(skill_path):
    """验证 _meta.json 格式"""
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        return False, "_meta.json 不存在"

    import json
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"

    required_fields = ['id', 'version']
    missing_fields = []

    for field in required_fields:
        if field not in meta:
            missing_fields.append(field)

    if missing_fields:
        return False, f"_meta.json 缺少必需字段: {', '.join(missing_fields)}"

    # 检查 id 是否为数字
    if not isinstance(meta['id'], (int, str)):
        return False, "_meta.json 的 id 必须是数字或字符串"

    # 检查 version 格式
    if not re.match(r'^\d+\.\d+\.\d+$', str(meta['version'])):
        return False, "_meta.json 的 version 必须符合语义化版本格式 (x.y.z)"

    return True, "_meta.json 验证通过"

def validate_structure(skill_path):
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    # 检查目录（可选）
    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists() and not dir_path.is_dir():
            return False, f"{dir_name} 应该是目录而非文件"

    return True, "目录结构验证通过"

def validate_skill_content(skill_path):
    """验证 SKILL.md 内容完整性"""
    skill_md = skill_path / "SKILL.md"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查核心章节
    required_sections = [
        '分析维度',
        '评分',
        '执行流程',
        '输出格式',
        '触发确认'
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        return False, f"SKILL.md 缺少必要章节: {', '.join(missing_sections)}"

    return True, "内容完整性验证通过"

def main():
    """主验证流程"""
    skill_path = Path(__file__).parent.parent

    print("=" * 50)
    print("股票量化资金参与度分析技能 - 验证工具")
    print("=" * 50)
    print()

    validations = [
        ("Frontmatter 验证", validate_frontmatter),
        ("_meta.json 验证", validate_meta_json),
        ("目录结构验证", validate_structure),
        ("内容完整性验证", validate_skill_content),
    ]

    all_passed = True
    for name, validator in validations:
        print(f"🔍 {name}...")
        passed, message = validator(skill_path)
        if passed:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            all_passed = False
        print()

    print("=" * 50)
    if all_passed:
        print("✅ 所有验证通过！技能结构完整。")
        return 0
    else:
        print("❌ 验证失败，请修复上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
