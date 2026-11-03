#!/usr/bin/env python3
"""
企业资信评估技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import json
import shutil
import zipfile
from datetime import datetime

def load_meta(skill_path):
    """加载 _meta.json"""
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def package_skill(skill_path, output_dir="/workspace/temp-skills"):
    """打包技能"""
    skill_name = os.path.basename(skill_path)
    meta = load_meta(skill_path)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{skill_name}_{meta['version']}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建 zip 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 排除 __pycache__ 等目录
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

            for file in files:
                # 排除 .pyc 等文件
                if file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zipf.write(file_path, arcname)

    print("=" * 50)
    print("企业资信评估技能 - 打包完成")
    print("=" * 50)
    print(f"\n技能名称: {skill_name}")
    print(f"版本: {meta['version']}")
    print(f"打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n输出文件: {output_path}")
    print(f"\n包含文件:")
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if not file.endswith('.pyc'):
                rel_path = os.path.relpath(os.path.join(root, file), skill_path)
                print(f"  - {rel_path}")
    print("=" * 50)

    return output_path

def main():
    skill_path = "/workspace/temp-skills/enterprise-credit-assessment"
    output_path = package_skill(skill_path)
    print(f"\n技能已成功打包!")
    return output_path

if __name__ == "__main__":
    main()
