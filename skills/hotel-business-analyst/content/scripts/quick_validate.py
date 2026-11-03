#!/usr/bin/env python3
"""
酒店商业分析技能验证脚本
检查 SKILL.md 和 _meta.json 的格式和内容
"""

import os
import json
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list]:
    """验证技能结构和内容"""
    errors = []
    skill_path = Path(skill_path)

    # 检查目录结构
    if not skill_path.exists():
        return False, [f"技能目录不存在: {skill_path}"]

    # 检查 SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("缺少 SKILL.md 文件")
    else:
        content = skill_md.read_text(encoding="utf-8")

        # 检查 frontmatter
        if not content.startswith("---"):
            errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")

        # 提取 frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm_content = fm_match.group(1)

            # 检查必需字段
            if "name:" not in fm_content:
                errors.append("Frontmatter 缺少 name 字段")
            if "description:" not in fm_content:
                errors.append("Frontmatter 缺少 description 字段")

            # 验证 name 格式
            name_match = re.search(r"name:\s*(.+)", fm_content)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r"^[a-z0-9-]+$", name):
                    errors.append(f"name 必须使用小写字母、数字和连字符: {name}")
                if name != skill_path.name:
                    errors.append(f"name ({name}) 必须与文件夹名称 ({skill_path.name}) 匹配")

            # 验证 description
            desc_match = re.search(r"description:\s*(.+)", fm_content)
            if desc_match:
                desc = desc_match.group(1).strip()
                if len(desc) < 20:
                    errors.append("description 太短，至少需要20个字符")
                if not desc.endswith("。"):
                    errors.append("description 应以句号结尾")
        else:
            errors.append("无法解析 YAML frontmatter")

        # 检查是否有 markdown 标题在 frontmatter 之前
        lines = content.split("\n")
        for i, line in enumerate(lines[:5]):
            if line.startswith("# ") and not line.startswith("##"):
                errors.append(f"Markdown 标题不应出现在 frontmatter 之前 (第{i+1}行)")
                break

    # 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))

            if "id" not in meta:
                errors.append("_meta.json 缺少 id 字段")
            elif not isinstance(meta["id"], int):
                errors.append("_meta.json 的 id 必须是整数")

            if "version" not in meta:
                errors.append("_meta.json 缺少 version 字段")
            elif not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
                errors.append("_meta.json 的 version 必须符合语义化版本格式 (如 1.0.0)")

        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 格式错误: {e}")

    # 检查 references 目录（可选但建议有）
    references_dir = skill_path / "references"
    if not references_dir.exists():
        print(f"  提示: 建议添加 references/ 目录存放参考文档")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"正在验证技能: {skill_path}")
    print("-" * 50)

    success, errors = validate_skill(skill_path)

    if success:
        print("✓ 验证通过！")
        return 0
    else:
        print("✗ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
