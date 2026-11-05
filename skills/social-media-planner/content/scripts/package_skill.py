#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime

def load_meta(skill_dir):
    """加载 _meta.json"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_package(skill_dir, output_dir):
    """创建技能包"""
    # 处理相对路径如 "."
    abs_skill_dir = os.path.abspath(skill_dir)
    skill_name = os.path.basename(abs_skill_dir)
    meta = load_meta(abs_skill_dir)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成包文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}_{meta['version']}_{timestamp}.skill"
    package_path = os.path.join(output_dir, package_name)

    # 创建 zip 包
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(abs_skill_dir):
            # 排除 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('__') and d != '.git']

            for file in files:
                if file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, abs_skill_dir)
                zf.write(file_path, arcname)

    print(f"技能包已创建: {package_path}")
    return package_path

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '/workspace/temp-skills/packages'

    print("=" * 50)
    print("技能打包开始")
    print("=" * 50)
    print(f"源目录: {skill_dir}")
    print(f"输出目录: {output_dir}")

    # 验证必要文件
    if not os.path.exists(os.path.join(skill_dir, 'SKILL.md')):
        print("[✗] SKILL.md 不存在")
        sys.exit(1)

    if not os.path.exists(os.path.join(skill_dir, '_meta.json')):
        print("[✗] _meta.json 不存在")
        sys.exit(1)

    package_path = create_package(skill_dir, output_dir)

    print("=" * 50)
    print(f"✓ 打包成功: {package_path}")
    print("=" * 50)

if __name__ == '__main__':
    main()
