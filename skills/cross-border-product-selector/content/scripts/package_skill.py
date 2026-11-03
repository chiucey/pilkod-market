#!/usr/bin/env python3
"""
跨境电商选品技能 - 打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_skill_metadata(skill_path):
    """获取技能元数据"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return None

    try:
        return json.loads(meta_file.read_text(encoding='utf-8'))
    except:
        return None

def scan_files(skill_path, exclude_patterns=None):
    """扫描技能目录中的所有文件"""
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__',
            '.pyc',
            '.git',
            '.DS_Store',
            'Thumbs.db',
            '*.log',
            '.env'
        ]

    files = []
    for item in skill_path.rglob('*'):
        if item.is_file():
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith('*.'):
                    if item.suffix == pattern[1:]:
                        should_exclude = True
                        break
                else:
                    if pattern in str(item):
                        should_exclude = True
                        break

            if not should_exclude:
                rel_path = item.relative_to(skill_path)
                files.append((str(rel_path), item))

    return files

def create_skill_package(skill_path, output_dir=None):
    """创建技能安装包"""
    skill_path = Path(skill_path)

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"错误: 技能路径不存在: {skill_path}")
        return False

    # 获取元数据
    metadata = get_skill_metadata(skill_path)
    if not metadata:
        print("错误: 无法读取技能元数据 (_meta.json)")
        return False

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)

    # 创建包文件名
    skill_name = metadata.get('name', skill_path.name)
    version = metadata.get('version', '1.0.0')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}_v{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 扫描文件
    files = scan_files(skill_path)

    if not files:
        print("错误: 技能目录为空")
        return False

    # 创建ZIP包
    try:
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for rel_path, abs_path in files:
                zf.write(abs_path, rel_path)

        print(f"✓ 技能包创建成功: {package_path}")
        print(f"  - 技能名称: {skill_name}")
        print(f"  - 版本: {version}")
        print(f"  - 文件数量: {len(files)}")

        return str(package_path)

    except Exception as e:
        print(f"错误: 创建包失败: {e}")
        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='打包技能为 .skill 文件')
    parser.add_argument('skill_path', nargs='?', default=None,
                        help='技能目录路径（默认当前目录）')
    parser.add_argument('-o', '--output', default=None,
                        help='输出目录')

    args = parser.parse_args()

    skill_path = Path(args.skill_path) if args.skill_path else Path(__file__).parent.parent

    print(f"正在打包技能: {skill_path.name}")
    print("=" * 50)

    result = create_skill_package(skill_path, args.output)

    if result:
        print("=" * 50)
        print(f"\n打包完成！")
        print(f"包文件路径: {result}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
