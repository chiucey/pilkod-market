#!/usr/bin/env python3
"""
Content Checker 技能验证脚本
验证 SKILL.md 和 _meta.json 的结构和格式
"""

import os
import json
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能文件夹的结构和内容"""
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # 检查目录存在
    if not skill_path.exists():
        print(f"❌ 错误: 路径不存在: {skill_path}")
        return False

    if not skill_path.is_dir():
        print(f"❌ 错误: 路径不是目录: {skill_path}")
        return False

    print(f"🔍 验证技能: {skill_path.name}")
    print("=" * 50)

    # 1. 检查 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("缺少 SKILL.md 文件")
    else:
        # 读取并验证 SKILL.md
        content = skill_md.read_text(encoding='utf-8')

        # 检查 frontmatter 是否在第一行
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")
        else:
            # 提取 frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter_text = frontmatter_match.group(1)

                # 检查必需字段
                if 'name:' not in frontmatter_text:
                    errors.append("frontmatter 缺少 'name' 字段")
                if 'description:' not in frontmatter_text:
                    errors.append("frontmatter 缺少 'description' 字段")

                # 检查 name 格式
                name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip()
                    if not re.match(r'^[a-z0-9-]+$', name):
                        errors.append(f"name 必须使用连字符格式 (如 'content-checker'): 当前 '{name}'")
                    if name != skill_path.name:
                        warnings.append(f"name '{name}' 与文件夹名 '{skill_path.name}' 不匹配")
            else:
                errors.append("无法解析 YAML frontmatter")

        # 检查标题不在 frontmatter 之前
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if line == '---':
                if frontmatter_end == -1:
                    frontmatter_end = i
                else:
                    break

        # 检查 frontmatter 之前是否有 markdown 内容
        for i in range(frontmatter_end):
            if lines[i].strip().startswith('#'):
                errors.append("markdown 标题不能出现在 frontmatter 之前")
                break

    # 2. 检查 _meta.json 存在
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))

            # 检查必需字段
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            elif not isinstance(meta['id'], int):
                errors.append("_meta.json 'id' 必须是整数")

            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
            elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                errors.append("_meta.json 'version' 必须是语义化版本 (如 '1.0.0')")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 解析错误: {e}")

    # 3. 检查文件命名
    if skill_path.name != skill_path.name.lower():
        warnings.append("文件夹名应使用小写字母")

    if len(skill_path.name) > 64:
        errors.append(f"文件夹名过长 ({len(skill_path.name)}/64)")

    # 4. 检查 references/ 目录 (可选但推荐)
    references_dir = skill_path / "references"
    if references_dir.exists():
        print("✓ references/ 目录存在 (推荐)")

    # 输出结果
    print("\n📊 验证结果:")

    if warnings:
        print("\n⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")
        print(f"\n❌ 验证失败 ({len(errors)} 个错误)")
        return False

    print("\n✅ 验证通过!")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = "."

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
