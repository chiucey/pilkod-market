#!/usr/bin/env python3
"""
A股短线选股系统 - 技能打包脚本
将技能目录打包为可分发的.skill文件
"""

import os
import zipfile
import json
import sys
from datetime import datetime

def get_skill_meta(skill_path):
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def package_skill(skill_path, output_dir=None):
    """打包技能为.skill文件"""
    skill_name = os.path.basename(skill_path)
    meta = get_skill_meta(skill_path)

    if not meta:
        print("✗ 未能读取技能元数据")
        return False

    # 确定输出路径
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # 生成输出文件名
    version = meta.get('version', '1.0.0')
    output_file = os.path.join(output_dir, f"{skill_name}_v{version}.skill")

    print(f"正在打包技能: {skill_name}")
    print(f"版本: {version}")
    print(f"输出: {output_file}")

    # 创建zip文件
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_path):
                # 跳过scripts目录（可选）
                dirs[:] = [d for d in dirs if d != '__pycache__']

                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_path)
                    zf.write(file_path, arcname)

        print(f"✓ 打包成功: {output_file}")
        return True
    except Exception as e:
        print(f"✗ 打包失败: {e}")
        return False

def main():
    # 获取技能路径
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    success = package_skill(skill_path, output_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
