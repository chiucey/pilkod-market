#!/usr/bin/env python3
"""
打包技能为 .skill 文件
"""

import os
import json
import shutil
import zipfile
from datetime import datetime

def package_skill(skill_dir, output_dir="/workspace"):
    """打包技能为 .skill 文件"""

    skill_name = os.path.basename(skill_dir)

    # 读取 meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        print("❌ 缺少 _meta.json")
        return None

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 生成输出文件名
    version = meta.get('version', '1.0.0')
    output_file = os.path.join(output_dir, f"{skill_name}_{version}.skill")

    # 创建打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_dir))
                zipf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return output_file

def main():
    import sys

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认当前目录
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        skill_dir = os.path.dirname(skill_dir)

    output_file = package_skill(skill_dir)
    if output_file:
        print(f"\n打包完成！")
        print(f"文件位置: {output_file}")

if __name__ == "__main__":
    main()
