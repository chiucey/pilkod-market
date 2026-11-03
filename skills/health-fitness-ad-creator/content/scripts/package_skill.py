#!/usr/bin/env python3
"""
打包技能为 .skill 文件
Usage: python package_skill.py <skill_path> [output_dir]
"""
import os
import sys
import zipfile
import shutil
from datetime import datetime

def package_skill(skill_path, output_dir=None):
    """将技能打包为 .skill 文件"""

    # 获取技能名称（目录名）
    skill_name = os.path.basename(skill_path)

    # 默认输出到当前目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_path) or '.'

    # 创建打包目录
    temp_dir = os.path.join(output_dir, '.skill_temp')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制技能文件
    for item in os.listdir(skill_path):
        src = os.path.join(skill_path, item)
        # 跳过临时文件和隐藏文件
        if item.startswith('.') or item.endswith('.pyc'):
            continue
        if os.path.isdir(src) and item not in ['scripts', 'references', 'assets']:
            continue
        dst = os.path.join(temp_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    # 创建打包文件
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}.{timestamp}.skill")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arc_name)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    # 复制到最终位置（不带时间戳的版本）
    final_file = os.path.join(output_dir, f"{skill_name}.skill")
    shutil.copy2(output_file, final_file)

    print(f"✓ Skill packaged successfully!")
    print(f"  Output: {final_file}")
    print(f"  Backup: {output_file}")

    return final_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_path):
        print(f"Error: Skill path not found: {skill_path}")
        sys.exit(1)

    package_skill(skill_path, output_dir)

if __name__ == "__main__":
    main()