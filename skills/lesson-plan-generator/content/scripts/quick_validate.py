#!/usr/bin/env python3
"""
快速验证脚本：检查lesson-plan-generator技能的结构和内容
"""
import os
import re
import json
import sys

def validate_skill():
    """验证技能结构和内容"""
    errors = []
    warnings = []

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    meta_path = os.path.join(skill_dir, "_meta.json")

    # 检查必需文件
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md 文件不存在")
        return errors, warnings

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return errors, warnings

    # 读取并验证 SKILL.md
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 位置（必须在第一行）
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 YAML frontmatter")
    else:
        frontmatter_text = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter_text:
            errors.append("frontmatter 缺少 name 字段")

        if 'description:' not in frontmatter_text:
            errors.append("frontmatter 缺少 description 字段")

        # 检查触发短语
        if '生成教案' not in frontmatter_text and '教案' not in frontmatter_text:
            warnings.append("description 中应包含教案相关触发短语")

    # 读取并验证 _meta.json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        errors.append("_meta.json 缺少 id 字段")
    elif not isinstance(meta['id'], (int, str)):
        errors.append("_meta.json id 必须是数字或字符串")

    if 'version' not in meta:
        errors.append("_meta.json 缺少 version 字段")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        warnings.append("version 建议使用语义化版本格式 (x.y.z)")

    # 检查内容完整性
    required_sections = [
        '收集备课信息', '生成课前部分', '生成课中部分',
        '生成课后部分', '生成课后评价', '输出完整教案'
    ]

    for section in required_sections:
        if section not in content:
            warnings.append(f"缺少 '{section}' 部分")

    return errors, warnings


def main():
    """主函数"""
    errors, warnings = validate_skill()

    if errors:
        print("❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    if warnings:
        print("⚠️ 验证通过（有警告）:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("✅ 验证通过")

    sys.exit(0)


if __name__ == "__main__":
    main()
