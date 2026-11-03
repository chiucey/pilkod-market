#!/usr/bin/env python3
"""
MIDI Instrument Comparison Skill Package Builder
将技能打包为 .skill 文件格式
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

SKILL_DIR = "/workspace/temp-skills/midi-instrument-comparison"
OUTPUT_DIR = "/workspace/temp-skills"
SKILL_NAME = "midi-instrument-comparison"


def validate_skill_structure(skill_dir: str) -> tuple[bool, str]:
    """验证技能目录结构"""
    required_files = [
        "SKILL.md",
        "_meta.json"
    ]

    required_dirs = [
        "scripts",
        "references"
    ]

    if not os.path.exists(skill_dir):
        return False, f"技能目录不存在: {skill_dir}"

    # 检查必需文件
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            return False, f"缺少必需文件: {file}"

    # 检查必需目录
    for dir_name in required_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if not os.path.exists(dir_path):
            return False, f"缺少必需目录: {dir_name}"

    # 验证 SKILL.md frontmatter
    with open(os.path.join(skill_dir, "SKILL.md"), 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            return False, "SKILL.md 必须以 YAML frontmatter 开头"
        if 'name:' not in content[:500]:
            return False, "SKILL.md frontmatter 必须包含 name 字段"
        if 'description:' not in content[:500]:
            return False, "SKILL.md frontmatter 必须包含 description 字段"

    # 验证 _meta.json
    with open(os.path.join(skill_dir, "_meta.json"), 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta:
            return False, "_meta.json 必须包含 id 字段"
        if 'version' not in meta:
            return False, "_meta.json 必须包含 version 字段"

    return True, "验证通过"


def package_skill(skill_dir: str, output_dir: str) -> str:
    """打包技能为 .skill 文件"""
    skill_name = os.path.basename(skill_dir.rstrip('/'))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 创建 ZIP 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 跳过空目录和 __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('__') and d != '__pycache__']

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"✅ 技能打包成功: {output_file}")
    return output_file


def main():
    print("=" * 60)
    print("MIDI Instrument Comparison Skill - Package Builder")
    print("=" * 60)

    # 验证结构
    print("\n📋 验证技能结构...")
    valid, message = validate_skill_structure(SKILL_DIR)
    if not valid:
        print(f"❌ 验证失败: {message}")
        sys.exit(1)
    print(f"✅ {message}")

    # 打包
    print("\n📦 正在打包技能...")
    output_file = package_skill(SKILL_DIR, OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("打包完成!")
    print(f"输出文件: {output_file}")
    print("=" * 60)

    return output_file


if __name__ == "__main__":
    main()