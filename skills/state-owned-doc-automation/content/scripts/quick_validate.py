"""快速验证脚本：检查技能结构和 frontmatter"""

import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_frontmatter():
    """验证 SKILL.md frontmatter 格式"""
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Frontmatter 必须在第一行
    if not content.startswith("---"):
        return False, "SKILL.md 必须以 --- 开头（frontmatter）"

    # 检查必需字段
    if 'name:' not in content[:500]:
        return False, "缺少 name 字段"

    if 'description:' not in content[:500]:
        return False, "缺少 description 字段"

    # 检查是否有 markdown 标题在 frontmatter 之前
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "frontmatter 未正确闭合"

    # frontmatter 之后可以有 markdown 标题，这是正确的格式
    # 不需要此检查

    return True, "OK"


def check_meta_json():
    """验证 _meta.json 格式"""
    meta_path = os.path.join(SKILL_DIR, "_meta.json")
    if not os.path.exists(meta_path):
        return False, "_meta.json 不存在"

    with open(meta_path, "r", encoding="utf-8") as f:
        content = f.read()

    if '"id"' not in content:
        return False, "_meta.json 缺少 id 字段"

    if '"version"' not in content:
        return False, "_meta.json 缺少 version 字段"

    return True, "OK"


def check_naming():
    """验证文件夹和 SKILL.md name 一致"""
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
    if not match:
        return False, "无法从 SKILL.md 提取 name"

    skill_name = match.group(1).strip()
    folder_name = os.path.basename(SKILL_DIR)

    if skill_name != folder_name:
        return False, f"SKILL.md name '{skill_name}' 与文件夹名 '{folder_name}' 不匹配"

    return True, f"OK (name={skill_name})"


def main():
    checks = [
        ("Frontmatter", check_frontmatter),
        ("_meta.json", check_meta_json),
        ("命名一致性", check_naming),
    ]

    all_passed = True
    for name, func in checks:
        passed, msg = func()
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}: {msg}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n所有检查通过！")
        return 0
    else:
        print("\n有检查未通过，请修复后重新运行。")
        return 1


if __name__ == "__main__":
    sys.exit(main())