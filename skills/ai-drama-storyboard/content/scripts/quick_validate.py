#!/usr/bin/env python3
"""
快速验证脚本 - AI短剧分镜脚本技能
检查 SKILL.md 结构和 _meta.json
"""

import json
import os
import sys
from pathlib import Path

def validate_skill():
    """验证技能文件结构和内容"""
    errors = []
    warnings = []

    skill_dir = Path(__file__).parent.parent

    # 1. 检查 _meta.json
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 解析错误: {e}")

    # 2. 检查 SKILL.md
    skill_path = skill_dir / "SKILL.md"
    if not skill_path.exists():
        errors.append("缺少 SKILL.md 文件")
    else:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 frontmatter
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")

        # 解析 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                if 'name:' not in frontmatter:
                    errors.append("frontmatter 缺少 'name' 字段")
                if 'description:' not in frontmatter:
                    errors.append("frontmatter 缺少 'description' 字段")
            else:
                errors.append("frontmatter 格式不正确")

        # 检查内容长度
        if len(content) < 500:
            warnings.append("SKILL.md 内容过短，可能不完整")

        # 检查核心关键词
        keywords = ['镜头', '运镜', '景别', '音效', '台词', '时长']
        missing = [k for k in keywords if k not in content]
        if missing:
            warnings.append(f"缺少关键词: {', '.join(missing)}")

    # 3. 检查文件夹名称
    folder_name = skill_dir.name
    if not folder_name.replace('-', '').replace('_', '').isalnum():
        warnings.append(f"文件夹名称 '{folder_name}' 包含非英文字符")

    # 4. 检查 references 目录
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        if len(ref_files) < 1:
            warnings.append("references 目录为空，建议添加参考资料")

    # 输出结果
    print("=" * 60)
    print("技能验证报告")
    print("=" * 60)

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"   - {e}")

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"   - {w}")

    if not errors and not warnings:
        print("\n✅ 验证通过！")
    elif not errors:
        print("\n✅ 基础验证通过（有警告）")
    else:
        print("\n❌ 验证失败")

    print("=" * 60)

    return len(errors) == 0

if __name__ == "__main__":
    success = validate_skill()
    sys.exit(0 if success else 1)
