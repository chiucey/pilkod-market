#!/usr/bin/env python3
"""
简历优化专家技能验证脚本
验证SKILL.md、AGENTS.md、SOUL.md文件结构和内容规范
"""

import os
import re
import json
from pathlib import Path

SKILL_ROOT = Path("/workspace/temp-skills/ji-si-2026-resume-optimizer-v25")

def check_frontmatter(filepath):
    """检查frontmatter格式"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # SKILL.md必须有frontmatter
    if filepath.name == "SKILL.md":
        if not content.startswith('---'):
            return False, "SKILL.md必须以frontmatter开头"

        # 提取frontmatter
        lines = content.split('\n')
        fm_end = -1
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '---':
                fm_end = i
                break

        if fm_end == -1:
            return False, "frontmatter未正确闭合"

        fm_content = '\n'.join(lines[1:fm_end])

        # 检查必需字段
        if 'name:' not in fm_content:
            return False, "缺少name字段"
        if 'description:' not in fm_content:
            return False, "缺少description字段"

    return True, "通过"

def check_meta_json():
    """检查_meta.json格式"""
    meta_path = SKILL_ROOT / "_meta.json"

    if not meta_path.exists():
        return False, "_meta.json不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json缺少{field}字段"

    return True, "通过"

def check_output_format():
    """检查输出格式规范"""
    agents_path = SKILL_ROOT / "AGENTS.md"
    soul_path = SKILL_ROOT / "SOUL.md"

    issues = []

    # AGENTS.md必须包含合规声明要求
    with open(agents_path, 'r', encoding='utf-8') as f:
        agents_content = f.read()

    if '合规声明' not in agents_content:
        issues.append("AGENTS.md缺少合规声明要求")

    if '最后一行' not in agents_content:
        issues.append("AGENTS.md缺少最后一行规范")

    if '三段式' not in agents_content.lower():
        issues.append("AGENTS.md缺少三段式输出要求")

    # SOUL.md必须包含输出限制
    with open(soul_path, 'r', encoding='utf-8') as f:
        soul_content = f.read()

    if '真实性' not in soul_content:
        issues.append("SOUL.md缺少真实性原则")

    if issues:
        return False, "; ".join(issues)

    return True, "通过"

def main():
    """执行所有验证"""
    print("=" * 50)
    print("简历优化专家技能验证")
    print("=" * 50)

    # 1. 检查SKILL.md frontmatter
    print("\n[1] 检查SKILL.md frontmatter...")
    valid, msg = check_frontmatter(SKILL_ROOT / "SKILL.md")
    print(f"    {'✓' if valid else '✗'} {msg}")

    # 2. 检查_meta.json
    print("\n[2] 检查_meta.json...")
    valid, msg = check_meta_json()
    print(f"    {'✓' if valid else '✗'} {msg}")

    # 3. 检查输出格式
    print("\n[3] 检查输出格式规范...")
    valid, msg = check_output_format()
    print(f"    {'✓' if valid else '✗'} {msg}")

    # 4. 检查文件完整性
    print("\n[4] 检查文件完整性...")
    required_files = ['SKILL.md', '_meta.json', 'AGENTS.md', 'SOUL.md']
    for fname in required_files:
        path = SKILL_ROOT / fname
        status = '✓' if path.exists() else '✗'
        print(f"    {status} {fname}")

    # 5. 检查references目录
    print("\n[5] 检查references目录...")
    ref_dir = SKILL_ROOT / "references"
    if ref_dir.exists():
        ref_files = list(ref_dir.glob("*.md"))
        print(f"    ✓ 包含{len(ref_files)}个参考文档")
        for rf in ref_files:
            print(f"      - {rf.name}")
    else:
        print("    ✗ references目录不存在")

    print("\n" + "=" * 50)
    print("验证完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
