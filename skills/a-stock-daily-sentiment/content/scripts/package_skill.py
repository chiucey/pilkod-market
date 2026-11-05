#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill打包脚本
将skill打包为可分发的.skill文件
"""

import os
import shutil
import zipfile
from datetime import datetime


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """
    打包skill为.skill文件

    Args:
        skill_dir: skill目录路径
        output_dir: 输出目录，默认为skill_dir的父目录

    Returns:
        打包后的.skill文件路径
    """
    # 获取skill名称
    skill_name = os.path.basename(skill_dir.rstrip('/'))

    # 默认输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    # 创建打包目录
    package_dir = os.path.join(output_dir, f'{skill_name}_package')
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)

    # 复制文件
    for item in os.listdir(skill_dir):
        src = os.path.join(skill_dir, item)
        dst = os.path.join(package_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    # 创建.skill文件
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    skill_file = os.path.join(output_dir, f'{skill_name}_{timestamp}.skill')

    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, package_dir)
                zf.write(file_path, arc_name)

    # 清理临时目录
    shutil.rmtree(package_dir)

    print(f"Skill打包完成: {skill_file}")
    return skill_file


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = '/workspace/temp-skills/a-stock-daily-sentiment'

    skill_file = package_skill(skill_dir)
    print(f"生成文件: {skill_file}")
