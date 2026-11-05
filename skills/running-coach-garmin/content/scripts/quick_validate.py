#!/usr/bin/env python3
"""
快速验证脚本 - running-coach-garmin 技能
检查 SKILL.md frontmatter、_meta.json 和目录结构
"""

import os
import re
import sys
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def ok(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def err(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def warn(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否是 ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        err(f"SKILL.md 第一行必须是 '---'，当前第一行: {lines[0][:50]}...")
        return False

    # 找到第二个 ---
    second_dash_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            second_dash_idx = i
            break

    if second_dash_idx is None:
        err("找不到 frontmatter 结束标记 '---'")
        return False

    # 解析 frontmatter
    frontmatter_lines = lines[1:second_dash_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    try:
        frontmatter = {}
        for line in frontmatter_lines:
            if ':' in line:
                key, val = line.split(':', 1)
                frontmatter[key.strip()] = val.strip().strip('"')
    except Exception as e:
        err(f"Frontmatter 解析失败: {e}")
        return False

    # 检查必需字段
    required_fields = ['name', 'description']
    all_ok = True
    for field in required_fields:
        if field not in frontmatter:
            err(f"缺少必需字段: {field}")
            all_ok = False

    if all_ok:
        ok(f"Frontmatter 格式正确，包含所有必需字段")

    # 检查 name 格式 (连字符)
    name = frontmatter.get('name', '')
    if name and not re.match(r'^[a-z][a-z0-9-]*$', name):
        err(f"name 格式错误，应使用连字符格式 (e.g., 'my-skill'): {name}")
        all_ok = False
    elif name:
        ok(f"name 格式正确: {name}")

    # 检查 description 触发短语
    desc = frontmatter.get('description', '')
    trigger_phrases = ['当用户要求', '使用当', 'Use when', 'When users']
    has_trigger = any(phrase.lower() in desc.lower() for phrase in trigger_phrases)
    if has_trigger:
        ok(f"description 包含触发短语")
    else:
        warn(f"description 建议包含触发短语 (如 '当用户要求...')")

    return all_ok

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    if not os.path.exists(meta_path):
        err(f"_meta.json 不存在: {meta_path}")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        err(f"_meta.json JSON 解析失败: {e}")
        return False

    required_fields = ['id', 'version']
    all_ok = True
    for field in required_fields:
        if field not in meta:
            err(f"缺少必需字段: {field}")
            all_ok = False

    if all_ok:
        ok(f"_meta.json 格式正确")

    # 验证 id 是数字
    if 'id' in meta:
        try:
            int(meta['id'])
            ok(f"技能 ID 有效: {meta['id']}")
        except ValueError:
            err(f"技能 ID 必须是数字，当前: {meta['id']}")
            all_ok = False

    # 验证 version 格式
    if 'version' in meta:
        if re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            ok(f"版本格式正确: {meta['version']}")
        else:
            err(f"版本格式错误，应为 semver (如 1.0.0): {meta['version']}")
            all_ok = False

    return all_ok

def validate_directory_structure(skill_dir):
    """验证目录结构安全性"""
    # 检查没有符号链接逃逸
    skill_path = Path(skill_dir).resolve()
    for root, dirs, files in os.walk(skill_path):
        root_path = Path(root).resolve()
        try:
            root_path.relative_to(skill_path)
        except ValueError:
            err(f"目录结构不安全: {root} 不在技能目录内")
            return False

    ok("目录结构安全，无符号链接逃逸")
    return True

def validate_file_naming(skill_dir):
    """验证文件名都是英文"""
    skill_path = Path(skill_dir)
    non_english_files = []

    for f in skill_path.rglob('*'):
        if f.is_file():
            # 检查文件名是否包含非 ASCII 字符
            if not f.name.isascii():
                non_english_files.append(f.name)

    if non_english_files:
        err(f"发现非英文文件名: {', '.join(non_english_files)}")
        return False

    ok("所有文件名都是英文")
    return True

def validate_scripts(skill_dir):
    """验证 scripts 目录中的脚本"""
    scripts_dir = Path(skill_dir) / 'scripts'
    if not scripts_dir.exists():
        return True  # scripts 可选

    all_ok = True
    for script in scripts_dir.glob('*.py'):
        # 检查脚本语法
        try:
            with open(script, 'r', encoding='utf-8') as f:
                compile(f.read(), script.name, 'exec')
            ok(f"脚本语法正确: {script.name}")
        except SyntaxError as e:
            err(f"脚本语法错误 {script.name}: {e}")
            all_ok = False

    return all_ok

def main():
    # 获取技能根目录（脚本所在目录的父目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    skill_name = Path(skill_dir).name

    print(f"\n{'='*60}")
    print(f"技能验证: {skill_name}")
    print(f"{'='*60}\n")

    all_checks_pass = True

    # 1. 验证 frontmatter
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if not validate_frontmatter(skill_md):
        all_checks_pass = False

    # 2. 验证 _meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    if not validate_meta_json(meta_json):
        all_checks_pass = False

    # 3. 验证目录结构
    if not validate_directory_structure(skill_dir):
        all_checks_pass = False

    # 4. 验证文件名
    if not validate_file_naming(skill_dir):
        all_checks_pass = False

    # 5. 验证脚本语法
    if not validate_scripts(skill_dir):
        all_checks_pass = False

    print(f"\n{'='*60}")
    if all_checks_pass:
        print(f"{Colors.GREEN}✓ 所有验证通过{Colors.RESET}")
        print(f"{'='*60}\n")
        return 0
    else:
        print(f"{Colors.RED}✗ 部分验证失败，请修复后重试{Colors.RESET}")
        print(f"{'='*60}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())