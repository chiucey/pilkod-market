#!/usr/bin/env python3
"""
项目管理技能验证脚本
验证 SKILL.md 结构、frontmatter 格式和内容完整性
"""

import os
import re
import sys
from pathlib import Path


def validate_skill(root_path: Path) -> tuple[bool, list[str]]:
    """验证技能结构和内容"""
    errors = []

    # 检查 SKILL.md 存在
    skill_md = root_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # 读取文件内容
    content = skill_md.read_text(encoding="utf-8")

    # 检查 frontmatter 格式
    if not content.startswith("---"):
        errors.append("SKILL.md must start with --- (frontmatter)")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Frontmatter not properly formatted")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    if not re.search(r'^name:\s*.+', frontmatter, re.MULTILINE):
        errors.append("Missing 'name' field in frontmatter")

    if not re.search(r'^description:\s*.+', frontmatter, re.MULTILINE):
        errors.append("Missing 'description' field in frontmatter")

    # 检查 description 是否包含触发关键词
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1)
        required_keywords = ["项目管理", "项目计划", "任务管理", "进度跟踪"]
        missing = [kw for kw in required_keywords if kw not in desc]
        if missing:
            errors.append(f"Missing keywords in description: {missing}")

    # 检查 _meta.json
    meta_json = root_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("Missing 'id' in _meta.json")
            if "version" not in meta:
                errors.append("Missing 'version' in _meta.json")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid _meta.json: {e}")

    # 检查内容完整性
    if "#" not in content:
        errors.append("SKILL.md should contain markdown headers")

    # 检查关键章节
    required_sections = ["启动", "规划", "执行", "监控", "收尾"]
    missing_sections = [s for s in required_sections if s not in content]
    if missing_sections:
        errors.append(f"Missing required sections: {missing_sections}")

    return len(errors) == 0, errors


if __name__ == "__main__":
    skill_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/project-management")
    success, errors = validate_skill(skill_path)

    if success:
        print("✓ Validation passed")
        sys.exit(0)
    else:
        print("✗ Validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)