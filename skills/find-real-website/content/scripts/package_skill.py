#!/usr/bin/env python3
"""
打包技能为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict


def read_json(filepath: str) -> Dict:
    """读取JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill_structure(skill_path: str) -> Tuple[bool, List[str]]:
    """验证技能目录结构"""
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = os.path.join(skill_path, filename)
        if not os.path.exists(filepath):
            errors.append(f"缺少必需文件: {filename}")

    # 验证 _meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        try:
            meta = read_json(meta_path)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    # 验证 SKILL.md frontmatter
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")
        else:
            # 简单验证 frontmatter 结构
            parts = content.split('---')
            if len(parts) < 3:
                errors.append("SKILL.md frontmatter 格式错误")
            else:
                frontmatter = parts[1]
                if 'name:' not in frontmatter:
                    errors.append("frontmatter 缺少 'name:' 字段")
                if 'description:' not in frontmatter:
                    errors.append("frontmatter 缺少 'description:' 字段")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_path: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)

    # 验证结构
    is_valid, errors = validate_skill_structure(skill_path)
    if not is_valid:
        print("❌ 技能结构验证失败:")
        for error in errors:
            print(f"   • {error}")
        sys.exit(1)

    print(f"✅ 技能结构验证通过")

    # 创建输出目录
    if output_path:
        output_dir = os.path.dirname(os.path.abspath(output_path))
    else:
        output_dir = os.path.join(os.path.dirname(skill_path), 'dist')

    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 创建 zip 包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 排除特定目录
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'dist']]

            for file in files:
                # 排除特定文件
                if file.endswith('.pyc') or file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zipf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return output_file


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_path]")
        print("示例: python package_skill.py ../find-real-website")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_path):
        print(f"❌ 技能目录不存在: {skill_path}")
        sys.exit(1)

    output_file = package_skill(skill_path, output_path)
    print(f"\n打包完成！")
    print(f"文件位置: {output_file}")


if __name__ == "__main__":
    main()
