#!/usr/bin/env python3
"""
股票趋势交易操作系统技能验证脚本
验证 SKILL.md 格式和数据准确性
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证 frontmatter 格式"""
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_md.read_text(encoding='utf-8')

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter --- 开头"

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "未找到 YAML frontmatter 结束标记 ---"

    frontmatter = '\n'.join(lines[1:frontmatter_end])

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter, re.MULTILINE):
            return False, f"frontmatter 缺少必填字段: {field}"

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 必须使用连字符格式（hyphen-case），当前: {name}"

    return True, "frontmatter 格式正确"

def validate_structure(skill_path):
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    # 检查必填文件
    if not (Path(skill_path) / "SKILL.md").exists():
        return False, "缺少 SKILL.md"

    if not (Path(skill_path) / "_meta.json").exists():
        return False, "缺少 _meta.json"

    # 检查 _meta.json 格式
    meta_path = Path(skill_path) / "_meta.json"
    if meta_path.exists():
        import json
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            if 'id' not in meta or 'version' not in meta:
                return False, "_meta.json 必须包含 id 和 version"
        except json.JSONDecodeError:
            return False, "_meta.json 格式错误"

    return True, "目录结构正确"

def validate_references(skill_path):
    """验证参考文档"""
    refs_path = Path(skill_path) / "references"
    if refs_path.exists():
        md_files = list(refs_path.glob("*.md"))
        if len(md_files) < 2:
            return False, f"references 目录应包含至少2个参考文档，当前: {len(md_files)}"
    return True, "参考文档完整"

def validate_trigger_phrases(skill_path):
    """验证触发短语"""
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text(encoding='utf-8')

    # 提取 description
    desc_match = re.search(r'^description:\s*\|?\s*\n(.*?)(?=^---|\n# |\Z)',
                          content, re.MULTILINE | re.DOTALL)
    if not desc_match:
        return False, "未找到 description 字段"

    desc = desc_match.group(1)

    # 检查触发短语示例
    if '触发短语示例' not in desc and 'trigger' not in desc.lower():
        return False, "description 中应包含触发短语示例"

    return True, "触发短语设置完整"

def main():
    skill_path = "/workspace/temp-skills/stock-trend-trading-system"

    checks = [
        ("Frontmatter 验证", validate_frontmatter),
        ("目录结构验证", validate_structure),
        ("参考文档验证", validate_references),
        ("触发短语验证", validate_trigger_phrases),
    ]

    all_passed = True
    print("=" * 50)
    print("股票趋势交易操作系统技能验证")
    print("=" * 50)

    for name, check_func in checks:
        try:
            passed, message = check_func(skill_path)
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} | {name}: {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"✗ FAIL | {name}: 验证出错 - {str(e)}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("验证结果：全部通过 ✓")
        return 0
    else:
        print("验证结果：存在失败项 ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
