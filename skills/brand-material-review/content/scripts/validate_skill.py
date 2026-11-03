#!/usr/bin/env python3
"""
品牌物料审核技能 - 验证脚本
验证 SKILL.md 结构、frontmatter 和资源完整性
"""

import os
import re
import json
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 frontmatter 格式和必填字段"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding='utf-8')

    # 检查第一行是否是 ---
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        errors.append("SKILL.md 必须以 --- 开头（frontmatter 分隔符）")
        return False, errors

    # 找到第二个 --- 的位置
    try:
        second_dash = lines.index('---', 1)
    except ValueError:
        errors.append("frontmatter 缺少结束的分隔符 ---")
        return False, errors

    # 提取 frontmatter (转换为字符串)
    frontmatter_lines = lines[1:second_dash]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*.+', frontmatter_text, re.MULTILINE):
            errors.append(f"frontmatter 缺少必填字段: {field}")

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"name 字段必须使用小写字母、数字和连字符: {name_value}")
        if name_value != skill_md.parent.name:
            errors.append(f"name ({name_value}) 必须与文件夹名称 ({skill_md.parent.name}) 一致")

    # 检查 description 包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append("description 至少需要20个字符")
        if not any(keyword in desc_value for keyword in ['审核', '品牌', '物料', 'VIS', '识别', '评审', '检查']):
            errors.append("description 应包含触发关键词（审核、品牌、物料、VIS等）")

    return len(errors) == 0, errors

def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json 格式错误: {e}"]

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必填字段: {field}")

    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append(f"version 字段格式错误，应为语义化版本（如 1.0.0）: {meta['version']}")

    return len(errors) == 0, errors

def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    skill_dir = Path(skill_path)

    # 检查必要文件
    if not (skill_dir / "SKILL.md").exists():
        errors.append("缺少 SKILL.md")
    if not (skill_dir / "_meta.json").exists():
        errors.append("缺少 _meta.json")

    # 建议的目录
    recommended_dirs = ['references', 'assets', 'scripts']
    for dir_name in recommended_dirs:
        dir_path = skill_dir / dir_name
        if dir_path.exists() and not any(dir_path.iterdir()):
            errors.append(f"{dir_name}/ 目录存在但为空")

    return len(errors) == 0, errors

def main():
    skill_path = "/workspace/temp-skills/brand-material-review"

    print("=" * 50)
    print("品牌物料审核技能 - 验证报告")
    print("=" * 50)

    all_passed = True

    # 1. 验证 frontmatter
    print("\n[1] 验证 frontmatter 格式...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("    ✓ frontmatter 格式正确")
    else:
        all_passed = False
        for err in errors:
            print(f"    ✗ {err}")

    # 2. 验证 _meta.json
    print("\n[2] 验证 _meta.json...")
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("    ✓ _meta.json 格式正确")
    else:
        all_passed = False
        for err in errors:
            print(f"    ✗ {err}")

    # 3. 验证目录结构
    print("\n[3] 验证目录结构...")
    passed, errors = validate_structure(skill_path)
    if passed:
        print("    ✓ 目录结构完整")
    else:
        all_passed = False
        for err in errors:
            print(f"    ✗ {err}")

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证错误，请修复后重试")
        return 1

if __name__ == "__main__":
    exit(main())
