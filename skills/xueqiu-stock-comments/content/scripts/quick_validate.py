#!/usr/bin/env python3
"""
雪球个股评论分析技能 - 快速验证脚本
验证SKILL.md的frontmatter和结构是否符合规范
"""

import os
import re
import sys

def validate_skill_md(file_path):
    """验证SKILL.md文件"""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter
    if not content.startswith('---'):
        errors.append("Frontmatter必须从第一行开始，以'---'开头")
    else:
        lines = content.split('\n')
        if len(lines) < 3:
            errors.append("Frontmatter格式不正确，需要包含name和description")
        else:
            # 提取frontmatter
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break

            if frontmatter_end == -1:
                errors.append("Frontmatter未正确关闭，缺少结束标记'---'")
            else:
                frontmatter_text = '\n'.join(lines[1:frontmatter_end])

                # 检查必填字段
                if 'name:' not in frontmatter_text:
                    errors.append("Frontmatter缺少'name'字段")

                if 'description:' not in frontmatter_text:
                    errors.append("Frontmatter缺少'description'字段")

                # 检查description内容
                desc_match = re.search(r'description:\s*(.+)', frontmatter_text)
                if desc_match:
                    desc_content = desc_match.group(1).strip()
                    if len(desc_content) < 10:
                        warnings.append("description内容过短，建议更详细的描述")
                    if '当用户' not in desc_content and 'Use when' not in desc_content:
                        warnings.append("description应包含触发短语（如'当用户要求...'）")

    # 检查是否在frontmatter之前有markdown标题
    content_without_frontmatter = content
    if content.startswith('---'):
        lines = content.split('\n')
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                content_without_frontmatter = '\n'.join(lines[i+1:])
                break

    if content_without_frontmatter.strip().startswith('#'):
        errors.append("Frontmatter之后不能直接以markdown标题开头")

    return errors, warnings

def validate_meta_json(file_path):
    """验证_meta.json文件"""
    errors = []
    warnings = []

    import json

    if not os.path.exists(file_path):
        errors.append("_meta.json文件不存在")
        return errors, warnings

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必填字段
        if 'id' not in meta:
            errors.append("_meta.json缺少'id'字段")

        if 'version' not in meta:
            errors.append("_meta.json缺少'version'字段")

        # 检查id是否为数字
        if 'id' in meta and not isinstance(meta['id'], int):
            errors.append("_meta.json的'id'必须是整数")

        # 检查version格式
        if 'version' in meta:
            version_pattern = r'^\d+\.\d+\.\d+$'
            if not re.match(version_pattern, meta['version']):
                warnings.append("_meta.json的'version'建议使用语义化版本格式（如1.0.0）")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json格式错误：{str(e)}")
    except Exception as e:
        errors.append(f"读取_meta.json时发生错误：{str(e)}")

    return errors, warnings

def main():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    meta_json_path = os.path.join(skill_dir, '_meta.json')

    print("=" * 60)
    print("雪球个股评论分析技能 - 验证报告")
    print("=" * 60)
    print()

    all_errors = []
    all_warnings = []

    # 验证SKILL.md
    print("正在验证 SKILL.md...")
    if os.path.exists(skill_md_path):
        errors, warnings = validate_skill_md(skill_md_path)
        all_errors.extend([f"SKILL.md: {e}" for e in errors])
        all_warnings.extend([f"SKILL.md: {w}" for w in warnings])
        if errors:
            for e in errors:
                print(f"  ❌ 错误: {e}")
        if warnings:
            for w in warnings:
                print(f"  ⚠️ 警告: {w}")
        if not errors and not warnings:
            print("  ✅ SKILL.md验证通过")
    else:
        print(f"  ❌ SKILL.md文件不存在: {skill_md_path}")
        all_errors.append("SKILL.md文件不存在")
    print()

    # 验证_meta.json
    print("正在验证 _meta.json...")
    if os.path.exists(meta_json_path):
        errors, warnings = validate_meta_json(meta_json_path)
        all_errors.extend([f"_meta.json: {e}" for e in errors])
        all_warnings.extend([f"_meta.json: {w}" for w in warnings])
        if errors:
            for e in errors:
                print(f"  ❌ 错误: {e}")
        if warnings:
            for w in warnings:
                print(f"  ⚠️ 警告: {w}")
        if not errors and not warnings:
            print("  ✅ _meta.json验证通过")
    else:
        print(f"  ❌ _meta.json文件不存在: {meta_json_path}")
        all_errors.append("_meta.json文件不存在")
    print()

    # 输出总结
    print("=" * 60)
    print("验证总结")
    print("=" * 60)

    if all_errors:
        print(f"❌ 发现 {len(all_errors)} 个错误:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    else:
        print("✅ 所有验证通过！")
        if all_warnings:
            print(f"⚠️ 包含 {len(all_warnings)} 个警告:")
            for w in all_warnings:
                print(f"  - {w}")
        return 0

if __name__ == '__main__':
    sys.exit(main())
