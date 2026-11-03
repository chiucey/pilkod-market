#!/usr/bin/env python3
"""
视频封面生成器技能验证脚本
验证 SKILL.md 的 frontmatter、结构和内容完整性
"""

import os
import re
import sys

def validate_skill(skill_path):
    """验证技能文件的完整性和正确性"""
    errors = []
    warnings = []

    # 检查目录结构
    if not os.path.exists(skill_path):
        errors.append(f"技能目录不存在: {skill_path}")
        return errors, warnings

    skill_md_path = os.path.join(skill_path, "SKILL.md")
    meta_json_path = os.path.join(skill_path, "_meta.json")

    # 检查必填文件
    if not os.path.exists(skill_md_path):
        errors.append("缺少 SKILL.md 文件")

    if not os.path.exists(meta_json_path):
        errors.append("缺少 _meta.json 文件")

    if errors:
        return errors, warnings

    # 验证 SKILL.md frontmatter
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 是否在第一行
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头，不能有 markdown 标题")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 检查必填字段
        if 'name:' not in frontmatter:
            errors.append("frontmatter 缺少 name 字段")

        if 'description:' not in frontmatter:
            errors.append("frontmatter 缺少 description 字段")

        # 提取 name 值
        name_match = re.search(r'name:\s*(.+)', frontmatter)
        if name_match:
            name = name_match.group(1).strip()
            folder_name = os.path.basename(skill_path)
            if name != folder_name:
                errors.append(f"name 字段值 '{name}' 与文件夹名称 '{folder_name}' 不匹配")

        # 检查 description 长度
        desc_match = re.search(r'description:\s*(.+)', frontmatter)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append("description 过短，可能影响触发准确性")

    else:
        errors.append("无法解析 frontmatter")

    # 验证 _meta.json
    import json
    with open(meta_json_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        errors.append("_meta.json 缺少 id 字段")

    if 'version' not in meta:
        errors.append("_meta.json 缺少 version 字段")

    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"version 格式不正确，应为语义化版本如 '1.0.0'，实际为: {version}")

    # 检查内容完整性
    required_sections = [
        'Step 1',
        'Step 2',
        'Step 3',
        'image_synthesize',
    ]

    for section in required_sections:
        if section not in content:
            errors.append(f"缺少必需内容模块: {section}")

    # 检查禁止性约束
    forbidden_patterns = [
        (r'主标题.*超过.*汉字', "主标题长度约束"),
        (r'副标题.*超过.*汉字', "副标题长度约束"),
        (r'严禁.*输出.*解释', "输出约束"),
        (r'1920x1080', "分辨率约束"),
        (r'16:9', "比例约束"),
    ]

    for pattern, name in forbidden_patterns:
        if not re.search(pattern, content):
            warnings.append(f"建议添加 {name} 约束说明")

    return errors, warnings

def main():
    skill_path = "/workspace/temp-skills/video-cover-generator"

    print("=" * 50)
    print("视频封面生成器技能验证")
    print("=" * 50)

    errors, warnings = validate_skill(skill_path)

    print(f"\n技能路径: {skill_path}")

    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")

    if not errors and not warnings:
        print("\n✅ 验证通过！技能结构完整正确。")

    print("\n" + "=" * 50)

    # 返回退出码
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()