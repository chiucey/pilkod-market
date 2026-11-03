#!/usr/bin/env python3
"""
快速验证脚本 - daily-stock-news-analysis 技能
验证 SKILL.md frontmatter、文件结构和命名规范
"""

import os
import re
import sys
from pathlib import Path

def validate_skill():
    """验证技能文件结构和内容"""
    skill_dir = Path("/workspace/temp-skills/daily-stock-news-analysis")
    errors = []
    warnings = []

    # 1. 检查目录结构
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_dir / f).exists():
            errors.append(f"缺少必需文件: {f}")

    # 2. 验证 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 检查第一行是否为 frontmatter 开始
        lines = content.split("\n")
        if not lines[0].strip().startswith("---"):
            errors.append("SKILL.md 必须以 --- 开头（frontmatter）")

        # 提取 frontmatter
        if lines[0].strip() == "---":
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    frontmatter_end = i
                    break

            if frontmatter_end == -1:
                errors.append("frontmatter 未正确关闭（缺少结束 ---）")
            else:
                frontmatter = "\n".join(lines[1:frontmatter_end])

                # 检查必需字段
                if not re.search(r'^name:\s*.+$', frontmatter, re.MULTILINE):
                    errors.append("frontmatter 缺少 name 字段")

                if not re.search(r'^description:\s*.+$', frontmatter, re.MULTILINE):
                    errors.append("frontmatter 缺少 description 字段")

                # 验证 name 格式
                name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip()
                    if not re.match(r'^[a-z0-9-]+$', name):
                        errors.append(f"name 格式错误: '{name}'，应使用小写字母、数字和连字符")
                    if name != skill_dir.name:
                        warnings.append(f"name '{name}' 与目录名 '{skill_dir.name}' 不一致")

        # 检查是否在 frontmatter 开始前有 markdown 标题（这是错误的）
        # frontmatter 开始后可以有任意内容，包括标题
        if lines[0].strip() == "---":
            in_frontmatter = False
            found_frontmatter_end = False
            for i, line in enumerate(lines):
                # 找到 frontmatter 开始
                if line.strip() == "---" and not in_frontmatter:
                    in_frontmatter = True
                    continue
                # 找到 frontmatter 结束
                if line.strip() == "---" and in_frontmatter:
                    found_frontmatter_end = True
                    in_frontmatter = False
                    continue
                # frontmatter 结束后，不再检查
                if found_frontmatter_end:
                    continue
                # 只在 frontmatter 开始前检查是否有标题
                if not in_frontmatter and line.strip().startswith("#"):
                    errors.append(f"markdown 标题 '#' 出现在 frontmatter 之前（第{i+1}行）")
                    break

    # 3. 验证 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 version 字段")
            if "version" in meta:
                version = meta["version"]
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    errors.append(f"version 格式错误: '{version}'，应使用语义化版本如 1.0.0")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON格式错误: {e}")

    # 4. 检查文件路径和名称（仅英文）
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if not re.match(r'^[a-zA-Z0-9_-]+$', d):
                errors.append(f"目录名包含非英文字符: {d}")
        for f in files:
            if not re.match(r'^[a-zA-Z0-9_.-]+$', f):
                errors.append(f"文件名包含非英文字符: {f}")

    # 输出结果
    print("=" * 50)
    print("技能验证结果")
    print("=" * 50)

    if warnings:
        print(f"\n⚠️  警告 ({len(warnings)}项):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ 错误 ({len(errors)}项):")
        for e in errors:
            print(f"  - {e}")
        print("\n验证失败，请修复以上错误。")
        return False
    else:
        print("\n✅ 验证通过！")
        return True

if __name__ == "__main__":
    success = validate_skill()
    sys.exit(0 if success else 1)
