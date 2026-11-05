#!/usr/bin/env python3
"""
快速验证脚本 - 验证技能结构完整性
"""
import os
import sys
import json
import re
from pathlib import Path


def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能结构和内容"""
    errors = []
    skill_dir = Path(skill_path).resolve()

    # 1. 检查 SKILL.md 存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("❌ SKILL.md 不存在")
        return False, errors

    # 2. 检查 _meta.json 存在
    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        errors.append("❌ _meta.json 不存在")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("❌ _meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("❌ _meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json JSON 解析错误: {e}")

    # 3. 检查 SKILL.md frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter = ""
    name_match = None

    # 检查文件开头是否是 ---
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 YAML frontmatter (---) 开头")
    else:
        # 提取 frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append("❌ SKILL.md frontmatter 格式错误")
        else:
            frontmatter = parts[1]
            # 检查 name 字段
            if not re.search(r'^name:\s*\S', frontmatter, re.MULTILINE):
                errors.append("❌ frontmatter 缺少 'name' 字段")
            else:
                name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
            # 检查 description 字段
            if not re.search(r'^description:\s*\S', frontmatter, re.MULTILINE):
                errors.append("❌ frontmatter 缺少 'description' 字段")

    # 4. 检查目录名与 frontmatter name 是否匹配
    folder_name = skill_dir.name
    if name_match:
        frontmatter_name = name_match.group(1).strip().lower().replace('_', '-')
        if folder_name.lower() != frontmatter_name:
            errors.append(f"❌ 目录名 '{folder_name}' 与 frontmatter name '{frontmatter_name}' 不匹配")

    # 5. 检查代码文件存在
    skill_name = name_match.group(1).strip().replace('-', '_') if name_match else ""
    if skill_name:
        code_file = skill_dir / f"{skill_name}.py"
        if not code_file.exists():
            # 尝试其他可能的代码文件名
            possible_files = ['video_clipper.py', 'main.py', 'cli.py']
            found = False
            for pf in possible_files:
                if (skill_dir / pf).exists():
                    found = True
                    break
            if not found:
                errors.append(f"⚠️ 未找到主要代码文件")

    # 6. 检查 scripts 目录（如果存在）
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        if not (scripts_dir / "package_skill.py").exists():
            errors.append("⚠️ scripts 目录存在但缺少 package_skill.py")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # 解析为绝对路径
    skill_path = str(Path(skill_path).resolve())

    print("=" * 50)
    print("🔍 技能验证")
    print("=" * 50)
    print(f"\n验证路径: {skill_path}\n")

    passed, errors = validate_skill(skill_path)

    if passed:
        print("✅ 验证通过！")
        print("-" * 50)
        print("检查项:")
        print("  ✓ SKILL.md 存在且格式正确")
        print("  ✓ _meta.json 存在且有效")
        print("  ✓ frontmatter 包含 name 和 description")
        print("  ✓ 目录名与 frontmatter name 匹配")
        print("  ✓ 代码文件存在")
        sys.exit(0)
    else:
        print("❌ 验证失败！")
        print("-" * 50)
        print("错误列表:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
