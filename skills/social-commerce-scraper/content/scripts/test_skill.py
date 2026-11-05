#!/usr/bin/env python3
"""
社交电商热销商品抓取技能 - 测试脚本
测试技能的核心功能
"""

import sys
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """测试模块导入"""
    try:
        import json
        import re
        from pathlib import Path
        return True
    except ImportError as e:
        print(f"模块导入失败: {e}")
        return False

def test_regex():
    """测试正则表达式匹配"""
    import re

    # 测试frontmatter解析
    test_content = """---
name: social-commerce-scraper
description: Test description
---

# Content
"""
    frontmatter_match = re.match(r'^---\n(.*?)\n---', test_content, re.DOTALL)
    if not frontmatter_match:
        print("Frontmatter正则解析失败")
        return False

    # 测试name提取
    name_match = re.search(r'^name:\s*(.+)', frontmatter_match.group(1), re.MULTILINE)
    if not name_match:
        print("Name提取失败")
        return False

    if name_match.group(1).strip() != "social-commerce-scraper":
        print("Name值不正确")
        return False

    return True

def test_directory():
    """测试目录结构"""
    skill_dir = Path(__file__).parent.parent

    required_files = [
        "SKILL.md",
        "_meta.json",
    ]

    for filename in required_files:
        if not (skill_dir / filename).exists():
            print(f"缺少必需文件: {filename}")
            return False

    return True

def test_meta_json():
    """测试_meta.json格式"""
    import json

    skill_dir = Path(__file__).parent.parent
    meta_file = skill_dir / "_meta.json"

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta or 'version' not in meta:
        print("_meta.json缺少必需字段")
        return False

    return True

def run_tests():
    """运行所有测试"""
    print("=" * 50)
    print("运行技能测试")
    print("=" * 50)
    print()

    tests = [
        ("模块导入测试", test_import),
        ("正则表达式测试", test_regex),
        ("目录结构测试", test_directory),
        ("meta.json测试", test_meta_json),
    ]

    results = []
    for name, test_func in tests:
        print(f"执行 {name}...")
        try:
            result = test_func()
            results.append(result)
            if result:
                print(f"  ✓ 通过")
            else:
                print(f"  ✗ 失败")
        except Exception as e:
            print(f"  ✗ 异常: {e}")
            results.append(False)
        print()

    print("=" * 50)
    if all(results):
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
