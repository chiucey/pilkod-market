#!/usr/bin/env python3
"""
医疗器械注册专家技能验证脚本
验证SKILL.md的frontmatter和结构完整性
"""

import re
import sys
from pathlib import Path


def validate_skill(path: str) -> tuple[bool, list[str]]:
    """验证技能文件的完整性和格式正确性"""
    errors = []
    skill_path = Path(path)

    # 检查SKILL.md存在
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        errors.append("❌ SKILL.md文件不存在")
        return False, errors

    content = skill_file.read_text(encoding="utf-8")

    # 检查frontmatter
    if not content.startswith("---"):
        errors.append("❌ SKILL.md必须以frontmatter(---)开头")

    # 解析frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("❌ frontmatter格式不正确")
    else:
        frontmatter = frontmatter_match.group(1)

        # 检查必填字段
        if not re.search(r"^name:", frontmatter, re.MULTILINE):
            errors.append("❌ frontmatter缺少name字段")
        elif not re.search(r"name: medical-device-registration-expert", frontmatter):
            errors.append("❌ name字段值不正确，应为: medical-device-registration-expert")

        if not re.search(r"^description:", frontmatter, re.MULTILINE):
            errors.append("❌ frontmatter缺少description字段")

    # 检查_meta.json
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        errors.append("❌ _meta.json文件不存在")
    else:
        import json
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("❌ _meta.json缺少id字段")
            if "version" not in meta:
                errors.append("❌ _meta.json缺少version字段")
        except json.JSONDecodeError as e:
            errors.append(f"❌ _meta.json格式错误: {e}")

    # 检查目录结构
    expected_dirs = ["references"]
    for d in expected_dirs:
        if not (skill_path / d).exists():
            errors.append(f"⚠️ 缺少{d}目录（建议添加）")

    return len(errors) == 0, errors


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success, errors = validate_skill(skill_path)

    print("=" * 50)
    print("医疗器械注册专家技能 - 验证报告")
    print("=" * 50)

    if errors:
        print("\n发现问题:")
        for err in errors:
            print(f"  {err}")
    else:
        print("\n✅ 所有检查通过！")

    print("=" * 50)
    sys.exit(0 if success else 1)