#!/usr/bin/env python3
"""
打包技能脚本 - 创建 .skill 文件
"""
import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


def get_files_to_package(skill_dir: str) -> list[str]:
    """获取需要打包的文件，排除临时文件和敏感文件"""
    exclude_patterns = [
        '__pycache__',
        '.DS_Store',
        '.git',
        '.gitignore',
        '*.pyc',
        '.pytest_cache',
        'node_modules',
    ]

    files_to_include = []
    skill_path = Path(skill_dir)

    for file_path in skill_path.rglob('*'):
        if file_path.is_file():
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(file_path):
                    should_exclude = True
                    break

            if not should_exclude:
                files_to_include.append(str(file_path))

    return files_to_include


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 读取 meta 信息
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_version = meta.get('version', '1.0.0')
        skill_id = meta.get('id', 'unknown')
    else:
        skill_version = 'unknown'
        skill_id = 'unknown'

    print(f"📦 打包技能: {skill_name}")
    print(f"   版本: {skill_version}")
    print(f"   ID: {skill_id}")

    # 获取要打包的文件
    files = get_files_to_package(skill_dir)
    print(f"   文件数: {len(files)}")

    # 创建 ZIP 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            # 计算在 skill 目录中的相对路径
            relative_path = Path(file_path).relative_to(skill_path)
            zf.write(file_path, relative_path)
            print(f"   + {relative_path}")

    print(f"\n✅ 打包完成: {output_file}")
    return str(output_file)


def main():
    if len(sys.argv) < 2:
        skill_dir = "/workspace/temp-skills/long-term-investment-analysis"
    else:
        skill_dir = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_dir, output_dir)
        print(f"\n📁 输出文件: {output_file}")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()