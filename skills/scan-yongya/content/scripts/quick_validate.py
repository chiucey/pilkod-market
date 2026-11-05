#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构是否符合规范
"""
import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能目录结构和文件"""
    skill_dir = Path(skill_path)
    errors = []
    warnings = []

    # 1. 检查目录结构
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_dir / f).exists():
            errors.append(f"缺少必需文件: {f}")

    # 2. 检查 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 检查是否以 --- 开头
        if not content.strip().startswith("---"):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头（第一行为 '---'）")

        # 检查 frontmatter 必填字段
        if not re.search(r'^name:\s*\S', content, re.MULTILINE):
            errors.append("SKILL.md 缺少 'name' 字段")

        if not re.search(r'^description:\s*>', content, re.MULTILINE) and \
           not re.search(r'^description:\s*\n', content, re.MULTILINE):
            warnings.append("SKILL.md 缺少 'description' 字段或格式不正确")

        # 检查 name 与目录名是否一致
        folder_name = skill_dir.name
        name_match = re.search(r'^name:\s*([^\n]+)', content, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()
            # 允许名称格式变换（如下划线vs连字符）
            normalized_folder = folder_name.replace("_", "-")
            normalized_name = skill_name.replace("_", "-")
            if normalized_folder != normalized_name:
                warnings.append(f"目录名 '{folder_name}' 与 SKILL.md name '{skill_name}' 不一致")

    # 3. 检查 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 格式错误: {e}")

    # 4. 检查 scripts 目录
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        js_files = list(scripts_dir.glob("*.js"))
        if not py_files and not js_files:
            warnings.append("scripts 目录存在但无任何脚本文件")

    # 5. 输出结果
    print("=" * 60)
    print(f"技能验证: {skill_dir.name}")
    print("=" * 60)

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✅ 验证通过！")
        return True
    elif not errors:
        print("\n✅ 基础验证通过（有警告但不影响使用）")
        return True
    else:
        print("\n❌ 验证失败，请修复上述错误")
        return False

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
