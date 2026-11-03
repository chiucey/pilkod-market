#!/usr/bin/env python3
"""
Aegis Studios 技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_version(skill_path: Path) -> str:
    """从 _meta.json 获取版本"""
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        return meta.get("version", "1.0.0")
    return "1.0.0"


def get_name(skill_path: Path) -> str:
    """获取技能名称"""
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        lines = content.split("\n")
        if lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                if line.startswith("name:"):
                    return line.split(":", 1)[1].strip()
    return skill_path.name


def scan_files(skill_path: Path) -> list[Path]:
    """扫描技能目录下的所有文件"""
    ignore_patterns = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".DS_Store",
        "*.log",
        ".env",
    ]

    files = []
    for item in skill_path.rglob("*"):
        if item.is_file():
            # 检查是否应该忽略
            should_ignore = False
            rel_path = item.relative_to(skill_path)
            for pattern in ignore_patterns:
                if pattern.startswith("*."):
                    ext = pattern[1:]
                    if str(rel_path).endswith(ext):
                        should_ignore = True
                        break
                elif pattern in str(rel_path):
                    should_ignore = True
                    break

            if not should_ignore:
                files.append(item)

    return files


def create_skill_package(skill_path: Path, output_dir: Path) -> Path:
    """创建技能包"""
    name = get_name(skill_path)
    version = get_version(skill_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    package_name = f"{name}-{version}-{timestamp}.skill"
    package_path = output_dir / package_name

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建 ZIP 包
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in scan_files(skill_path):
            arcname = file.relative_to(skill_path)
            zf.write(file, arcname)

    print(f"✓ 技能包已创建: {package_path}")
    print(f"  名称: {name}")
    print(f"  版本: {version}")
    print(f"  文件数: {len(scan_files(skill_path))}")

    return package_path


def main():
    # 获取技能路径
    script_path = Path(__file__).resolve()
    skill_path = script_path.parent.parent

    # 输出目录
    output_dir = skill_path.parent / "output"

    print("=" * 50)
    print("Aegis Studios 技能打包工具")
    print("=" * 50)
    print(f"\n技能路径: {skill_path}")
    print(f"输出目录: {output_dir}")

    try:
        package_path = create_skill_package(skill_path, output_dir)
        print("\n" + "=" * 50)
        print("✓ 打包成功!")
        print(f"包路径: {package_path}")
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
