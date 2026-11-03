#!/usr/bin/env python3
"""
国家标准下载器技能 - 打包脚本
生成 .skill 打包文件用于分发
"""

import os
import sys
import json
import shutil
from pathlib import Path
import zipfile
from datetime import datetime

def package_skill(skill_dir, output_dir='/workspace/temp-skills'):
    """打包技能目录为 .skill 文件"""

    skill_dir = Path(skill_dir)
    skill_name = skill_dir.name

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成打包文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 读取 meta 信息
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    print("=" * 50)
    print("国家标准下载器技能 - 打包工具")
    print("=" * 50)
    print(f"\n技能名称: {skill_name}")
    print(f"技能ID: {meta['id']}")
    print(f"版本: {meta['version']}")

    # 创建 ZIP 文件
    print(f"\n正在打包...")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_dir.parent)
                zf.write(file_path, arc_name)
                print(f"  + {arc_name}")

    # 获取文件大小
    file_size = os.path.getsize(output_file)
    print(f"\n打包完成!")
    print(f"输出文件: {output_file}")
    print(f"文件大小: {file_size / 1024:.2f} KB")

    return output_file

if __name__ == '__main__':
    skill_dir = '/workspace/temp-skills/national-standard-downloader'
    output_dir = '/workspace/temp-skills'

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    try:
        output_file = package_skill(skill_dir, output_dir)
        print(f"\n✅ 打包成功!")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)
