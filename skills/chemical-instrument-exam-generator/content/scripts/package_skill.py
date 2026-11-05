#!/usr/bin/env python3
"""
化工仪表培训出题技能 - 打包脚本
将技能打包为 .skill 文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_meta_info(skill_dir):
    """获取技能元数据"""
    meta_path = skill_dir / '_meta.json'
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json 不存在")

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    return meta


def create_package(skill_dir, output_dir=None):
    """创建技能包"""
    skill_dir = Path(skill_dir)

    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)

    # 获取元数据
    meta = get_meta_info(skill_dir)
    skill_name = meta.get('name', 'unnamed-skill')
    version = meta.get('version', '1.0.0')

    # 生成包名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}_v{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 创建 zip 包
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)

                # 检查文件安全性（防止符号链接逃逸）
                if file_path.is_symlink():
                    print(f"  ⚠️  跳过符号链接: {file_path}")
                    continue

                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print()
    print(f"✅ 技能包已创建: {package_path}")
    print(f"   大小: {package_path.stat().st_size / 1024:.2f} KB")

    return package_path


def extract_package(package_path, output_dir=None):
    """解压技能包"""
    package_path = Path(package_path)

    if not package_path.exists():
        raise FileNotFoundError(f"技能包不存在: {package_path}")

    # 确定输出目录
    if output_dir is None:
        output_dir = package_path.parent / package_path.stem
    else:
        output_dir = Path(output_dir)

    # 解压
    with zipfile.ZipFile(package_path, 'r') as zf:
        # 安全检查
        for name in zf.namelist():
            if name.startswith('/') or '..' in name:
                raise ValueError(f"不安全的文件路径: {name}")

        zf.extractall(output_dir)

    print(f"✅ 技能包已解压到: {output_dir}")
    return output_dir


def main():
    import argparse

    parser = argparse.ArgumentParser(description='化工仪表培训出题技能 - 打包工具')
    parser.add_argument('action', choices=['pack', 'extract'],
                        help='操作: pack=打包, extract=解压')
    parser.add_argument('path', nargs='?', default=None,
                        help='技能目录路径（pack）或技能包路径（extract）')
    parser.add_argument('-o', '--output', default=None,
                        help='输出目录')

    args = parser.parse_args()

    # 确定路径
    if args.path is None:
        script_dir = Path(__file__).parent
        skill_dir = script_dir.parent
    else:
        skill_dir = Path(args.path)

    print("=" * 60)
    print("化工仪表培训出题技能 - 打包工具")
    print("=" * 60)
    print()

    if args.action == 'pack':
        if not skill_dir.is_dir():
            print(f"❌ 技能目录不存在: {skill_dir}")
            return

        print(f"技能目录: {skill_dir}")
        print("打包文件:")
        create_package(skill_dir, args.output)

    elif args.action == 'extract':
        package_path = skill_dir
        if not package_path.exists():
            print(f"❌ 技能包不存在: {package_path}")
            return

        print(f"技能包: {package_path}")
        extract_package(package_path, args.output)


if __name__ == '__main__':
    main()
