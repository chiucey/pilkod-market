#!/usr/bin/env python3
"""
食品标签审核技能验证脚本
验证 SKILL.md 结构、frontmatter 格式和内容完整性
"""

import os
import re
import sys
from pathlib import Path

# 定义颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def log_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def validate_frontmatter(skill_path):
    """验证 frontmatter 格式和必填字段"""
    errors = []

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否为 ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        errors.append("Frontmatter 必须以 --- 开始，且为文件第一行")

    # 查找 frontmatter 结束标记
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        errors.append("Frontmatter 缺少结束 --- 标记")
        return errors

    # 提取 frontmatter 内容
    frontmatter_text = '\n'.join(lines[1:end_idx])

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*.+', frontmatter_text, re.MULTILINE):
            errors.append(f"缺少必填字段: {field}")

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 格式错误: '{name}' - 应使用小写字母、数字和连字符")
        if len(name) > 64:
            errors.append(f"name 长度超过64字符限制: {len(name)}")

    # 检查 description 是否包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        trigger_keywords = ['审核', '检查', '合规', '标签']
        if not any(keyword in desc for keyword in trigger_keywords):
            errors.append("description 应包含触发关键词（如：审核、检查、合规）")

    return errors

def validate_structure(skill_dir):
    """验证技能目录结构"""
    errors = []

    # 检查必填文件
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = skill_dir / filename
        if not filepath.exists():
            errors.append(f"缺少必填文件: {filename}")

    # 检查 _meta.json 格式
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        import json
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    return errors

def validate_content(skill_path):
    """验证 SKILL.md 内容完整性"""
    errors = []

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否包含 GB 7718 相关内容
    if 'GB 7718' not in content:
        errors.append("SKILL.md 应包含 GB 7718 相关内容")

    # 检查是否包含 GB 28050 相关内容
    if 'GB 28050' not in content:
        errors.append("SKILL.md 应包含 GB 28050 相关内容")

    # 检查是否有审核流程
    if not re.search(r'审核流程|检查清单|审核清单', content):
        errors.append("SKILL.md 应包含审核流程或检查清单")

    # 检查是否有输出格式
    if not re.search(r'报告|输出|格式', content):
        errors.append("SKILL.md 应包含输出格式说明")

    return errors

def main():
    skill_dir = Path(__file__).parent.parent
    skill_name = skill_dir.name

    print(f"\n{'='*60}")
    log_info(f"验证食品标签审核技能: {skill_name}")
    print(f"{'='*60}\n")

    all_passed = True

    # 1. Frontmatter 验证
    log_info("检查 1: Frontmatter 和必填字段")
    skill_path = skill_dir / 'SKILL.md'
    if skill_path.exists():
        errors = validate_frontmatter(skill_path)
        if errors:
            for err in errors:
                log_error(err)
            all_passed = False
        else:
            log_success("Frontmatter 格式正确")
    else:
        log_error(f"SKILL.md 不存在: {skill_path}")
        all_passed = False

    # 2. 目录结构验证
    log_info("\n检查 2: 目录结构")
    errors = validate_structure(skill_dir)
    if errors:
        for err in errors:
            log_error(err)
        all_passed = False
    else:
        log_success("目录结构完整")

    # 3. 内容完整性验证
    log_info("\n检查 3: 内容完整性")
    if skill_path.exists():
        errors = validate_content(skill_path)
        if errors:
            for err in errors:
                log_error(err)
            all_passed = False
        else:
            log_success("内容完整性验证通过")

    # 4. 命名规范检查
    log_info("\n检查 4: 命名规范")
    if not re.match(r'^[a-z][a-z0-9-]*$', skill_name):
        log_error(f"技能名称不符合规范: {skill_name}")
        all_passed = False
    else:
        log_success(f"技能名称规范: {skill_name}")

    print(f"\n{'='*60}")
    if all_passed:
        log_success("所有验证通过！")
        return 0
    else:
        log_error("存在验证失败项，需要修复后重新验证")
        return 1

if __name__ == '__main__':
    sys.exit(main())