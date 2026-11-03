#!/usr/bin/env python3
"""打包 OpenClaw 自我进化引擎技能"""

import os
import json
import shutil
from pathlib import Path

def package_skill(skill_dir, output_dir='.'):
    """打包技能为 .skill 文件"""
    skill_name = 'openclaw-self-evolution'
    output_file = os.path.join(output_dir, f'{skill_name}.skill')

    # 读取 meta.json 获取版本
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    version = meta['version']

    # 创建临时打包目录
    temp_dir = f'/tmp/{skill_name}_package'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制文件
    for item in os.listdir(skill_dir):
        src = os.path.join(skill_dir, item)
        dst = os.path.join(temp_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    # 创建 .skill 文件（zip 格式）
    skill_file = f'/tmp/{skill_name}.skill'
    if os.path.exists(skill_file):
        os.remove(skill_file)

    shutil.make_archive('/tmp/openclaw-self-evolution', 'zip', temp_dir)
    shutil.move('/tmp/openclaw-self-evolution.zip', skill_file)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"✅ 技能打包完成: {skill_file}")
    print(f"版本: {version}")
    return skill_file

if __name__ == '__main__':
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    package_skill(skill_dir)
