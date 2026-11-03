#!/usr/bin/env python3
"""
快速验证谈判助手技能结构
"""

import os
import sys
from pathlib import Path

SKILL_DIR = Path("/workspace/temp-skills/negotiation-assistant")

def check_file_exists(path, name):
    if path.exists():
        print(f"✓ {name} 存在")
        return True
    else:
        print(f"✗ {name} 不存在")
        return False

def validate_skill():
    errors = []
    warnings = []

    print("=== 谈判助手技能验证 ===\n")

    # 检查必需文件
    print("1. 检查文件结构...")
    required_files = {
        "SKILL.md": SKILL_DIR / "SKILL.md",
        "_meta.json": SKILL_DIR / "_meta.json",
    }

    for name, path in required_files.items():
        if not check_file_exists(path, name):
            errors.append(f"缺少必需文件: {name}")

    # 检查可选目录
    optional_dirs = {
        "references": SKILL_DIR / "references",
        "assets": SKILL_DIR / "assets",
    }

    for name, path in optional_dirs.items():
        if path.exists():
            print(f"✓ {name}/ 目录存在")
        else:
            print(f"⚪ {name}/ 目录不存在 (可选)")

    # 验证 SKILL.md frontmatter
    print("\n2. 验证 SKILL.md frontmatter...")
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 检查 frontmatter
        if not content.startswith("---"):
            errors.append("SKILL.md 必须以 frontmatter (---) 开头")

        # 提取 frontmatter
        frontmatter_end = content.find("---", 3)
        if frontmatter_end > 0:
            frontmatter = content[3:frontmatter_end].strip()

            if "name:" not in frontmatter:
                errors.append("Frontmatter 必须包含 name 字段")
            if "description:" not in frontmatter:
                errors.append("Frontmatter 必须包含 description 字段")

            # 检查 description 内容
            import re
            desc_match = re.search(r'description:\s*(.+)', frontmatter)
            if desc_match:
                desc = desc_match.group(1).strip()
                if len(desc) < 20:
                    warnings.append("description 内容偏短，可能影响触发准确性")
                print(f"✓ description: {desc[:50]}...")
        else:
            errors.append("Frontmatter 格式错误")

    # 验证 _meta.json
    print("\n3. 验证 _meta.json...")
    meta_json = SKILL_DIR / "_meta.json"
    if meta_json.exists():
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json 必须包含 id 字段")
            if "version" not in meta:
                errors.append("_meta.json 必须包含 version 字段")
            print(f"✓ id: {meta.get('id', 'N/A')}, version: {meta.get('version', 'N/A')}")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查 references 内容
    print("\n4. 检查参考资料...")
    refs_dir = SKILL_DIR / "references"
    if refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        print(f"✓ 找到 {len(ref_files)} 个参考文件")
        for f in ref_files:
            print(f"  - {f.name}")

    # 结果汇总
    print("\n=== 验证结果 ===")
    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✅ 验证通过!")
        return True
    elif not errors:
        print("\n⚠️ 验证通过 (有警告)")
        return True
    else:
        print("\n❌ 验证失败")
        return False

if __name__ == "__main__":
    success = validate_skill()
    sys.exit(0 if success else 1)