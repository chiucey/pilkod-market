#!/usr/bin/env python3
"""
打包技能为 .skill 文件

用法: python package_skill.py <skill_path>
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


def get_skill_meta(skill_path: str) -> dict:
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_path):
        raise FileNotFoundError("_meta.json 文件不存在")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_skill_package(skill_path: str, output_dir: str = None) -> str:
    """
    创建技能包

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录，默认为当前目录

    Returns:
        生成的 .skill 文件路径
    """
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)

    # 读取元数据
    meta = get_skill_meta(skill_path)
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)
    output_dir = os.path.abspath(output_dir)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"{skill_name}_v{version}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建ZIP包
    print(f"正在打包技能: {skill_name}")
    print(f"版本: {version}")
    print(f"技能ID: {skill_id}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 排除临时文件和隐藏文件
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ 技能包已生成: {output_path}")
    return output_path


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path>")
        print("\n示例:")
        print("  python package_skill.py /workspace/temp-skills/ppt-translator")
        print("  python package_skill.py ./my-skill")
        sys.exit(1)

    skill_path = sys.argv[1]

    if not os.path.exists(skill_path):
        print(f"错误: 路径不存在 - {skill_path}")
        sys.exit(1)

    if not os.path.isdir(skill_path):
        print(f"错误: 路径不是目录 - {skill_path}")
        sys.exit(1)

    try:
        output_path = create_skill_package(skill_path)
        print(f"\n打包成功！")
    except Exception as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
