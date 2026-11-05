# -*- coding: utf-8 -*-
"""
RAG技能验证脚本

验证skill的基本结构和配置
"""

import os
import sys
import json
from pathlib import Path


def validate_structure(skill_path: str) -> bool:
    """验证目录结构"""
    print("检查目录结构...")

    required_files = {
        "SKILL.md": "技能主文件",
        "_meta.json": "元数据文件",
    }

    required_dirs = {
        "scripts": "脚本目录",
    }

    all_valid = True

    # 检查文件
    for filename, desc in required_files.items():
        filepath = os.path.join(skill_path, filename)
        if os.path.exists(filepath):
            print(f"  ✓ {filename} ({desc})")
        else:
            print(f"  ✗ {filename} 缺失 ({desc})")
            all_valid = False

    # 检查目录
    for dirname, desc in required_dirs.items():
        dirpath = os.path.join(skill_path, dirname)
        if os.path.isdir(dirpath):
            print(f"  ✓ {dirname}/ ({desc})")
        else:
            print(f"  ✗ {dirname}/ 缺失 ({desc})")
            all_valid = False

    return all_valid


def validate_frontmatter(skill_path: str) -> bool:
    """验证Frontmatter"""
    print("\n检查Frontmatter...")

    skilload_md_path = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skilload_md_path):
        print("  ✗ SKILL.md 不存在")
        return False

    with open(skilload_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        print("  ✗ SKILL.md 必须以 --- 开头")
        return False

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        print("  ✗ Frontmatter 未正确关闭")
        return False

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ['name', 'description']
    all_valid = True

    for field in required_fields:
        if field + ':' in frontmatter_text:
            print(f"  ✓ {field} 字段存在")
        else:
            print(f"  ✗ {field} 字段缺失")
            all_valid = False

    # 检查name与目录名是否匹配
    folder_name = os.path.basename(skill_path)
    name_match = False
    for line in lines[1:frontmatter_end]:
        if line.startswith('name:'):
            frontmatter_name = line.split(':', 1)[1].strip()
            if frontmatter_name == folder_name:
                name_match = True
                print(f"  ✓ name 与目录名匹配: {folder_name}")
            else:
                print(f"  ✗ name ({frontmatter_name}) 与目录名 ({folder_name}) 不匹配")
                all_valid = False
            break

    if not name_match:
        # 如果没找到name字段，也报错
        pass

    return all_valid


def validate_meta(skill_path: str) -> bool:
    """验证_meta.json"""
    print("\n检查_meta.json...")

    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        print("  ✗ _meta.json 不存在")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        print("  ✗ _meta.json 格式错误")
        return False

    required_fields = ['id', 'version']
    all_valid = True

    for field in required_fields:
        if field in meta:
            print(f"  ✓ {field}: {meta[field]}")
        else:
            print(f"  ✗ {field} 字段缺失")
            all_valid = False

    return all_valid


def validate_scripts(skill_path: str) -> bool:
    """验证脚本"""
    print("\n检查脚本文件...")

    scripts_path = os.path.join(skill_path, "scripts")

    if not os.path.isdir(scripts_path):
        print("  ✗ scripts 目录不存在")
        return False

    # 检查核心脚本
    required_scripts = ['rag_engine.py']

    all_valid = True
    for script in required_scripts:
        script_path = os.path.join(scripts_path, script)
        if os.path.exists(script_path):
            print(f"  ✓ {script}")
        else:
            print(f"  ✗ {script} 缺失")
            all_valid = False

    return all_valid


def main():
    skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("RAG技能验证")
    print("=" * 60)
    print(f"技能路径: {skill_path}\n")

    results = []

    results.append(("目录结构", validate_structure(skill_path)))
    results.append(("Frontmatter", validate_frontmatter(skill_path)))
    results.append(("元数据", validate_meta(skill_path)))
    results.append(("脚本", validate_scripts(skill_path)))

    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ 所有验证通过！")
        return 0
    else:
        print("\n✗ 存在验证失败项，请修复后重试。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
