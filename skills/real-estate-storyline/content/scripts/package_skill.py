#!/usr/bin/env python3
"""
打包技能脚本 - 将技能目录打包为 .skill 文件
用法: python package_skill.py <技能目录路径>
"""

import os
import sys
import zipfile
import json
from datetime import datetime


def validate_skill(skill_dir):
    """验证技能结构"""
    errors = []
    warnings = []

    # 检查必需文件
    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    if not os.path.exists(skill_md):
        errors.append("SKILL.md 不存在")
    if not os.path.exists(meta_json):
        errors.append("_meta.json 不存在")

    # 验证 _meta.json
    if os.path.exists(meta_json):
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 格式错误: {e}")

    # 验证 SKILL.md frontmatter
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 frontmatter --- 开头")
        if 'name:' not in content[:500]:
            errors.append("SKILL.md frontmatter 缺少 'name:' 字段")
        if 'description:' not in content[:1000]:
            errors.append("SKILL.md frontmatter 缺少 'description:' 字段")

    # 检查目录名称是否包含非ASCII字符
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if not all(ord(c) < 128 or c == '_' or c == '-' for c in d):
                if d not in ['knowledge_base', 'scripts', 'references', 'assets']:
                    warnings.append(f"目录 '{d}' 可能包含非ASCII字符")
        for f in files:
            if not all(ord(c) < 128 or c in ['_', '-', '.'] for c in f):
                if f.endswith('.md'):
                    continue  # md 文件内容可以有中文

    return errors, warnings


def package_skill(skill_dir, output_path=None):
    """打包技能"""
    skill_name = os.path.basename(skill_dir)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"/workspace/temp-skills/{skill_name}.skill"

    print(f"打包技能: {skill_name}")
    print(f"来源目录: {skill_dir}")
    print(f"输出文件: {output_path}")
    print()

    # 验证
    errors, warnings = validate_skill(skill_dir)

    if warnings:
        print("⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("❌ 错误:")
        for e in errors:
            print(f"  - {e}")
        print("打包终止")
        return False

    print("✓ 验证通过")
    print()

    # 创建 ZIP 包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('__')]
            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_dir))
                zf.write(file_path, arcname)
                print(f"  添加: {arcname}")

    print()
    print(f"✓ 打包完成: {output_path}")

    # 显示文件大小
    size = os.path.getsize(output_path)
    print(f"  文件大小: {size / 1024:.1f} KB")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_dir = "/workspace/temp-skills/real-estate-storyline"
    else:
        skill_dir = sys.argv[1]

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在 {skill_dir}")
        sys.exit(1)

    success = package_skill(skill_dir)
    sys.exit(0 if success else 1)
