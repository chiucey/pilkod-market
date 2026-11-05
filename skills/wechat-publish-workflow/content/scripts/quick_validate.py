#!/usr/bin/env python3
"""
微信公众号发布工作流 - 快速验证脚本
验证 SKILL.md 和 _meta.json 的基本格式
"""

import os
import sys
import re
import json
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证 SKILL.md frontmatter 格式"""
    sk_md = Path(skill_path) / "SKILL.md"

    if not sk_md.exists():
        return False, "SKILL.md 文件不存在"

    content = sk_md.read_text(encoding='utf-8')

    # 检查是否以 frontmatter 开始
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 frontmatter (---) 开头，不能有标题或空格"

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        return False, "frontmatter 格式不正确"

    # 找到 frontmatter 结束
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return False, "frontmatter 未正确关闭"

    # 解析 frontmatter
    fm_text = '\n'.join(lines[1:end_idx+1])
    fm = {}
    for line in lines[1:end_idx]:
        if ':' in line:
            key, value = line.split(':', 1)
            fm[key.strip()] = value.strip()

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in fm:
            return False, f"frontmatter 缺少必需字段: {field}"

    # 验证 name 格式
    name = fm['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"name 必须使用小写字母、数字和连字符: {name}"

    # 验证 description
    desc = fm['description']
    if len(desc) < 10:
        return False, "description 太短，需要更详细的描述"

    return True, "frontmatter 验证通过"

def validate_meta(skill_path):
    """验证 _meta.json 格式"""
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, f"_meta.json 格式错误: {e}"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少字段: {field}"

    # 验证 id
    skill_id = meta['id']
    if not isinstance(skill_id, str):
        return False, "_meta.json id 必须是字符串"

    # 验证 version
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"version 格式不正确，应为 semver 格式: {version}"

    return True, "_meta.json 验证通过"

def validate_structure(skill_path):
    """验证目录结构"""
    required_dirs = ['references']
    optional_dirs = ['scripts', 'assets']

    skill_path = Path(skill_path)

    # 检查必需目录
    for d in required_dirs:
        if not (skill_path / d).exists():
            return False, f"缺少必需目录: {d}"

    return True, "目录结构验证通过"

def validate_references(skill_path):
    """验证 references 目录内容"""
    refs_dir = Path(skill_path) / "references"

    if not refs_dir.exists():
        return True, "references 目录为空（可选）"

    md_files = list(refs_dir.glob("*.md"))
    if not md_files:
        return True, "references 目录为空（可选）"

    for f in md_files:
        content = f.read_text(encoding='utf-8')
        if len(content) < 100:
            return False, f"{f.name} 内容太少，需要更详细的文档"

    return True, "references 内容验证通过"

def main():
    # 获取技能路径（默认当前目录）
    skill_path = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"验证技能: {skill_path}")
    print("=" * 50)

    checks = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta),
        ("目录结构", validate_structure),
        ("References", validate_references),
    ]

    all_passed = True
    for name, func in checks:
        try:
            passed, msg = func(skill_path)
            status = "✓" if passed else "✗"
            print(f"[{status}] {name}: {msg}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"[✗] {name}: 验证出错 - {e}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
