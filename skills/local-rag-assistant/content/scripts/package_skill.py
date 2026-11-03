# -*- coding: utf-8 -*-
"""
Skill打包脚本

将技能打包为可分发的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_info(skill_path: str) -> dict:
    """获取技能信息"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {}


def validate_for_packaging(skill_path: str) -> tuple:
    """验证技能是否可打包，返回(是否通过, 错误信息)"""
    required = ["SKILL.md", "_meta.json"]
    errors = []

    for filename in required:
        path = os.path.join(skill_path, filename)
        if not os.path.exists(path):
            errors.append(f"必需文件缺失: {filename}")

    # 检查meta.json
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能"""
    skill_name = os.path.basename(skill_path)

    # 验证
    valid, errors = validate_for_packaging(skill_path)
    if not valid:
        print("打包验证失败:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("技能验证失败，无法打包")

    # 获取信息
    meta = get_skill_info(skill_path)
    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"{skill_name}-{version}-{skill_id}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建zip文件
    print(f"正在打包技能: {skill_name}")
    print(f"版本: {version}")
    print(f"输出: {output_path}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ 打包完成: {output_filename}")

    # 同时输出到当前目录
    final_output = os.path.join(os.getcwd(), output_filename)
    shutil.copy(output_path, final_output)
    print(f"✓ 副本已保存: {final_output}")

    return final_output


def main():
    if len(sys.argv) < 2:
        # 默认打包当前目录下的skill
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print("=" * 60)
    print("Skill打包工具")
    print("=" * 60)
    print(f"技能路径: {skill_path}")
    print()

    try:
        output_path = package_skill(skill_path, output_dir)
        print()
        print("=" * 60)
        print(f"✓ 打包成功！")
        print(f"输出文件: {output_path}")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
