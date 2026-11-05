#!/usr/bin/env python3
"""
打包脚本：将lesson-plan-generator技能打包为可发布的格式
"""
import os
import json
import shutil
import zipfile
from datetime import datetime

def get_skill_id(skill_dir):
    """从_meta.json读取技能ID"""
    meta_path = os.path.join(skill_dir, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return str(meta['id'])

def get_skill_version(skill_dir):
    """从_meta.json读取技能版本"""
    meta_path = os.path.join(skill_dir, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta['version']

def package_skill():
    """打包技能"""
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    # 获取技能信息
    skill_id = get_skill_id(skill_dir)
    version = get_skill_version(skill_dir)
    skill_name = os.path.basename(skill_dir)

    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_name = f"{skill_name}-{version}-{timestamp}.skill"
    output_path = os.path.join(os.path.dirname(skill_dir), output_name)

    # 创建zip包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除 __pycache__ 等目录
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_path}")
    return output_path


if __name__ == "__main__":
    package_skill()
