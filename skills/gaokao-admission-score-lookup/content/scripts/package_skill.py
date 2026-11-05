#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考录取分数线查询技能打包脚本

将技能打包为可分发的 .skill 文件，便于发布和共享。
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_skill_meta(skill_dir: str) -> dict:
    """读取技能元数据"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"元数据文件不存在: {meta_path}")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill_structure(skill_dir: str) -> tuple:
    """验证技能目录结构

    Returns:
        (是否有效, 错误列表, 警告列表)
    """
    errors = []
    warnings = []

    required_files = ['SKILL.md', '_meta.json']
    required_dirs = ['references']

    # 检查必需文件
    for filename in required_files:
        filepath = os.path.join(skill_dir, filename)
        if not os.path.exists(filepath):
            errors.append(f"缺少必需文件: {filename}")

    # 检查必需目录
    for dirname in required_dirs:
        dirpath = os.path.join(skill_dir, dirname)
        if not os.path.exists(dirpath):
            warnings.append(f"建议包含目录: {dirname}")

    # 检查 scripts 目录
    scripts_dir = os.path.join(skill_dir, 'scripts')
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith('.py'):
                warnings.append(f"发现Python脚本: {filename} (可能需要权限设置)")

    # 验证 _meta.json
    try:
        meta = get_skill_meta(skill_dir)
        required_meta_fields = ['id', 'version', 'name']
        for field in required_meta_fields:
            if field not in meta:
                errors.append(f"元数据缺少必需字段: {field}")
    except Exception as e:
        errors.append(f"元数据文件格式错误: {str(e)}")

    # 检查 SKILL.md frontmatter
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")

        # 检查 frontmatter 包含 name 和 description
        if 'name:' not in content[:500]:
            warnings.append("SKILL.md frontmatter 建议包含 name 字段")
        if 'description:' not in content[:500]:
            warnings.append("SKILL.md frontmatter 建议包含 description 字段")

    return len(errors) == 0, errors, warnings


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件

    Args:
        skill_dir: 技能目录路径
        output_dir: 输出目录路径（默认与技能目录相同）

    Returns:
        打包后的文件路径
    """
    skill_dir = os.path.abspath(skill_dir)
    skill_name = os.path.basename(skill_dir)

    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)
    output_dir = os.path.abspath(output_dir)

    # 验证结构
    is_valid, errors, warnings = validate_skill_structure(skill_dir)
    if errors:
        print("验证失败，发现以下错误:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("技能目录结构验证失败")

    if warnings:
        print("验证警告:")
        for warning in warnings:
            print(f"  - {warning}")

    # 获取元数据
    meta = get_skill_meta(skill_dir)
    version = meta.get('version', '1.0.0')

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{skill_name}_v{version}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建 zip 压缩包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)

                # 跳过 .skill 输出文件本身
                if arcname.endswith('.skill'):
                    continue

                zipf.write(file_path, arcname)
                print(f"  添加: {arcname}")

    print(f"\n打包完成: {output_path}")
    print(f"技能名称: {skill_name}")
    print(f"技能版本: {version}")
    print(f"技能ID: {meta.get('id', 'N/A')}")

    return output_path


def list_skill_contents(skill_dir: str):
    """列出技能目录内容"""
    print(f"\n技能目录: {skill_dir}")
    print("=" * 50)

    for root, dirs, files in os.walk(skill_dir):
        # 排除隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        level = root.replace(skill_dir, '').count(os.sep)
        indent = ' ' * 2 * level

        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)

        for file in sorted(files):
            if not file.startswith('.'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({file_size} bytes)")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='高考录取分数线查询技能打包工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'skill_dir',
        nargs='?',
        default='.',
        help='技能目录路径（默认当前目录）'
    )

    parser.add_argument(
        '--output', '-o',
        help='输出目录路径'
    )

    parser.add_argument(
        '--validate-only', '-v',
        action='store_true',
        help='仅验证，不打包'
    )

    args = parser.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在: {skill_dir}")
        return 1

    # 列出目录内容
    list_skill_contents(skill_dir)

    # 验证结构
    print("\n验证技能结构...")
    is_valid, errors, warnings = validate_skill_structure(skill_dir)

    if errors:
        print("\n❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️ 验证警告:")
        for warning in warnings:
            print(f"  - {warning}")

    if is_valid:
        print("\n✅ 验证通过")

    if not args.validate_only and is_valid:
        print("\n开始打包...")
        try:
            output_path = package_skill(skill_dir, args.output)
            print("\n" + "=" * 50)
            print("打包成功！")
            print(f"输出文件: {output_path}")
            return 0
        except Exception as e:
            print(f"\n打包失败: {str(e)}")
            return 1

    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())
