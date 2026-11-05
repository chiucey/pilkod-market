#!/usr/bin/env python3
"""
经典战役解说视频生成器 - 技能验证脚本
验证 SKILL.md 的完整性和格式正确性
"""

import json
import os
import sys
from pathlib import Path


def validate_frontmatter(skill_md_content: str) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    if not skill_md_content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头"

    lines = skill_md_content.split('\n')
    if len(lines) < 4:
        return False, "frontmatter 内容不足"

    # 找到第二个 ---
    second_dash = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            second_dash = i
            break

    if second_dash == -1:
        return False, "缺少结束 --- 分隔符"

    frontmatter_lines = lines[1:second_dash]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if f"{field}:" not in frontmatter_text:
            return False, f"缺少必需字段: {field}"

    return True, "Frontmatter 验证通过"


def validate_structure(base_path: Path) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = base_path / file
        if not file_path.exists():
            errors.append(f"缺少必需文件: {file}")

    # 检查 _meta.json
    meta_path = base_path / '_meta.json'
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    return len(errors) == 0, errors


def validate_naming(skill_md_content: str, folder_name: str) -> tuple[bool, str]:
    """验证命名规范"""
    # 检查 frontmatter 中的 name 是否与文件夹名称匹配
    lines = skill_md_content.split('\n')
    name_value = None
    for line in lines[1:]:
        if line.strip().startswith('name:'):
            name_value = line.split(':', 1)[1].strip()
            break

    if name_value and name_value != folder_name:
        return False, f"name '{name_value}' 与文件夹名称 '{folder_name}' 不匹配"

    return True, "命名验证通过"


def main():
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    print(f"验证技能: {skill_dir.name}")
    print("=" * 50)

    all_valid = True

    # 1. 检查文件存在
    skill_md_path = skill_dir / 'SKILL.md'
    if not skill_md_path.exists():
        print("❌ 缺少 SKILL.md 文件")
        sys.exit(1)

    # 2. 读取并验证 SKILL.md
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 验证 frontmatter
    valid, msg = validate_frontmatter(content)
    print(f"{'✓' if valid else '❌'} Frontmatter: {msg}")
    all_valid = all_valid and valid

    # 验证命名
    valid, msg = validate_naming(content, skill_dir.name)
    print(f"{'✓' if valid else '❌'} 命名规范: {msg}")
    all_valid = all_valid and valid

    # 3. 验证目录结构
    valid, errors = validate_structure(skill_dir)
    if errors:
        for error in errors:
            print(f"❌ {error}")
        all_valid = False
    else:
        print("✓ 目录结构验证通过")

    # 4. 检查 references 目录
    references_dir = skill_dir / 'references'
    if references_dir.exists():
        ref_files = list(references_dir.glob('*.json'))
        print(f"✓ references 目录: 包含 {len(ref_files)} 个参考文件")

    print("=" * 50)
    if all_valid:
        print("✅ 验证通过！技能结构完整。")
        sys.exit(0)
    else:
        print("❌ 验证失败！请修复以上问题。")
        sys.exit(1)


if __name__ == '__main__':
    main()
