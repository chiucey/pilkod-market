#!/usr/bin/env python3
"""
快速验证脚本 - 检查数学课件生成器技能的结构完整性
"""

import os
import re
import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
REQUIRED_FILES = [
    'SKILL.md',
    '_meta.json'
]
REQUIRED_REFS = [
    'katex-syntax.md',
    'jsxgraph-patterns.md',
    'mermaid-patterns.md',
    'css-styles.md'
]


def check_frontmatter():
    """检查 SKILL.md 的 frontmatter 格式"""
    skill_md = SKILL_DIR / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md 不存在"

    content = skill_md.read_text(encoding='utf-8')

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter，请检查格式"

    frontmatter = frontmatter_match.group(1)

    # 检查必填字段
    if 'name:' not in frontmatter:
        return False, "frontmatter 缺少 name 字段"
    if 'description:' not in frontmatter:
        return False, "frontmatter 缺少 description 字段"

    # 检查 description 是否包含触发短语
    if '当用户' not in frontmatter and 'Use when' not in frontmatter:
        return False, "description 应包含触发短语（如 '当用户...' 或 'Use when...'）"

    return True, "Frontmatter 格式正确"


def check_meta_json():
    """检查 _meta.json 的格式"""
    meta_json = SKILL_DIR / '_meta.json'
    if not meta_json.exists():
        return False, "_meta.json 不存在"

    try:
        data = json.loads(meta_json.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"

    # 检查必填字段
    if 'id' not in data:
        return False, "_meta.json 缺少 id 字段"
    if 'version' not in data:
        return False, "_meta.json 缺少 version 字段"

    return True, "_meta.json 格式正确"


def check_directory_structure():
    """检查目录结构"""
    required_dirs = ['scripts', 'references', 'assets']

    for dir_name in required_dirs:
        dir_path = SKILL_DIR / dir_name
        if not dir_path.exists():
            return False, f"缺少 {dir_name}/ 目录"

    return True, "目录结构完整"


def check_references():
    """检查参考文档"""
    missing = []
    for ref_file in REQUIRED_REFS:
        ref_path = SKILL_DIR / 'references' / ref_file
        if not ref_path.exists():
            missing.append(ref_file)

    if missing:
        return False, f"缺少参考文档: {', '.join(missing)}"

    return True, "参考文档完整"


def check_file_paths():
    """检查路径和名称是否为英文"""
    # 检查文件夹名称
    folder_name = SKILL_DIR.name
    if not re.match(r'^[a-z0-9\-]+$', folder_name):
        return False, f"文件夹名称必须使用英文小写字母、数字和连字符: {folder_name}"

    # 检查 meta.json 中的 name 字段
    meta_json = SKILL_DIR / '_meta.json'
    if meta_json.exists():
        data = json.loads(meta_json.read_text(encoding='utf-8'))
        if 'id' in data and not re.match(r'^[a-z0-9\-_]+$', data['id']):
            return False, f"技能 ID 必须使用英文: {data['id']}"

    return True, "路径和名称验证通过"


def main():
    """主验证函数"""
    print("=" * 50)
    print("数学课件生成器技能 - 快速验证")
    print("=" * 50)
    print()

    all_passed = True
    results = []

    # 1. Frontmatter 检查
    print("[1/5] 检查 Frontmatter 格式...")
    passed, msg = check_frontmatter()
    results.append(("Frontmatter", passed, msg))
    print(f"    {'✅' if passed else '❌'} {msg}")
    if not passed:
        all_passed = False
    print()

    # 2. _meta.json 检查
    print("[2/5] 检查 _meta.json 格式...")
    passed, msg = check_meta_json()
    results.append(("_meta.json", passed, msg))
    print(f"    {'✅' if passed else '❌'} {msg}")
    if not passed:
        all_passed = False
    print()

    # 3. 目录结构检查
    print("[3/5] 检查目录结构...")
    passed, msg = check_directory_structure()
    results.append(("目录结构", passed, msg))
    print(f"    {'✅' if passed else '❌'} {msg}")
    if not passed:
        all_passed = False
    print()

    # 4. 参考文档检查
    print("[4/5] 检查参考文档...")
    passed, msg = check_references()
    results.append(("参考文档", passed, msg))
    print(f"    {'✅' if passed else '❌'} {msg}")
    if not passed:
        all_passed = False
    print()

    # 5. 路径验证
    print("[5/5] 检查路径和名称...")
    passed, msg = check_file_paths()
    results.append(("路径验证", passed, msg))
    print(f"    {'✅' if passed else '❌'} {msg}")
    if not passed:
        all_passed = False
    print()

    # 总结
    print("=" * 50)
    if all_passed:
        print("✅ 所有检查通过！技能结构完整。")
        return 0
    else:
        print("❌ 部分检查未通过，请修复后重试。")
        return 1


if __name__ == '__main__':
    exit(main())