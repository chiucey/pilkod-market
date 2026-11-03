#!/usr/bin/env python3
"""
PPT Translator - 快速验证脚本

验证技能配置和文件结构是否正确
"""

import os
import sys
import json
from pathlib import Path


def validate_skill_structure(skill_path: str) -> bool:
    """验证技能目录结构"""
    print("正在验证技能结构...")

    required_files = {
        'SKILL.md': '技能核心文件',
        '_meta.json': '技能元数据',
    }

    required_dirs = {
        'scripts': '脚本目录',
        'references': '参考文档目录',
    }

    all_valid = True

    # 检查必需文件
    for filename, desc in required_files.items():
        filepath = os.path.join(skill_path, filename)
        if os.path.exists(filepath):
            print(f"  ✓ {filename} - {desc}")
        else:
            print(f"  ✗ {filename} - 缺失 {desc}")
            all_valid = False

    # 检查必需目录
    for dirname, desc in required_dirs.items():
        dirpath = os.path.join(skill_path, dirname)
        if os.path.isdir(dirpath):
            print(f"  ✓ {dirname}/ - {desc}")
        else:
            print(f"  ✗ {dirname}/ - 缺失 {desc}")
            all_valid = False

    return all_valid


def validate_frontmatter(skill_path: str) -> bool:
    """验证SKILL.md的frontmatter"""
    print("\n正在验证frontmatter...")

    skill_md = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md):
        print("  ✗ SKILL.md 文件不存在")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否存在
    if not content.startswith('---'):
        print("  ✗ SKILL.md 必须以 YAML frontmatter 开头")
        return False

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False
    frontmatter_ended = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_ended = True
                break
        elif in_frontmatter:
            frontmatter_lines.append(line)

    if not frontmatter_ended:
        print("  ✗ YAML frontmatter 未正确闭合")
        return False

    # 解析frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key = line.split(':')[0].strip()
            frontmatter[key] = True

    # 检查必需字段
    required_fields = ['name', 'description']
    all_valid = True

    for field in required_fields:
        if field in frontmatter:
            print(f"  ✓ {field}: 字段存在")
        else:
            print(f"  ✗ {field}: 缺少必需字段")
            all_valid = False

    # 检查name格式
    if 'name' in frontmatter:
        # 查找name开头的行（可能有缩进）
        name_line = next((line for line in frontmatter_lines
                         if line.strip().startswith('name:')), None)
        if name_line:
            name_value = name_line.split(':', 1)[1].strip()
            if ' ' in name_value and name_value != '':
                print("  ✗ name 不能包含空格，请使用连字符")
                all_valid = False
            else:
                print(f"  ✓ name 格式正确 (值为: {name_value})")

    return all_valid


def validate_meta_json(skill_path: str) -> bool:
    """验证_meta.json"""
    print("\n正在验证 _meta.json...")

    meta_path = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_path):
        print("  ✗ _meta.json 文件不存在")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        if 'id' in meta:
            print(f"  ✓ id: {meta['id']}")
        else:
            print("  ✗ id: 缺少必需字段")
            return False

        if 'version' in meta:
            print(f"  ✓ version: {meta['version']}")
        else:
            print("  ✗ version: 缺少必需字段")
            return False

        return True

    except json.JSONDecodeError as e:
        print(f"  ✗ JSON解析错误: {e}")
        return False


def main():
    """主函数"""
    # 获取技能目录路径
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # 默认路径
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"=== PPT Translator 技能验证 ===")
    print(f"技能路径: {skill_path}\n")

    results = []

    # 执行各项验证
    results.append(("目录结构", validate_skill_structure(skill_path)))
    results.append(("Frontmatter", validate_frontmatter(skill_path)))
    results.append(("_meta.json", validate_meta_json(skill_path)))

    # 汇总结果
    print("\n" + "=" * 40)
    print("验证结果汇总:")
    print("=" * 40)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试")
        return 1


if __name__ == '__main__':
    sys.exit(main())
