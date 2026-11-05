#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_safe_files(skill_dir: Path) -> list:
    """获取需要打包的安全文件列表"""
    safe_patterns = [
        'SKILL.md',
        '_meta.json',
        '*.py',
        '*.json',
        '*.md',
        '*.txt',
        '*.csv',
        '*.yaml',
        '*.yml',
    ]

    exclude_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
    exclude_files = {'.DS_Store', 'Thumbs.db'}

    files_to_package = []

    for root, dirs, files in os.walk(skill_dir):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # 处理文件
        for file in files:
            if file in exclude_files:
                continue

            # 检查扩展名
            file_path = Path(root) / file
            if file_path.suffix in ['.py', '.json', '.md', '.txt', '.csv', '.yaml', '.yml']:
                rel_path = file_path.relative_to(skill_dir)
                files_to_package.append(rel_path)

            # 包含顶层的非隐藏文件
            elif file_path.parent == skill_dir and not file.startswith('.'):
                rel_path = file_path.relative_to(skill_dir)
                files_to_package.append(rel_path)

    return files_to_package


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """
    打包技能为 .skill 文件
    返回打包后的文件路径
    """
    skill_path = Path(skill_dir).resolve()
    skill_name = skill_path.name

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    # 读取 meta 信息
    meta_path = skill_path / '_meta.json'
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        version = meta.get('version', '1.0.0')
    else:
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_name = f"{skill_name}_v{version}_{timestamp}.skill"

    if output_dir:
        output_path = Path(output_dir) / output_name
    else:
        output_path = skill_path.parent / output_name

    # 创建打包目录
    package_dir = skill_path.parent / f'_temp_package_{timestamp}'
    package_dir.mkdir(exist_ok=True)

    try:
        # 获取文件列表
        files_to_package = get_safe_files(skill_path)

        print(f"打包文件列表 ({len(files_to_package)} 个文件):")
        for f in files_to_package:
            print(f"  - {f}")

        # 复制文件到临时目录
        for rel_path in files_to_package:
            src = skill_path / rel_path
            dst = package_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        # 创建 zip 压缩包
        output_path_str = str(output_path)
        with zipfile.ZipFile(output_path_str, 'w', zipfile.ZIP_DEFLATED) as zf:
            for rel_path in files_to_package:
                file_path = package_dir / rel_path
                zf.write(file_path, rel_path)

        print(f"\n✓ 打包完成: {output_path}")
        return str(output_path)

    finally:
        # 清理临时目录
        if package_dir.exists():
            shutil.rmtree(package_dir)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='打包技能为 .skill 文件')
    parser.add_argument('skill_path', help='技能目录路径')
    parser.add_argument('--output', '-o', help='输出目录 (默认与技能目录同级)')

    args = parser.parse_args()

    try:
        output_path = package_skill(args.skill_path, args.output)
        print(f"\n技能已打包为: {output_path}")
        return 0
    except Exception as e:
        print(f"\n✗ 打包失败: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
