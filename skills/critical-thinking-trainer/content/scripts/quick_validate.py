#!/usr/bin/env python3
"""
批判性思维训练师技能快速验证脚本
"""

import json
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path: Path) -> tuple[bool, list[str]]:
    """验证 frontmatter 格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头（可能有空行在前面）
    lines = content.split('\n')
    start_idx = None
    end_idx = None

    # 找到开始标记 ---
    for i, line in enumerate(lines):
        if line.strip() == '---':
            start_idx = i
            break

    if start_idx is None:
        errors.append("SKILL.md 必须以 YAML frontmatter 块开头 (---)")
        return False, errors

    # 找到结束标记 ---
    for i, line in enumerate(lines[start_idx + 1:], start=start_idx + 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        errors.append("YAML frontmatter 未正确关闭")
        return False, errors

    # 提取 frontmatter 内容
    frontmatter_text = '\n'.join(lines[start_idx:end_idx + 1])

    # 检查必需字段
    if 'name:' not in frontmatter_text:
        errors.append("Frontmatter 缺少 name 字段")

    if 'description:' not in frontmatter_text:
        errors.append("Frontmatter 缺少 description 字段")

    # 提取 name 值
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # 检查是否与目录名匹配
        expected_name = skill_md_path.parent.name
        if name != expected_name:
            errors.append(f"name 字段值 '{name}' 与目录名 '{expected_name}' 不匹配")

    # 检查 frontmatter 之前是否有 markdown 标题（允许空行）
    before_frontmatter = '\n'.join(lines[:start_idx])
    if '#' in before_frontmatter:
        errors.append("Frontmatter 之前不应有 markdown 标题")

    return len(errors) == 0, errors

def validate_meta_json(meta_path: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json 缺少 'id' 字段")
        elif not isinstance(meta['id'], (int, str)):
            errors.append("_meta.json 'id' 必须是数字或字符串")

        if 'version' not in meta:
            errors.append("_meta.json 缺少 'version' 字段")
        elif not isinstance(meta['version'], str):
            errors.append("_meta.json 'version' 必须是字符串")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 格式错误: {e}")

    return len(errors) == 0, errors

def main():
    skill_path = Path('/workspace/temp-skills/critical-thinking-trainer')

    print("=" * 50)
    print("批判性思维训练师技能验证")
    print("=" * 50)

    all_valid = True

    # 验证 SKILL.md
    print("\n[1] 验证 SKILL.md frontmatter...")
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        valid, errors = validate_frontmatter(skill_md)
        if valid:
            print("    ✓ SKILL.md frontmatter 验证通过")
        else:
            for error in errors:
                print(f"    ✗ {error}")
            all_valid = False
    else:
        print("    ✗ SKILL.md 文件不存在")
        all_valid = False

    # 验证 _meta.json
    print("\n[2] 验证 _meta.json...")
    meta_json = skill_path / '_meta.json'
    if meta_json.exists():
        valid, errors = validate_meta_json(meta_json)
        if valid:
            print("    ✓ _meta.json 验证通过")
        else:
            for error in errors:
                print(f"    ✗ {error}")
            all_valid = False
    else:
        print("    ✗ _meta.json 文件不存在")
        all_valid = False

    # 检查 references 目录
    print("\n[3] 检查 resources...")
    references = skill_path / 'references'
    if references.exists():
        ref_files = list(references.glob('*.md'))
        print(f"    ✓ references/ 目录存在，包含 {len(ref_files)} 个参考文件")
    else:
        print("    - references/ 目录不存在（可选）")

    # 检查脚本目录
    print("\n[4] 检查 scripts...")
    scripts = skill_path / 'scripts'
    if scripts.exists():
        script_files = list(scripts.glob('*.py'))
        print(f"    ✓ scripts/ 目录存在，包含 {len(script_files)} 个脚本")
    else:
        print("    - scripts/ 目录不存在（可选）")

    # 总结
    print("\n" + "=" * 50)
    if all_valid:
        print("验证结果: 全部通过 ✓")
        print("=" * 50)
        return 0
    else:
        print("验证结果: 存在问题 ✗")
        print("=" * 50)
        return 1

if __name__ == '__main__':
    sys.exit(main())
