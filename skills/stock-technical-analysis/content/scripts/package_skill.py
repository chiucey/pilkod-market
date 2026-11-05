#!/usr/bin/env python3
"""
技能打包脚本 - stock-technical-analysis
生成可发布的 .skill 文件
"""

import os
import zipfile
import json
from datetime import datetime

SKILL_DIR = "/workspace/temp-skills/stock-technical-analysis"
OUTPUT_DIR = "/workspace/temp-skills"

def validate_skill():
    """验证技能结构和内容"""
    errors = []

    # 检查必需文件
    required_files = [
        "SKILL.md",
        "_meta.json"
    ]

    for f in required_files:
        path = os.path.join(SKILL_DIR, f)
        if not os.path.exists(path):
            errors.append(f"缺少必需文件: {f}")

    # 检查 _meta.json
    meta_path = os.path.join(SKILL_DIR, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")

    # 检查 SKILL.md frontmatter
    skill_path = os.path.join(SKILL_DIR, "SKILL.md")
    if os.path.exists(skill_path):
        with open(skill_path, 'r') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 frontmatter 开头")
            if 'name:' not in content:
                errors.append("SKILL.md 缺少 name 字段")
            if 'description:' not in content:
                errors.append("SKILL.md 缺少 description 字段")

    return errors

def package_skill():
    """打包技能"""
    print("=" * 50)
    print("股票技术分析技能打包工具")
    print("=" * 50)

    # 验证
    print("\n[1/3] 验证技能结构...")
    errors = validate_skill()
    if errors:
        print("验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False
    print("  ✓ 验证通过")

    # 创建 zip 包
    print("\n[2/3] 创建技能包...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"stock-technical-analysis_{timestamp}.skill"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, SKILL_DIR)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"  ✓ 技能包已创建: {output_name}")

    # 输出摘要
    print("\n[3/3] 打包完成")
    print("=" * 50)
    print(f"输出文件: {output_path}")
    print(f"技能ID: 1747476920")
    print(f"技能名称: stock-technical-analysis")
    print("=" * 50)

    return True

if __name__ == "__main__":
    success = package_skill()
    exit(0 if success else 1)
