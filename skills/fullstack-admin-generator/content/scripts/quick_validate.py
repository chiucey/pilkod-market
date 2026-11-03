#!/usr/bin/env python3
"""技能验证脚本 - 检查 SKILL.md 结构和 frontmatter"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能目录结构"""
    errors = []
    warnings = []

    # 检查 SKILL.md 是否存在
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return False

    # 读取 SKILL.md 内容
    content = skill_md.read_text(encoding="utf-8")

    # 检查 frontmatter
    if not content.startswith("---"):
        errors.append("Frontmatter 必须从第一行开始（以 --- 开头）")

    # 解析 frontmatter
    if "---" in content:
        frontmatter_end = content.index("---", 2) if content.count("---") >= 2 else -1
        if frontmatter_end > 0:
            frontmatter = content[3:frontmatter_end].strip()

            # 检查必需字段
            if not re.search(r"^name:\s*.+$", frontmatter, re.MULTILINE):
                errors.append("缺少 'name' 字段")

            if not re.search(r"^description:\s*.+$", frontmatter, re.MULTILINE):
                errors.append("缺少 'description' 字段")

    # 检查标题是否在 frontmatter 之后
    lines = content.split("\n")
    frontmatter_ended = False
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not frontmatter_ended:
                frontmatter_ended = True
                continue
        if frontmatter_ended and line.strip().startswith("#"):
            # 找到第一个标题，说明结构正确
            break
        if i > 0 and line.strip().startswith("#") and not frontmatter_ended:
            errors.append(f"标题 '#' 不能在 frontmatter 之前（第 {i+1} 行）")
            break

    # 检查 _meta.json
    meta_json = Path(skill_path) / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json 文件不存在")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 输出结果
    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"   - {err}")
        return False

    if warnings:
        print("⚠️ 警告:")
        for w in warnings:
            print(f"   - {w}")

    print("✅ 验证通过")
    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
