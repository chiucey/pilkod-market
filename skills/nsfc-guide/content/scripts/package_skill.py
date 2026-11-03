#!/usr/bin/env python3
"""
国基金申报指南技能打包脚本
将技能打包为可分发的.skill文件
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent / "dist"

def get_skill_info():
    """读取技能元信息"""
    meta_path = SKILL_ROOT / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_package():
    """创建技能包"""
    skill_info = get_skill_info()
    skill_name = skill_info.get('name', 'unknown')
    skill_version = skill_info.get('version', '1.0.0')

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 输出文件名
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = OUTPUT_DIR / f"{skill_name}-{skill_version}-{timestamp}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历技能目录
        for root, dirs, files in os.walk(SKILL_ROOT):
            # 排除dist目录
            if 'dist' in dirs:
                dirs.remove('dist')

            for file in files:
                file_path = Path(root) / file
                # 计算相对路径
                arcname = file_path.relative_to(SKILL_ROOT)
                zipf.write(file_path, arcname)
                print(f"添加: {arcname}")

    print(f"\n技能包已创建: {output_file}")
    print(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")

    return output_file

def verify_package(package_path):
    """验证包内容"""
    print("\n验证包内容...")

    with zipfile.ZipFile(package_path, 'r') as zipf:
        file_list = zipf.namelist()

        # 检查必需文件
        required_files = ['SKILL.md', '_meta.json']
        for rf in required_files:
            if rf not in file_list:
                print(f"缺少必需文件: {rf}")
                return False

        # 显示文件列表
        print("\n包内容:")
        for f in file_list:
            info = zipf.getinfo(f)
            print(f"  {f} ({info.file_size} bytes)")

    print("\n验证通过！")
    return True

def main():
    print("="*60)
    print("国基金申报指南技能 - 打包工具")
    print("="*60)

    # 创建包
    package_path = create_package()

    # 验证包
    if verify_package(package_path):
        print("\n打包完成！")
        return 0
    else:
        print("\n打包失败！")
        return 1

if __name__ == "__main__":
    exit(main())
