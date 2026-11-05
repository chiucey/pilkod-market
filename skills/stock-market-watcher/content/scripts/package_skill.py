"""
技能打包脚本
将股票看盘技能打包为可发布的 .skill 文件
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime


def validate_skill_structure(skill_path: str) -> tuple[bool, list]:
    """
    验证技能目录结构

    Args:
        skill_path: 技能根目录路径

    Returns:
        (是否有效, 错误列表)
    """
    errors = []

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        file_path = os.path.join(skill_path, f)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {f}")

    # 检查 SKILL.md frontmatter
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 YAML frontmatter 开头")

            # 检查必需字段
            if 'name:' not in content:
                errors.append("SKILL.md frontmatter 缺少 name 字段")
            if 'description:' not in content:
                errors.append("SKILL.md frontmatter 缺少 description 字段")

    # 检查 _meta.json
    meta_json = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_json):
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """
    打包技能

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录，默认为 skill_path 的父目录

    Returns:
        打包文件路径
    """
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)

    # 验证结构
    valid, errors = validate_skill_structure(skill_path)
    if not valid:
        raise ValueError(f"技能结构验证失败:\n" + "\n".join(errors))

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除空目录和隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)

                # 排除打包产物本身
                if os.path.abspath(file_path) != os.path.abspath(output_file):
                    zf.write(file_path, arcname)

    return output_file


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"打包技能: {skill_path}")

    # 验证
    valid, errors = validate_skill_structure(skill_path)
    if not valid:
        print("验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("结构验证通过")

    # 打包
    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"打包成功: {output_file}")
    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
