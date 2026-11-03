#!/usr/bin/env python3
"""
AutoLearn&Refine_Claw 技能打包脚本
生成 .skill 分发文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def scan_directory(root_path: Path, exclude_patterns: set) -> list[tuple[Path, str]]:
    """扫描目录，生成文件列表"""
    files = []
    for item in root_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(root_path)
            # 检查是否在排除列表中
            if any(str(rel_path).startswith(p) for p in exclude_patterns):
                continue
            # 转换为 zip 内部路径
            zip_path = str(rel_path).replace(os.sep, "/")
            files.append((item, zip_path))
    return sorted(files, key=lambda x: x[1])


def package_skill(skill_path: str, output_dir: str = "./dist"):
    """打包技能"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取 meta
    meta_file = skill_path / "_meta.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    skill_name = meta.get("name", skill_path.name)
    output_file = output_dir / f"{skill_name}_{meta['version']}_{timestamp}.skill"

    # 扫描文件
    exclude_patterns = {"__pycache__", ".git", "node_modules", ".venv", "dist"}
    files = scan_directory(skill_path, exclude_patterns)

    print(f"打包技能: {skill_name}")
    print(f"版本: {meta['version']}")
    print(f"文件数: {len(files)}")
    print("-" * 50)

    # 创建 zip
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, zip_path in files:
            zf.write(file_path, zip_path)
            print(f"  + {zip_path}")

    print("-" * 50)
    print(f"打包完成: {output_file}")
    return str(output_file)


def main():
    skill_path = os.environ.get("SKILL_PATH", "/workspace/temp-skills/auto-learn-refine-claw")
    output_dir = os.environ.get("OUTPUT_DIR", "./dist")

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n✓ 打包成功: {output_file}")
        return 0
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
