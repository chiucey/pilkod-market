#!/usr/bin/env python3
"""
打包脚本 - 将技能打包为可分发的 .zip 文件
"""

import os
import sys
import zipfile
import json
from pathlib import Path

def package_skill(skill_dir, output_path=None):
    """打包技能目录为 .zip 文件"""

    skill_name = os.path.basename(skill_dir)

    if output_path is None:
        output_path = f"{skill_dir}.zip"

    print(f"📦 正在打包技能: {skill_name}")

    # 验证必需文件
    required = ['SKILL.md', '_meta.json']
    missing = [f for f in required if not os.path.exists(os.path.join(skill_dir, f))]
    if missing:
        print(f"❌ 缺少必需文件: {', '.join(missing)}")
        return False

    # 创建 zip 包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 跳过 __pycache__ 和隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, os.path.dirname(skill_dir))
                zf.write(file_path, arc_name)
                print(f"  ✓ 添加: {arc_name}")

    print(f"\n✅ 打包完成: {output_path}")
    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)  # 回到技能根目录

    # 默认输出到 /workspace
    output_path = f"/workspace/{os.path.basename(skill_dir)}.zip"

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    success = package_skill(skill_dir, output_path)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())