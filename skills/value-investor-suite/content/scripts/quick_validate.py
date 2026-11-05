#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和frontmatter规范
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能结构和规范"""
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # 1. 检查 SKILL.md 是否存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return False, errors

    # 2. 读取并检查 frontmatter
    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 frontmatter 开头
    if not content.startswith("---"):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")
    else:
        # 提取 frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            errors.append("无法解析 frontmatter 格式")
        else:
            frontmatter_text = match.group(1)

            # 检查必需字段
            if not re.search(r'^name:', frontmatter_text, re.MULTILINE):
                errors.append("frontmatter 缺少 'name' 字段")

            if not re.search(r'^description:', frontmatter_text, re.MULTILINE):
                errors.append("frontmatter 缺少 'description' 字段")

            # 检查 description 是否包含触发短语
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
            if desc_match:
                desc = desc_match.group(1)
                if "当用户" not in desc and "触发" not in desc.lower():
                    warnings.append("description 建议包含触发条件说明")

    # 3. 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json 文件不存在")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))

            # 检查必需字段
            if "id" not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 'version' 字段")

            # 检查 version 格式
            if "version" in meta:
                version = meta["version"]
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    errors.append(f"version '{version}' 格式不正确，应为 x.y.z")

        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 解析错误: {e}")

    # 4. 检查目录结构
    if not (skill_path / "scripts").exists():
        warnings.append("建议包含 scripts/ 目录")

    if not (skill_path / "references").exists():
        warnings.append("建议包含 references/ 目录（用于详细文档）")

    # 5. 检查技能名称与文件夹名称一致性
    if "name" in locals() or "name" in globals():
        folder_name = skill_path.name
        if name != folder_name:
            errors.append(f"frontmatter name '{name}' 与文件夹名称 '{folder_name}' 不一致")

    return len(errors) == 0, errors + warnings

def main():
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    print(f"正在验证技能: {skill_path}")
    print("-" * 50)

    is_valid, messages = validate_skill(skill_path)

    for msg in messages:
        prefix = "✓" if is_valid else "✗"
        print(f"  {prefix} {msg}")

    print("-" * 50)
    if is_valid:
        print("验证通过！")
        sys.exit(0)
    else:
        print("验证失败，请修复上述问题。")
        sys.exit(1)

if __name__ == "__main__":
    main()
