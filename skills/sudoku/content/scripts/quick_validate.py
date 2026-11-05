#!/usr/bin/env python3
"""
Sudoku Skill Validator
验证数独技能的结构和 frontmatter 格式
"""

import os
import re
import sys

def validate_skill(path: str) -> bool:
    """验证技能目录结构和文件内容"""
    errors = []
    warnings = []

    # 检查目录存在
    if not os.path.exists(path):
        errors.append(f"Skill directory not found: {path}")
        return False

    # 检查 SKILL.md 存在
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return False

    # 读取 SKILL.md 内容
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查 frontmatter 格式
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
    else:
        frontmatter = frontmatter_match.group(1)

        # 检查必填字段
        if "name:" not in frontmatter:
            errors.append("Frontmatter missing 'name' field")
        if "description:" not in frontmatter:
            errors.append("Frontmatter missing 'description' field")

    # 检查 _meta.json
    meta_path = os.path.join(path, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("_meta.json not found")
    else:
        import json
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # 检查命名（name 应与文件夹名匹配）
    skill_name = os.path.basename(path)
    if "name:" in frontmatter:
        name_match = re.search(r'name:\s*(\S+)', frontmatter)
        if name_match:
            frontmatter_name = name_match.group(1)
            if frontmatter_name != skill_name:
                errors.append(f"Frontmatter name '{frontmatter_name}' does not match directory name '{skill_name}'")

    # 检查描述包含触发短语
    if "description:" in frontmatter:
        desc_match = re.search(r'description:\s*(.+)', frontmatter)
        if desc_match:
            desc = desc_match.group(1)
            # 检查是否包含触发短语
            trigger_phrases = ["解答", "答案", "解题", "上传"]
            has_trigger = any(phrase in desc for phrase in trigger_phrases)
            if not has_trigger:
                warnings.append("Description should include trigger phrases like '解答', '答案', '解题'")

    # 报告结果
    print(f"\n{'='*60}")
    print(f"Validating skill: {skill_name}")
    print(f"{'='*60}")

    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("\n❌ Validation FAILED")
        return False
    else:
        print("\n✅ Validation PASSED")
        if warnings:
            print("   (with warnings)")
        return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/sudoku"
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)