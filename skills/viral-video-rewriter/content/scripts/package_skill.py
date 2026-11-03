#!/usr/bin/env python3
"""
打包脚本 - 将 viral-video-rewriter 技能打包为 .skill 文件
"""

import os
import json
import zipfile
import sys
from datetime import datetime

def package_skill(skill_dir, output_dir="."):
    """打包技能为 .skill 文件"""
    skill_name = os.path.basename(skill_dir)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    print(f"打包技能: {skill_name}")
    print(f"输出文件: {output_file}")
    print("-" * 50)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            print(f"❌ 缺少必需文件: {file}")
            return False

    # 创建 .skill 文件（实际上是 zip 格式）
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_dir):
                # 排除 scripts 目录（不打包内部脚本）
                if 'scripts' in dirs:
                    dirs.remove('scripts')

                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_dir)
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print("-" * 50)
        print(f"✅ 打包成功: {output_file}")
        return True

    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    package_skill(skill_dir)

if __name__ == "__main__":
    main()
