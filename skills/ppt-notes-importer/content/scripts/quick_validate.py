#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和依赖
"""

import os
import sys
from pathlib import Path

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent

def check_structure():
    """检查技能目录结构"""
    print("检查技能目录结构...")
    print(f"技能根目录: {SKILL_ROOT}")
    print()

    required_files = [
        'SKILL.md',
        '_meta.json',
        'scripts/import_notes.py',
        'references/format_guide.md'
    ]

    all_exist = True
    for file_path in required_files:
        full_path = SKILL_ROOT / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (缺失)")
            all_exist = False

    return all_exist

def check_frontmatter():
    """检查SKILL.md的frontmatter"""
    print()
    print("检查SKILL.md frontmatter...")

    skill_md = SKILL_ROOT / 'SKILL.md'
    if not skill_md.exists():
        print("  ✗ SKILL.md不存在")
        return False

    content = skill_md.read_text(encoding='utf-8')

    # 检查是否以---开头
    if not content.startswith('---'):
        print("  ✗ frontmatter必须以---开头")
        return False

    # 检查必要的字段
    required_fields = ['name:', 'description:']
    all_present = True
    for field in required_fields:
        if field in content:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} (缺失)")
            all_present = False

    return all_present

def check_meta_json():
    """检查_meta.json"""
    print()
    print("检查_meta.json...")

    meta_path = SKILL_ROOT / '_meta.json'
    if not meta_path.exists():
        print("  ✗ _meta.json不存在")
        return False

    import json
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_fields = ['id', 'version']
        all_present = True
        for field in required_fields:
            if field in meta:
                print(f"  ✓ {field}: {meta[field]}")
            else:
                print(f"  ✗ {field} (缺失)")
                all_present = False

        return all_present
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 读取错误: {e}")
        return False

def check_python_dependency():
    """检查Python依赖"""
    print()
    print("检查Python依赖...")

    try:
        from pptx import Presentation
        print("  ✓ python-pptx 已安装")
        return True
    except ImportError:
        print("  ✗ python-pptx 未安装")
        print("    请运行: pip install python-pptx")
        return False

def main():
    print("=" * 50)
    print("技能验证脚本")
    print("=" * 50)
    print()

    checks = [
        ("目录结构", check_structure),
        ("Frontmatter", check_frontmatter),
        ("_meta.json", check_meta_json),
        ("Python依赖", check_python_dependency),
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    print()
    print("=" * 50)
    print("验证结果汇总：")
    print("=" * 50)

    all_passed = True
    for name, result in results:
        status = "通过" if result else "失败"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {name}: {status}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("✓ 所有检查通过！")
        return 0
    else:
        print("✗ 部分检查失败，请修复后重试")
        return 1

if __name__ == '__main__':
    sys.exit(main())
