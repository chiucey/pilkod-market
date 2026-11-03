#!/usr/bin/env python3
"""
Skill 打包工具
将 Skill 目录打包成可分发的 .skill 文件
"""

import os
import json
import zipfile
import hashlib
from pathlib import Path
from typing import List, Set


def calculate_file_hash(file_path: Path) -> str:
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def should_exclude(path: str, exclude_patterns: Set[str]) -> bool:
    """检查路径是否应该排除"""
    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    return False


def get_package_size(filepath: str) -> int:
    """获取文件大小（人类可读）"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def package_skill(skill_dir: str, output_path: str = None) -> dict:
    """
    将 Skill 目录打包成 .skill 文件

    Args:
        skill_dir: Skill 目录路径
        output_path: 输出文件路径（可选）

    Returns:
        打包结果信息
    """
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    # 默认输出路径
    if output_path is None:
        output_path = f"{skill_name}.skill"

    # 验证必需文件
    required_files = ['SKILL.md', '_meta.json']
    for req in required_files:
        req_path = skill_path / req
        if not req_path.exists():
            raise FileNotFoundError(f"缺少必需文件: {req}")

    # 读取 meta
    with open(skill_path / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 排除模式
    exclude_patterns = {
        '.git', '.svn', '__pycache__', '.pytest_cache',
        'node_modules', '.venv', 'venv', '.DS_Store',
        '*.pyc', '*.pyo', '.env', '*.log', 'dist', 'build',
        '.tmp', '.temp'
    }

    # 创建包
    output = Path(output_path)
    if output.exists():
        output.unlink()

    file_hashes = []
    file_list = []

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(skill_path)

                if should_exclude(str(file_path), exclude_patterns):
                    continue

                # 计算哈希
                file_hash = calculate_file_hash(file_path)

                # 添加到 zip
                zf.write(file_path, str(rel_path))

                file_list.append({
                    "path": str(rel_path),
                    "size": file_path.stat().st_size,
                    "hash": file_hash
                })
                file_hashes.append(file_hash)

    # 生成包哈希
    package_hash = hashlib.sha256(''.join(file_hashes).encode()).hexdigest()

    result = {
        "package_path": str(output.resolve()),
        "package_name": skill_name,
        "version": meta.get('version', '1.0.0'),
        "skill_id": meta.get('id', 'unknown'),
        "file_count": len(file_list),
        "package_size": get_package_size(str(output)),
        "package_hash": package_hash,
        "files": file_list
    }

    return result


def extract_skill(skill_file: str, output_dir: str = None) -> dict:
    """
    解压 Skill 包文件

    Args:
        skill_file: .skill 文件路径
        output_dir: 输出目录（可选，默认在当前目录创建同名文件夹）

    Returns:
        解压结果信息
    """
    skill_path = Path(skill_file)

    if output_dir is None:
        output_dir = skill_path.stem

    output_path = Path(output_dir)

    # 读取包信息
    with zipfile.ZipFile(skill_path, 'r') as zf:
        zf.extractall(output_path)

    return {
        "extracted_to": str(output_path.resolve()),
        "file_count": len(list(output_path.rglob('*')))
    }


def verify_skill(skill_file: str) -> dict:
    """
    验证 Skill 包完整性

    Args:
        skill_file: .skill 文件路径

    Returns:
        验证结果
    """
    skill_path = Path(skill_file)

    if not skill_path.exists():
        return {"valid": False, "error": "文件不存在"}

    try:
        with zipfile.ZipFile(skill_path, 'r') as zf:
            # 检查必需文件
            namelist = zf.namelist()

            required = ['SKILL.md', '_meta.json']
            missing = [f for f in required if f not in namelist]

            if missing:
                return {"valid": False, "error": f"缺少必需文件: {', '.join(missing)}"}

            # 验证 JSON 格式
            meta_content = zf.read('_meta.json')
            meta = json.loads(meta_content)

            if 'id' not in meta or 'version' not in meta:
                return {"valid": False, "error": "_meta.json 缺少必填字段"}

            return {
                "valid": True,
                "name": meta.get('name', 'unknown'),
                "id": meta.get('id'),
                "version": meta.get('version'),
                "file_count": len(namelist)
            }

    except zipfile.BadZipFile:
        return {"valid": False, "error": "无效的 ZIP 格式"}
    except json.JSONDecodeError:
        return {"valid": False, "error": "_meta.json 格式错误"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Skill 打包工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # package 命令
    package_parser = subparsers.add_parser('package', help='打包 Skill')
    package_parser.add_argument('skill_dir', help='Skill 目录路径')
    package_parser.add_argument('-o', '--output', help='输出文件路径')

    # extract 命令
    extract_parser = subparsers.add_parser('extract', help='解压 Skill 包')
    extract_parser.add_argument('skill_file', help='.skill 文件路径')
    extract_parser.add_argument('-o', '--output', help='输出目录')

    # verify 命令
    verify_parser = subparsers.add_parser('verify', help='验证 Skill 包')
    verify_parser.add_argument('skill_file', help='.skill 文件路径')

    args = parser.parse_args()

    if args.command == 'package':
        result = package_skill(args.skill_dir, args.output)
        print(f"[OK] 打包成功!")
        print(f"   输出: {result['package_path']}")
        print(f"   文件数: {result['file_count']}")
        print(f"   大小: {result['package_size']}")
        print(f"   哈希: {result['package_hash'][:16]}...")

    elif args.command == 'extract':
        result = extract_skill(args.skill_file, args.output)
        print(f"[OK] 解压成功!")
        print(f"   目录: {result['extracted_to']}")
        print(f"   文件数: {result['file_count']}")

    elif args.command == 'verify':
        result = verify_skill(args.skill_file)
        if result['valid']:
            print(f"[OK] 验证通过")
            print(f"   名称: {result['name']}")
            print(f"   版本: {result['version']}")
            print(f"   文件数: {result['file_count']}")
        else:
            print(f"[ERROR] 验证失败: {result['error']}")
            return 1

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
