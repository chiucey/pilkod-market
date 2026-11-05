#!/usr/bin/env python3
"""
技能打包脚本
将技能文件夹打包为 .skill 文件
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def calculate_file_hash(file_path: Path) -> str:
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """打包技能"""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)

    if not skill_path.exists():
        print(f"错误: 技能目录不存在: {skill_dir}")
        sys.exit(1)

    # 读取元数据
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        print("错误: _meta.json 不存在")
        sys.exit(1)

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get("id", skill_path.name)
    version = meta.get("version", "1.0.0")

    # 创建输出文件名
    output_file = output_path / f"{skill_id}-{version}.skill"

    # 创建 ZIP 包
    print(f"打包技能: {skill_path.name}")
    print(f"版本: {version}")
    print(f"输出: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 计算相对路径
                arcname = file_path.relative_to(skill_path)

                # 跳过敏感文件和临时文件
                parts_str = str(arcname)
                if any(part.startswith('.') for part in arcname.parts):
                    continue
                if '__pycache__' in parts_str or '.pyc' in parts_str or '.pyo' in parts_str:
                    continue

                # 添加文件
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    # 计算哈希
    file_hash = calculate_file_hash(output_file)

    print(f"\n✅ 打包完成!")
    print(f"文件: {output_file}")
    print(f"大小: {output_file.stat().st_size / 1024:.1f} KB")
    print(f"SHA256: {file_hash[:16]}...")

    # 生成 manifest
    manifest = {
        "skill_id": skill_id,
        "version": version,
        "name": meta.get("name", skill_path.name),
        "description": meta.get("description", ""),
        "author": meta.get("author", "Unknown"),
        "created_at": meta.get("created_at", datetime.now().isoformat()),
        "file": output_file.name,
        "hash": file_hash,
        "packaged_at": datetime.now().isoformat()
    }

    manifest_file = output_path / f"{skill_id}.manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"清单: {manifest_file}")

    return str(output_file)


def main():
    parser = argparse.ArgumentParser(description="打包技能为 .skill 文件")
    parser.add_argument("skill_path", help="技能目录路径")
    parser.add_argument("--output", "-o", default=".", help="输出目录")
    args = parser.parse_args()

    output_file = package_skill(args.skill_path, args.output)
    print(f"\n技能已打包: {output_file}")


if __name__ == "__main__":
    main()
