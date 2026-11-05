#!/usr/bin/env python3
"""
技能验证脚本 - 检查邮件发送技能的结构和内容
"""
import os
import re
import json
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> dict:
    """验证 frontmatter"""
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return {'valid': False, 'error': 'SKILL.md 不存在'}

    content = skill_md.read_text(encoding='utf-8')

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return {'valid': False, 'error': 'SKILL.md 必须以 YAML frontmatter 开头（---）'}

    # 提取 frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {'valid': False, 'error': '无效的 YAML frontmatter 格式'}

    frontmatter = parts[1]

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return {'valid': False, 'error': f'缺少必需字段: {field}'}

    # 提取 name 和 description
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)

    name = name_match.group(1).strip() if name_match else None
    description = desc_match.group(1).strip() if desc_match else None

    # 检查 name 格式
    if name and not re.match(r'^[a-z0-9-]+$', name):
        return {'valid': False, 'error': 'name 必须是连字符格式（hyphen-case）'}

    # 检查 description 是否包含触发短语
    trigger_keywords = ['发邮件', '发送邮件', '写邮件', '邮件服务', '邮件模板', '群发邮件']
    has_trigger = any(keyword in description for keyword in trigger_keywords)

    if not has_trigger:
        return {'valid': False, 'error': 'description 应包含触发短语'}

    return {
        'valid': True,
        'name': name,
        'description': description
    }


def validate_meta(skill_path: Path) -> dict:
    """验证 _meta.json"""
    meta_file = skill_path / '_meta.json'

    if not meta_file.exists():
        return {'valid': False, 'error': '_meta.json 不存在'}

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))

        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                return {'valid': False, 'error': f'_meta.json 缺少字段: {field}'}

        return {
            'valid': True,
            'id': meta['id'],
            'version': meta['version']
        }
    except json.JSONDecodeError as e:
        return {'valid': False, 'error': f'_meta.json JSON 解析错误: {e}'}


def validate_structure(skill_path: Path) -> dict:
    """验证目录结构"""
    required_dirs = ['scripts', 'references']
    optional_dirs = ['assets']

    missing = []
    for dir_name in required_dirs:
        if not (skill_path / dir_name).is_dir():
            missing.append(dir_name)

    if missing:
        return {'valid': False, 'error': f'缺少必需目录: {", ".join(missing)}'}

    return {'valid': True}


def main():
    """运行所有验证"""
    skill_path = Path('/workspace/temp-skills/email-sender')

    print("=" * 50)
    print("邮件发送技能验证")
    print("=" * 50)

    results = {
        'frontmatter': validate_frontmatter(skill_path),
        'meta': validate_meta(skill_path),
        'structure': validate_structure(skill_path)
    }

    all_valid = all(r['valid'] for r in results.values())

    for check, result in results.items():
        status = "✅ 通过" if result['valid'] else "❌ 失败"
        print(f"\n{check.upper()}: {status}")
        if not result['valid']:
            print(f"  错误: {result['error']}")
        else:
            for key, value in result.items():
                if key != 'valid':
                    print(f"  {key}: {value}")

    print("\n" + "=" * 50)
    print(f"总体结果: {'✅ 所有检查通过' if all_valid else '❌ 存在问题'}")
    print("=" * 50)

    return 0 if all_valid else 1


if __name__ == '__main__':
    exit(main())
