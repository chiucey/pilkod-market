#!/usr/bin/env python3
"""
技能验证脚本
验证视频字幕生成器技能的结构和内容
"""

import os
import json
from pathlib import Path

def validate_structure(skill_dir: Path) -> list:
    """验证技能目录结构"""
    errors = []

    # 必需文件检查
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        file_path = skill_dir / f
        if not file_path.exists():
            errors.append(f"缺少必需文件: {f}")

    # 目录检查
    expected_dirs = ['scripts', 'references']
    for d in expected_dirs:
        dir_path = skill_dir / d
        if not dir_path.exists():
            errors.append(f"缺少目录: {d}")

    return errors

def validate_skills_md(skill_dir: Path) -> list:
    """验证 SKILL.md 内容"""
    errors = []
    skills_md = skill_dir / 'SKILL.md'

    if not skills_md.exists():
        return ["SKILL.md 文件不存在"]

    content = skills_md.read_text(encoding='utf-8')

    # 检查 frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")
    else:
        # 提取 frontmatter
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            errors.append("Frontmatter 未正确闭合")
        else:
            frontmatter_text = '\n'.join(lines[1:frontmatter_end])

            # 检查必需字段
            if 'name:' not in frontmatter_text:
                errors.append("Frontmatter 缺少 name 字段")
            if 'description:' not in frontmatter_text:
                errors.append("Frontmatter 缺少 description 字段")

    return errors

def validate_meta_json(skill_dir: Path) -> list:
    """验证 _meta.json 内容"""
    errors = []
    meta_json = skill_dir / '_meta.json'

    if not meta_json.exists():
        return ["_meta.json 文件不存在"]

    try:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        if 'id' not in meta:
            errors.append("_meta.json 缺少 id 字段")
        if 'version' not in meta:
            errors.append("_meta.json 缺少 version 字段")

        # 验证 id 格式
        if 'id' in meta and not isinstance(meta['id'], str):
            errors.append("_meta.json id 必须是字符串")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 格式错误: {e}")

    return errors

def validate_scripts(skill_dir: Path) -> list:
    """验证脚本文件"""
    errors = []
    scripts_dir = skill_dir / 'scripts'

    if not scripts_dir.exists():
        return []  # scripts 目录是可选的

    # 检查核心脚本是否存在
    core_script = scripts_dir / 'generate_subtitles.py'
    if not core_script.exists():
        errors.append("缺少核心脚本: scripts/generate_subtitles.py")

    return errors

def main():
    skill_dir = Path(__file__).parent.parent
    all_errors = []

    print(f"正在验证技能: {skill_dir.name}")
    print("-" * 40)

    # 执行各项验证
    all_errors.extend(validate_structure(skill_dir))
    all_errors.extend(validate_skills_md(skill_dir))
    all_errors.extend(validate_meta_json(skill_dir))
    all_errors.extend(validate_scripts(skill_dir))

    # 输出结果
    if all_errors:
        print("\n验证失败:")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("\n验证通过!")
        return 0

if __name__ == '__main__':
    exit(main())
