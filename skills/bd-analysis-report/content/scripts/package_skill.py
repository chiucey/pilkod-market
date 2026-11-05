#!/usr/bin/env python3
"""
BD分析报告技能 - 打包脚本

将技能打包为 .skill 文件，用于发布和分发。

输出：
- {skill-name}_{version}.skill: 可分发的技能包

排除项：
- .DS_Store, __pycache__, *.pyc
- build/, dist/, .git/
- 系统隐藏文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_skill_meta(skill_path: Path) -> dict:
    """从 SKILL.md 和 _meta.json 读取技能元数据"""
    meta_file = skill_path / "_meta.json"
    skill_md = skill_path / "SKILL.md"

    meta = {
        "name": skill_path.name,
        "version": "0.0.0",
        "description": ""
    }

    # 读取 _meta.json
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "version" in data:
                meta["version"] = data["version"]
        except Exception:
            pass

    # 从 SKILL.md frontmatter 读取 name 和 description
    if skill_md.exists():
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        import re
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
            desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
            if name_match:
                meta["name"] = name_match.group(1).strip()
            if desc_match:
                meta["description"] = desc_match.group(1).strip()

    return meta


def get_excluded_patterns() -> set:
    """返回应排除的文件/目录模式"""
    return {
        # macOS
        ".DS_Store",
        # Python
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "__pypackages__",
        # Version control
        ".git",
        ".svn",
        ".hg",
        # Build artifacts
        "build",
        "dist",
        "*.egg-info",
        # IDE
        ".vscode",
        ".idea",
        ".vs",
        # Test/Cache
        ".pytest_cache",
        ".tox",
        ".mypy_cache",
        ".ruff_cache",
        # Hidden files (except frontmatter files)
    }


def should_exclude(path: Path, base_path: Path) -> bool:
    """判断路径是否应被排除"""
    rel_path = path.relative_to(base_path) if path.is_relative_to(base_path) else path

    # 排除模式
    excluded = get_excluded_patterns()
    parts = str(rel_path).split(os.sep)

    for part in parts:
        if part in excluded:
            return True
        if part.startswith(".") and part not in [".", ".."]:
            # 排除隐藏文件/目录，但允许 . 开头但有意义的（如 frontmatter 变体）
            if not part.startswith("-"):
                return True

    return False


def collect_files(skill_path: Path) -> list[Path]:
    """收集应包含的文件列表"""
    files = []

    for root, dirs, filenames in os.walk(skill_path):
        root_path = Path(root)

        # 过滤目录
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d, skill_path)]

        for filename in filenames:
            file_path = root_path / filename
            if not should_exclude(file_path, skill_path):
                files.append(file_path)

    return files


def create_package(skill_path: str, output_dir: str = ".") -> str:
    """
    创建技能包

    Args:
        skill_path: 技能根目录
        output_dir: 输出目录（默认当前目录）

    Returns:
        生成的 .skill 文件路径
    """
    skill_path = Path(skill_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    if not skill_path.is_dir():
        raise ValueError(f"技能路径不是目录: {skill_path}")

    # 获取元数据
    meta = get_skill_meta(skill_path)
    skill_name = meta["name"]
    version = meta["version"]

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}_{version}.skill"

    # 收集文件
    files = collect_files(skill_path)

    print(f"=" * 60)
    print(f"打包技能: {skill_name} v{version}")
    print(f"=" * 60)
    print(f"源目录: {skill_path}")
    print(f"输出文件: {output_file}")
    print(f"\n包含文件 ({len(files)} 个):")

    # 创建 ZIP 包
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(files):
            arcname = file_path.relative_to(skill_path)
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

    # 计算包大小
    size_kb = output_file.stat().st_size / 1024
    print(f"\n✅ 打包完成")
    print(f"   文件: {output_file.name}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   文件数: {len(files)}")

    return str(output_file)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="打包技能为 .skill 文件")
    parser.add_argument("skill_path", nargs="?", default=".", help="技能目录路径")
    parser.add_argument("--output", "-o", default=".", help="输出目录")

    args = parser.parse_args()

    try:
        output_file = create_package(args.skill_path, args.output)
        print(f"\n打包文件: {output_file}")
    except Exception as e:
        print(f"❌ 打包失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
