#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可发布的.skill文件
"""

import os
import json
import shutil
import zipfile
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """
    打包技能为.skill文件

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录，默认与技能目录同级别

    Returns:
        打包后的.skill文件路径
    """
    skill_name = os.path.basename(skill_path)

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)
    else:
        os.makedirs(output_dir, exist_ok=True)

    # 创建临时打包目录
    temp_dir = os.path.join(output_dir, f".temp_{skill_name}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 读取_meta.json获取版本信息
    meta_path = os.path.join(skill_path, "_meta.json")
    version = "1.0.0"
    skill_id = "unknown"

    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            version = meta.get('version', '1.0.0')
            skill_id = meta.get('id', 'unknown')

    # 打包文件
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加技能目录中的所有文件
        for root, dirs, files in os.walk(skill_path):
            # 跳过隐藏文件和临时目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zipf.write(file_path, arcname)

        # 添加元数据文件到zip
        meta_info = {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "version": version,
            "packaged_at": datetime.now().isoformat(),
            "files": []
        }

        # 记录打包的文件列表
        for root, dirs, files in os.walk(skill_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__']]
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_path)
                    meta_info["files"].append(arcname)

        # 添加清单文件
        zipf.writestr("manifest.json", json.dumps(meta_info, indent=2, ensure_ascii=False))

    # 清理临时目录
    shutil.rmtree(temp_dir)

    return output_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Package skill into .skill file')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('--output', '-o', help='Output directory', default=None)
    args = parser.parse_args()

    if not os.path.exists(args.skill_path):
        print(f"Error: Skill path not found: {args.skill_path}")
        exit(1)

    if not os.path.exists(os.path.join(args.skill_path, "SKILL.md")):
        print(f"Error: SKILL.md not found in {args.skill_path}")
        exit(1)

    output_file = package_skill(args.skill_path, args.output)
    print(f"Successfully packaged skill to: {output_file}")


if __name__ == "__main__":
    main()
