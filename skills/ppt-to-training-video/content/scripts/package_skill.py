#!/usr/bin/env python3
"""
PPT转培训视频 - 打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import sys
import json
import zipfile
import shutil
from datetime import datetime

def get_skill_meta(skill_path):
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def package_skill(skill_path, output_dir='output'):
    """打包技能为.skill文件"""
    if not os.path.exists(skill_path):
        print(f"错误: 技能路径不存在 {skill_path}")
        return False

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取元数据
    meta = get_skill_meta(skill_path)
    skill_name = os.path.basename(skill_path)
    version = meta.get('version', '1.0.0')

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_v{version}_{timestamp}.skill")

    # 打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和临时文件
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)

    print(f"技能已打包: {output_file}")
    return output_file

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'

    print("=== 打包PPT转培训视频技能 ===")
    result = package_skill(skill_path, output_dir)

    if result:
        print(f"打包成功: {result}")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
