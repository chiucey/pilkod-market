#!/usr/bin/env python3
"""
技能验证脚本 - 验证 SKILL.md 和目录结构
"""
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证 Frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 --- 开头（Frontmatter 必须放在第一行）"

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---' or lines[1].strip() == '':
        return False, "Frontmatter 格式错误：需要 --- 开始和结束"

    # 查找 frontmatter 结束
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "Frontmatter 缺少结束 ---"

    frontmatter_text = '\n'.join(lines[1:end_idx])

    # 检查必需字段
    if 'name:' not in frontmatter_text and 'name =' not in frontmatter_text:
        return False, "Frontmatter 缺少 name 字段"

    if 'description:' not in frontmatter_text and 'description =' not in frontmatter_text:
        return False, "Frontmatter 缺少 description 字段"

    return True, "Frontmatter 验证通过"

def validate_meta_json(skill_path):
    """验证 _meta.json"""
    meta_json = skill_path / "_meta.json"

    if not meta_json.exists():
        return False, "_meta.json 文件不存在"

    try:
        import json
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            return False, "_meta.json 缺少 id 字段"

        if 'version' not in meta:
            return False, "_meta.json 缺少 version 字段"

        return True, "_meta.json 验证通过"
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"
    except Exception as e:
        return False, f"_meta.json 读取错误: {e}"

def validate_naming(skill_path):
    """验证命名规范"""
    name = skill_path.name

    # 检查是否使用连字符格式
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, f"技能名称 '{name}' 应使用小写连字符格式（如 salary-fund-advisor）"

    if len(name) > 64:
        return False, f"技能名称长度不能超过64字符，当前: {len(name)}"

    return True, f"命名规范验证通过: {name}"

def validate_directory_structure(skill_path):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    missing_files = []

    for file in required_files:
        if not (skill_path / file).exists():
            missing_files.append(file)

    if missing_files:
        return False, f"缺少必需文件: {', '.join(missing_files)}"

    return True, "目录结构验证通过"

def main():
    """主验证函数"""
    if len(sys.argv) < 2:
        # 默认验证当前目录下的技能
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    print(f"正在验证技能: {skill_path}")
    print("-" * 50)

    validations = [
        ("目录结构", validate_directory_structure),
        ("命名规范", validate_naming),
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
    ]

    all_passed = True

    for name, validator in validations:
        try:
            passed, message = validator(skill_path)
            status = "✓" if passed else "✗"
            print(f"{status} {name}: {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"✗ {name}: 验证出错 - {e}")
            all_passed = False

    print("-" * 50)

    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
