#!/usr/bin/env python3
"""
市场情绪分析技能 - 快速验证脚本
验证 SKILL.md 和 _meta.json 的格式和内容
"""

import os
import re
import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EXIT_CODE = 0

def validate_frontmatter():
    """验证 SKILL.md frontmatter"""
    global EXIT_CODE

    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        print("❌ SKILL.md 不存在")
        EXIT_CODE = 1
        return False

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        print("❌ SKILL.md 必须以 frontmatter --- 开头")
        EXIT_CODE = 1
        return False

    # 提取 frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        print("❌ frontmatter 未正确关闭")
        EXIT_CODE = 1
        return False

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # 验证必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf"^{field}:", frontmatter_text, re.MULTILINE):
            print(f"❌ frontmatter 缺少必需字段: {field}")
            EXIT_CODE = 1

    # 检查 name 格式
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            print(f"❌ name 格式错误: {name} (应使用小写字母、数字、连字符)")
            EXIT_CODE = 1
        if name != SKILL_DIR.name:
            print(f"❌ name ({name}) 与目录名 ({SKILL_DIR.name}) 不匹配")
            EXIT_CODE = 1

    print("✅ SKILL.md frontmatter 验证通过")
    return True

def validate_meta():
    """验证 _meta.json"""
    global EXIT_CODE

    meta_json = SKILL_DIR / "_meta.json"
    if not meta_json.exists():
        print("❌ _meta.json 不存在")
        EXIT_CODE = 1
        return False

    try:
        meta = json.loads(meta_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ _meta.json JSON 解析错误: {e}")
        EXIT_CODE = 1
        return False

    required_fields = ["id", "version", "name"]
    for field in required_fields:
        if field not in meta:
            print(f"❌ _meta.json 缺少必需字段: {field}")
            EXIT_CODE = 1

    # 验证 id 是整数
    if "id" in meta and not isinstance(meta["id"], int):
        print(f"❌ id 必须是整数，当前: {meta['id']}")
        EXIT_CODE = 1

    # 验证 version 格式
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            print(f"❌ version 格式错误: {version} (应为 x.y.z)")
            EXIT_CODE = 1

    print("✅ _meta.json 验证通过")
    return True

def validate_structure():
    """验证目录结构"""
    global EXIT_CODE

    required_dirs = ["scripts", "references", "assets"]
    for dir_name in required_dirs:
        dir_path = SKILL_DIR / dir_name
        if not dir_path.exists():
            print(f"⚠️  目录 {dir_name} 不存在（可选）")

    print("✅ 目录结构验证通过")
    return True

def validate_naming():
    """验证路径和命名仅使用英文"""
    global EXIT_CODE

    # 检查目录名
    dir_name = SKILL_DIR.name
    if not re.match(r"^[a-z0-9-]+$", dir_name):
        print(f"❌ 目录名包含非英文字符: {dir_name}")
        EXIT_CODE = 1

    # 检查文件
    for file_path in SKILL_DIR.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(SKILL_DIR)
            if not re.match(r"^[a-zA-Z0-9/_.-]+$", str(relative_path)):
                print(f"❌ 文件路径包含非英文字符: {relative_path}")
                EXIT_CODE = 1

    print("✅ 命名验证通过")
    return True

def main():
    print(f"🔍 验证技能: {SKILL_DIR.name}")
    print("=" * 50)

    validate_frontmatter()
    validate_meta()
    validate_structure()
    validate_naming()

    print("=" * 50)
    if EXIT_CODE == 0:
        print("✅ 所有验证通过！")
    else:
        print("❌ 存在验证错误，请修复后重试")

    return EXIT_CODE

if __name__ == "__main__":
    exit(main())
