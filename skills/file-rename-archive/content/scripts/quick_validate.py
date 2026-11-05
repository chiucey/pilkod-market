"""
快速验证 file-rename-archive 技能的 SKILL.md frontmatter 和目录结构。
用法：uv run scripts/quick_validate.py
"""

import json
import os
import re
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_skill_md():
    skill_md = os.path.join(SKILL_ROOT, "SKILL.md")
    assert os.path.isfile(skill_md), "SKILL.md 不存在"

    with open(skill_md, encoding="utf-8") as f:
        content = f.read()

    # frontmatter 必须在第一行
    assert content.startswith("---"), "SKILL.md 必须以 --- 开头（frontmatter 在首行）"

    # 提取 frontmatter
    end = content.index("---", 3)
    frontmatter = content[3:end]

    assert "name:" in frontmatter, "frontmatter 缺少 name 字段"
    assert "description:" in frontmatter, "frontmatter 缺少 description 字段"

    # name 应为 hyphen-case
    name_match = re.search(r'name:\s*(\S+)', frontmatter)
    assert name_match, "无法解析 name 字段"
    name_val = name_match.group(1)
    assert re.match(r'^[a-z][a-z0-9-]*$', name_val), f"name 应为英文 hyphen-case：{name_val}"
    assert name_val == "file-rename-archive", f"name 与预期不符：{name_val}"

    print("✅ SKILL.md frontmatter 验证通过")


def check_meta_json():
    meta_path = os.path.join(SKILL_ROOT, "_meta.json")
    assert os.path.isfile(meta_path), "_meta.json 不存在"

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    assert "id" in meta, "_meta.json 缺少 id 字段"
    assert "version" in meta, "_meta.json 缺少 version 字段"
    assert re.match(r'^\d+\.\d+\.\d+$', meta["version"]), f"version 不符合语义化版本：{meta['version']}"

    print("✅ _meta.json 验证通过")


def check_references():
    naming_rules = os.path.join(SKILL_ROOT, "references", "naming-rules.md")
    assert os.path.isfile(naming_rules), "references/naming-rules.md 不存在"
    print("✅ references/naming-rules.md 存在")


def check_scripts():
    script = os.path.join(SKILL_ROOT, "scripts", "rename_archive.py")
    assert os.path.isfile(script), "scripts/rename_archive.py 不存在"
    print("✅ scripts/rename_archive.py 存在")


def main():
    errors = []
    for check in [check_skill_md, check_meta_json, check_references, check_scripts]:
        try:
            check()
        except AssertionError as e:
            errors.append(str(e))
            print(f"❌ {e}")

    if errors:
        print(f"\n验证失败，共 {len(errors)} 项错误。")
        sys.exit(1)
    else:
        print("\n🎉 所有验证项通过！")


if __name__ == "__main__":
    main()
