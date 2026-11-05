#!/usr/bin/env python3
"""
技能打包脚本
Package skill for distribution
"""

import os
import json
import shutil
import zipfile


def get_skill_info(skill_path):
    """从_meta.json读取技能信息"""
    meta_path = os.path.join(skill_path, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def package_skill(skill_path, output_dir='/workspace/temp-skills'):
    """打包技能为.skill文件"""
    skill_name = os.path.basename(skill_path)
    skill_info = get_skill_info(skill_path)
    skill_id = skill_info.get('id', 'unknown')
    version = skill_info.get('version', '1.0.0')

    # 创建输出文件名
    output_file = os.path.join(output_dir, f'{skill_name}.skill')

    # 创建打包目录
    package_dir = os.path.join(output_dir, '_package_temp')

    # 清理旧的打包目录
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    # 复制文件到打包目录
    shutil.copytree(skill_path, os.path.join(package_dir, skill_name))

    # 创建ZIP文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(package_dir)

    print(f"✅ 技能打包成功！")
    print(f"   技能名称: {skill_name}")
    print(f"   技能ID: {skill_id}")
    print(f"   版本: {version}")
    print(f"   输出路径: {output_file}")

    return output_file


def main():
    skill_path = '/workspace/temp-skills/image-to-ascii'
    output_file = package_skill(skill_path)
    print(f"\n打包文件已生成: {output_file}")


if __name__ == '__main__':
    main()
