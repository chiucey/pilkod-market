#!/usr/bin/env python3
"""
技能验证脚本 - 检查 SKILL.md 格式和结构
"""

import re
import sys
from pathlib import Path


def validate_skill(skill_path: str) -> tuple[bool, list]:
    """验证技能文件"""
    errors = []
    skill_path = Path(skill_path)

    # 1. 检查目录存在
    if not skill_path.exists():
        return False, [f"技能目录不存在: {skill_path}"]

    # 2. 检查 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 不存在")
        return False, errors

    # 3. 读取 SKILL.md 内容
    content = skill_md.read_text(encoding='utf-8')

    # 4. 检查 frontmatter
    frontmatter_pattern = r'^---\n(.*?)\n---'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("Frontmatter 格式错误：必须以 --- 开头和结尾")
    else:
        frontmatter = match.group(1)

        # 检查必需字段
        if not re.search(r'^name:\s*.+$', frontmatter, re.MULTILINE):
            errors.append("Frontmatter 缺少 'name' 字段")

        if not re.search(r'^description:\s*.+$', frontmatter, re.MULTILINE):
            errors.append("Frontmatter 缺少 'description' 字段")

    # 5. 检查文件结构
    if not (skill_path / "_meta.json").exists():
        errors.append("_meta.json 不存在")

    # 6. 检查 frontmatter 后是否有 markdown 标题
    lines_after_frontmatter = content.split('---', 2)[-1].strip()
    if lines_after_frontmatter.startswith('#'):
        errors.append("Frontmatter 后不应直接以 # 标题开头")

    # 7. 检查名称格式
    meta_json = skill_path / "_meta.json"
    if meta_json.exists():
        import json
        meta = json.loads(meta_json.read_text(encoding='utf-8'))
        if 'id' not in meta:
            errors.append("_meta.json 缺少 'id' 字段")
        if 'version' not in meta:
            errors.append("_meta.json 缺少 'version' 字段")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    valid, errors = validate_skill(skill_path)

    if valid:
        print("✅ 验证通过")
        return 0
    else:
        print("❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
