#!/usr/bin/env python3
"""
面试题生成器Skill验证脚本
检查SKILL.md的frontmatter格式和基本结构
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_dir: Path) -> bool:
    """验证SKILL.md的frontmatter格式"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ 错误：{skill_md} 不存在")
        return False

    content = skill_md.read_text(encoding="utf-8")

    # 检查frontmatter是否在第一行
    if not content.startswith("---"):
        print("❌ 错误：SKILL.md必须以---开头（frontmatter必须在第一行）")
        return False

    # 提取frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        print("❌ 错误：frontmatter未正确闭合")
        return False

    frontmatter = "\n".join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf"^{field}:\s*\S+", frontmatter, re.MULTILINE):
            print(f"❌ 错误：frontmatter缺少必需字段 '{field}'")
            return False

    # 检查name格式
    name_match = re.search(r"name:\s*(.+)", frontmatter)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            print(f"❌ 错误：name必须使用小写字母、数字和连字符（当前：{name}）")
            return False
        if name != skill_dir.name:
            print(f"⚠️ 警告：name '{name}' 与目录名 '{skill_dir.name}' 不一致")

    # 检查description触发词
    desc_match = re.search(r"description:\s*(.+)", frontmatter)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            print(f"⚠️ 警告：description过短（建议至少20字符）")
        if "当用户" not in desc and "When" not in desc:
            print(f"⚠️ 警告：description建议包含触发条件（'当用户...' 或 'When...'）")

    print("✅ frontmatter格式验证通过")
    return True


def validate_meta_json(skill_dir: Path) -> bool:
    """验证_meta.json"""
    import json

    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        print(f"❌ 错误：{meta_file} 不存在")
        return False

    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 错误：_meta.json格式错误 - {e}")
        return False

    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            print(f"❌ 错误：_meta.json缺少字段 '{field}'")
            return False

    if not isinstance(meta["id"], int) or meta["id"] <= 0:
        print(f"❌ 错误：_meta.json的id必须是正整数")
        return False

    if not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
        print(f"⚠️ 警告：version应符合语义化版本格式（如1.0.0）")

    print("✅ _meta.json验证通过")
    return True


def validate_structure(skill_dir: Path) -> bool:
    """验证目录结构"""
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        if not (skill_dir / filename).exists():
            print(f"❌ 错误：缺少必需文件 {filename}")
            return False

    print("✅ 目录结构验证通过")
    return True


def validate_scripts(skill_dir: Path) -> bool:
    """验证脚本文件（如存在）"""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return True  # scripts可选

    py_files = list(scripts_dir.glob("*.py"))
    for py_file in py_files:
        # 检查语法
        import py_compile
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            print(f"❌ 错误：{py_file.name} 语法错误 - {e}")
            return False

    print(f"✅ 脚本验证通过（{len(py_files)}个Python文件）")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="验证Skill结构")
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill目录路径")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()

    print(f"\n{'='*50}")
    print(f"验证 Skill: {skill_dir.name}")
    print(f"{'='*50}\n")

    checks = [
        ("结构检查", lambda: validate_structure(skill_dir)),
        ("Frontmatter检查", lambda: validate_frontmatter(skill_dir)),
        ("Meta JSON检查", lambda: validate_meta_json(skill_dir)),
        ("脚本检查", lambda: validate_scripts(skill_dir)),
    ]

    results = []
    for name, check in checks:
        print(f"\n[{name}]")
        results.append(check())

    print(f"\n{'='*50}")
    if all(results):
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 部分验证失败，请修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
