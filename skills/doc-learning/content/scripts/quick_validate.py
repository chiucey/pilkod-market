#!/usr/bin/env python3
"""
快速验证脚本 - 检查 doc-learning 技能的结构和格式
"""

import os
import json
import re
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 YAML frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    if 'name:' not in frontmatter:
        return False, "缺少 'name' 字段"
    if 'description:' not in frontmatter:
        return False, "缺少 'description' 字段"

    # 检查 frontmatter 之前是否有 markdown 标题（即确保 --- 在最前面）
    first_lines = content[:100]  # 只检查文件开头部分
    lines_before_first_dash = first_lines.split('---')[0] if '---' in first_lines else content
    if lines_before_first_dash.strip().startswith('#'):
        return False, "Frontmatter 之前不应有 markdown 标题（#）"

    return True, "Frontmatter 验证通过"

def validate_meta(meta_path):
    """验证 _meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "_meta.json 缺少 'id' 字段"
    if 'version' not in meta:
        return False, "_meta.json 缺少 'version' 字段"

    return True, "_meta.json 验证通过"

def validate_naming(path):
    """验证路径和名称是否只包含英文"""
    name = os.path.basename(path).lower()

    # 检查是否包含中文字符
    if re.search(r'[\u4e00-\u9fff]', name):
        return False, f"路径 '{path}' 包含中文字符"

    return True, f"命名验证通过: {path}"

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    meta_json = skill_dir / "_meta.json"

    results = []

    # 验证 SKILL.md
    if skill_md.exists():
        valid, msg = validate_frontmatter(skill_md)
        results.append(("Frontmatter", valid, msg))
    else:
        results.append(("Frontmatter", False, "SKILL.md 不存在"))

    # 验证 _meta.json
    valid, msg = validate_meta(meta_json)
    results.append(("_meta.json", valid, msg))

    # 验证目录名称
    valid, msg = validate_naming(skill_dir)
    results.append(("目录命名", valid, msg))

    # 验证 SKILL.md 文件名
    valid, msg = validate_naming(skill_md)
    results.append(("文件名", valid, msg))

    # 打印结果
    print("=" * 50)
    print("doc-learning 技能验证结果")
    print("=" * 50)

    all_passed = True
    for name, valid, msg in results:
        status = "✓" if valid else "✗"
        print(f"{status} {name}: {msg}")
        if not valid:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("所有验证通过！")
        return 0
    else:
        print("存在验证失败项，请修复后重试。")
        return 1

if __name__ == "__main__":
    exit(main())
