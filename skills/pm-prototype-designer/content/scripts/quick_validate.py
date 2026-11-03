#!/usr/bin/env python3
"""
技能验证脚本 - 检查SKILL.md的frontmatter和结构完整性
"""

import os
import re
import sys
from pathlib import Path

# ANSI颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    print(f"{BOLD}ℹ{RESET} {msg}")

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter"""
    errors = []
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md文件不存在")
        return errors, warnings

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在文件开头
    if not content.startswith('---'):
        errors.append("SKILL.md必须以---frontmatter块开头")
    else:
        # 提取frontmatter
        lines = content.split('\n')
        frontmatter_lines = []
        in_frontmatter = False
        frontmatter_end = -1

        for i, line in enumerate(lines):
            if line.strip() == '---' and not in_frontmatter:
                in_frontmatter = True
                frontmatter_lines.append(line)
            elif line.strip() == '---' and in_frontmatter:
                frontmatter_lines.append(line)
                frontmatter_end = i
                break
            elif in_frontmatter:
                frontmatter_lines.append(line)

        if frontmatter_end == -1:
            errors.append("frontmatter未正确闭合（缺少结束---）")
        else:
            frontmatter_content = '\n'.join(frontmatter_lines)

            # 检查required字段
            if 'name:' not in frontmatter_content:
                errors.append("frontmatter缺少name字段")
            if 'description:' not in frontmatter_content:
                errors.append("frontmatter缺少description字段")

            # 检查name格式
            name_match = re.search(r'^name:\s*(.+)$', frontmatter_content, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    errors.append(f"name字段格式错误：'{name}'，应使用小写字母、数字和连字符")
                if len(name) > 64:
                    errors.append(f"name字段长度超过64字符限制")

            # 检查description触发短语
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter_content, re.MULTILINE)
            if desc_match:
                desc = desc_match.group(1).strip()
                if len(desc) < 20:
                    warnings.append("description字段过短，建议提供更详细的描述")
                if '当用户' not in desc and 'Use when' not in desc:
                    warnings.append("description建议包含触发条件说明（如'当用户...时使用'）")

    # 检查frontmatter后是否有markdown标题
    remaining = '\n'.join(lines[frontmatter_end+1:]).strip()
    if remaining and remaining.startswith('#'):
        warnings.append("frontmatter后不应有markdown标题，应直接是内容")

    return errors, warnings

def validate_meta_json(skill_path):
    """验证_meta.json"""
    errors = []

    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        errors.append("_meta.json文件不存在")
        return errors

    import json
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json缺少id字段")
        elif not isinstance(meta['id'], int):
            errors.append("_meta.json的id必须是整数")

        if 'version' not in meta:
            errors.append("_meta.json缺少version字段")
        elif not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
            errors.append("_meta.json的version格式错误，应为x.y.z格式")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON格式错误: {e}")
    except Exception as e:
        errors.append(f"读取_meta.json时出错: {e}")

    return errors

def validate_directory_structure(skill_path):
    """验证目录结构"""
    errors = []
    warnings = []

    # 检查必要的目录
    required_dirs = []
    optional_dirs = ['references', 'scripts', 'assets']

    for dir_name in required_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            warnings.append(f"建议目录{_dir_name}不存在")

    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists():
            # 检查目录是否为空
            if not any(dir_path.iterdir()):
                warnings.append(f"{dir_name}目录为空")

    return errors, warnings

def validate_path_names(skill_path):
    """验证路径和文件名只有英文"""
    errors = []

    # 遍历所有文件和目录
    for item in skill_path.rglob('*'):
        name = item.name
        # 检查是否包含非ASCII字符
        if not name.isascii():
            errors.append(f"路径包含非ASCII字符: {item.relative_to(skill_path)}")

    return errors

def main():
    if len(sys.argv) < 2:
        # 默认检查当前目录下的skill
        skill_path = Path.cwd()
    else:
        skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print_error(f"路径不存在: {skill_path}")
        sys.exit(1)

    print(f"\n{BOLD}{'='*50}")
    print(f"技能验证报告: {skill_path.name}")
    print(f"{'='*50}{RESET}\n")

    all_errors = []
    all_warnings = []

    # 1. 验证frontmatter
    print_info("检查SKILL.md frontmatter...")
    errors, warnings = validate_frontmatter(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print_error(e)
    if warnings:
        for w in warnings:
            print_warning(w)
    if not errors and not warnings:
        print_success("frontmatter格式正确")

    # 2. 验证_meta.json
    print_info("\n检查_meta.json...")
    errors = validate_meta_json(skill_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print_error(e)
    else:
        print_success("_meta.json格式正确")

    # 3. 验证目录结构
    print_info("\n检查目录结构...")
    errors, warnings = validate_directory_structure(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print_error(e)
    if warnings:
        for w in warnings:
            print_warning(w)
    if not errors and not warnings:
        print_success("目录结构完整")

    # 4. 验证路径名称
    print_info("\n检查路径名称...")
    errors = validate_path_names(skill_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print_error(e)
    else:
        print_success("路径名称全部为英文")

    # 输出总结
    print(f"\n{BOLD}{'='*50}")
    print("验证总结")
    print(f"{'='*50}{RESET}\n")

    if all_errors:
        print_error(f"发现 {len(all_errors)} 个错误")
        sys.exit(1)
    elif all_warnings:
        print_warning(f"发现 {len(all_warnings)} 个警告（建议修复）")
        print_success("核心验证通过")
        sys.exit(0)
    else:
        print_success("所有验证通过！")
        sys.exit(0)

if __name__ == "__main__":
    main()
