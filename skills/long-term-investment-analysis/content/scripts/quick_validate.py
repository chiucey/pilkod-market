#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能的基本结构和格式
"""
import os
import sys
import json
from pathlib import Path

def validate_frontmatter(skill_dir: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter 格式"""
    errors = []
    skill_md = Path(skill_dir) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter --- 开头，不能以 # 标题开头")
        return False, errors

    # 解析 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == '---':
            continue
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("frontmatter 未正确关闭（缺少结束的 ---）")
        return False, errors

    # 解析 YAML
    frontmatter_text = '\n'.join(lines[1:frontmatter_end])
    frontmatter = {}
    current_key = None
    current_value_lines = []

    for line in lines[1:frontmatter_end]:
        if ':' in line:
            if current_key:
                value = '\n'.join(current_value_lines).strip()
                if value:
                    frontmatter[current_key] = value
            parts = line.split(':', 1)
            current_key = parts[0].strip()
            current_value_lines = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
        elif line.startswith(' '):
            current_value_lines.append(line)

    if current_key:
        value = '\n'.join(current_value_lines).strip()
        if value:
            frontmatter[current_key] = value

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"frontmatter 缺少必需字段: {field}")

    # 检查 name 格式
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not name.replace('-', '').replace('_', '').isalnum():
            errors.append(f"name 必须为连字符格式（小写字母和连字符）: {name}")
        if name != Path(skill_dir).name:
            errors.append(f"name '{name}' 与文件夹名称 '{Path(skill_dir).name}' 不匹配")

    return len(errors) == 0, errors


def validate_meta(skill_dir: str) -> tuple[bool, list[str]]:
    """验证 _meta.json 的格式"""
    errors = []
    meta_path = Path(skill_dir) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON 解析错误: {e}"]

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必需字段: {field}")

    # 检查 version 格式（语义化版本）
    if 'version' in meta:
        version = meta['version']
        parts = version.split('.')
        if len(parts) != 3:
            errors.append(f"version 必须为语义化版本格式 (x.y.z): {version}")

    return len(errors) == 0, errors


def validate_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    skill_path = Path(skill_dir)

    # 检查顶层文件
    if not (skill_path / "SKILL.md").exists():
        errors.append("缺少 SKILL.md")

    if not (skill_path / "_meta.json").exists():
        errors.append("缺少 _meta.json")

    return len(errors) == 0, errors


def run_validation(skill_dir: str) -> bool:
    """运行所有验证"""
    print(f"🔍 验证技能: {skill_dir}")
    print("=" * 50)

    all_passed = True

    # 结构验证
    print("\n📁 检查目录结构...")
    passed, errors = validate_structure(skill_dir)
    if passed:
        print("  ✅ 目录结构正确")
    else:
        print("  ❌ 目录结构错误:")
        for e in errors:
            print(f"     - {e}")
        all_passed = False

    # Frontmatter 验证
    print("\n📝 检查 frontmatter 格式...")
    passed, errors = validate_frontmatter(skill_dir)
    if passed:
        print("  ✅ frontmatter 格式正确")
    else:
        print("  ❌ frontmatter 格式错误:")
        for e in errors:
            print(f"     - {e}")
        all_passed = False

    # Meta 验证
    print("\n📋 检查 _meta.json...")
    passed, errors = validate_meta(skill_dir)
    if passed:
        print("  ✅ _meta.json 格式正确")
    else:
        print("  ❌ _meta.json 格式错误:")
        for e in errors:
            print(f"     - {e}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有验证通过！")
    else:
        print("❌ 验证失败，请修复上述问题")

    return all_passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 默认验证当前目录下的 temp-skills 目录
        skill_dir = "/workspace/temp-skills/long-term-investment-analysis"
    else:
        skill_dir = sys.argv[1]

    success = run_validation(skill_dir)
    sys.exit(0 if success else 1)