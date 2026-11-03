#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import os
import sys
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime


def get_skill_info(skill_path: str) -> dict:
    """读取技能元信息"""
    meta_json = Path(skill_path) / "_meta.json"
    if meta_json.exists():
        return json.loads(meta_json.read_text(encoding="utf-8"))
    return {"name": Path(skill_path).name, "version": "unknown"}


def should_include(file_path: str) -> bool:
    """判断文件是否应该打包"""
    # 排除的文件和目录
    exclude_patterns = [
        "__pycache__",
        ".git",
        ".DS_Store",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
    ]

    path = Path(file_path)
    name = path.name

    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return False
        elif pattern in str(path):
            return False

    return True


def create_skill_package(skill_path: str, output_dir: str = None) -> str:
    """创建技能包"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 获取技能信息
    skill_info = get_skill_info(str(skill_path))
    version = skill_info.get("version", "1.0.0")

    # 输出路径
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent

    output_file = output_path / f"{skill_name}-{version}.skill"

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 复制文件
        for root, dirs, files in os.walk(skill_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if should_include(d)]

            for file in files:
                if not should_include(file):
                    continue

                src = Path(root) / file
                rel_path = src.relative_to(skill_path)
                dst = temp_path / rel_path

                # 确保目标目录存在
                dst.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件
                dst.write_bytes(src.read_bytes())

        # 创建 zip 包
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in temp_path.rglob("*"):
                if file.is_file():
                    arcname = file.relative_to(temp_path)
                    zf.write(file, arcname)

    return str(output_file)


def main():
    """主打包流程"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 50)
    print("技能打包工具")
    print("=" * 50)
    print(f"技能路径: {skill_path}")
    if output_dir:
        print(f"输出目录: {output_dir}")
    print()

    try:
        output_file = create_skill_package(skill_path, output_dir)
        print("=" * 50)
        print(f"✅ 打包成功!")
        print(f"📦 输出文件: {output_file}")
        print("=" * 50)
    except Exception as e:
        print(f"❌ 打包失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
