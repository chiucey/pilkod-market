#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可分发的 .skill 文件
"""

import os
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

def create_package(skill_dir, output_dir):
    """创建技能包"""
    skill_name = os.path.basename(skill_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"{skill_name}_{timestamp}.skill"
    package_path = os.path.join(output_dir, package_name)

    # 读取 meta 信息
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 创建打包目录
    temp_dir = os.path.join(output_dir, f"_temp_{skill_name}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        # 复制文件（排除临时文件和敏感文件）
        exclude_patterns = ['__pycache__', '.git', '.DS_Store', '.env', '*.pyc']

        for root, dirs, files in os.walk(skill_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in exclude_patterns and not d.startswith('_temp')]

            # 计算相对路径
            rel_path = os.path.relpath(root, skill_dir)

            for file in files:
                # 跳过排除的文件
                if any(file.endswith(pat.replace('*', '')) for pat in exclude_patterns if '*' in pat):
                    continue
                if file.startswith('.'):
                    continue

                src = os.path.join(root, file)
                dst = os.path.join(temp_dir, rel_path if rel_path != '.' else '', file)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

        # 创建 package.json
        package_info = {
            "name": skill_name,
            "version": meta['version'],
            "created_at": datetime.now().isoformat(),
            "skill_id": meta['id']
        }
        with open(os.path.join(temp_dir, 'package.json'), 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2, ensure_ascii=False)

        # 打包为 zip
        shutil.make_archive(package_path.replace('.skill', ''), 'zip', temp_dir)

        # 重命名为 .skill
        os.rename(package_path.replace('.skill', '.zip'), package_path)

        print("=" * 50)
        print("打包完成！")
        print("=" * 50)
        print(f"技能名称: {skill_name}")
        print(f"版本: {meta['version']}")
        print(f"技能 ID: {meta['id']}")
        print(f"输出路径: {package_path}")

        return package_path

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    # 解析命令行参数
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
        if os.path.isfile(skill_path):
            skill_dir = os.path.dirname(skill_path)
        elif os.path.isdir(skill_path):
            skill_dir = skill_path

    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    print(f"打包技能目录: {skill_dir}")

    package_path = create_package(skill_dir, output_dir)
    print(f"\n✓ 打包成功: {package_path}")

if __name__ == "__main__":
    main()
