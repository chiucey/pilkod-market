#!/usr/bin/env python3
"""
进销存技能打包脚本
将技能打包为可分发的.skill文件
"""

import os
import sys
import json
import zipfile
from datetime import datetime

def get_skill_info(skill_dir):
    """获取技能信息"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def package_skill(skill_dir, output_dir=None):
    """打包技能"""
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    # 获取技能信息
    meta = get_skill_info(skill_dir)
    skill_name = os.path.basename(skill_dir)

    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_v{meta['version']}_{timestamp}.skill")

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)

                # 跳过.skill文件和隐藏文件
                if file.endswith('.skill') or file.startswith('.'):
                    continue

                zf.write(file_path, arcname)

    print(f"✓ 技能已打包: {output_file}")
    return output_file

def main():
    # 获取技能目录
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_dir = os.path.dirname(script_dir)

    print(f"打包技能: {skill_dir}")
    print("-" * 50)

    try:
        output_file = package_skill(skill_dir)
        print("-" * 50)
        print("✓ 打包成功")
        return 0
    except Exception as e:
        print(f"✗ 打包失败: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
