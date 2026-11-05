#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可分发的.skill文件
"""

import os
import zipfile
import json
import sys
from datetime import datetime

def get_skill_meta(skill_path):
    """获取技能元数据"""
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def create_skill_package(skill_path, output_dir="."):
    """创建技能包"""
    skill_name = os.path.basename(skill_path)
    meta = get_skill_meta(skill_path)
    version = meta.get('version', '1.0.0')

    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过__pycache__等目录
            dirs[:] = [d for d in dirs if not d.startswith('__')]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arcname)

    print(f"✅ 技能包已生成: {output_file}")
    return output_file

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "investment-industry-analysis"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if not os.path.exists(skill_path):
        print(f"❌ 技能路径不存在: {skill_path}")
        return 1

    output_file = create_skill_package(skill_path, output_dir)
    print(f"📦 打包完成: {output_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
