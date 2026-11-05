#!/usr/bin/env python3
"""
Auto-RedNote 技能打包脚本

将技能文件夹打包为 .skill 文件，用于发布和分发
"""

import argparse
import json
import os
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_path: str) -> bool:
    """验证技能结构是否完整"""
    skill_path = Path(skill_path)

    # 检查必需文件
    required_files = [
        "SKILL.md",
        "_meta.json",
    ]

    for file in required_files:
        file_path = skill_path / file
        if not file_path.exists():
            print(f"错误: 缺少必需文件 {file}")
            return False

    # 检查 _meta.json 内容
    with open(skill_path / "_meta.json", "r") as f:
        meta = json.load(f)
        if "id" not in meta or "version" not in meta:
            print("错误: _meta.json 必须包含 id 和 version 字段")
            return False

    # 检查 SKILL.md frontmatter
    with open(skill_path / "SKILL.md", "r") as f:
        content = f.read()
        if not content.startswith("---"):
            print("错误: SKILL.md 必须以 YAML frontmatter 开头")
            return False

    print("技能验证通过 ✓")
    return True


def get_safe_path(path: str, base_path: Path) -> Path:
    """确保路径安全，不会逃逸到 base_path 之外"""
    resolved = (base_path / path).resolve()
    if not str(resolved).startswith(str(base_path.resolve())):
        raise ValueError(f"路径 {path} 不安全，逃逸到了目标目录之外")
    return resolved


def package_skill(skill_path: str, output_path: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 读取元数据
    with open(skill_path / "_meta.json", "r") as f:
        meta = json.load(f)

    # 生成输出文件名
    if output_path is None:
        output_path = f"{skill_name}_{meta['version']}.skill"
    else:
        output_path = Path(output_path)

    # 如果是目录，生成文件名
    if output_path.is_dir():
        output_path = output_path / f"{skill_name}_{meta['version']}.skill"

    # 创建打包目录（排除 .git 等）
    build_dir = Path("build_package")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()

    # 收集要打包的文件
    exclude_patterns = {".git", "__pycache__", ".DS_Store", "Thumbs.db", "*.pyc"}
    files_to_package = []

    for root, dirs, files in os.walk(skill_path):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns]

        rel_root = Path(root).relative_to(skill_path)

        for file in files:
            if file in exclude_patterns or file.startswith("."):
                continue

            src = Path(root) / file
            dst = build_dir / rel_root / file

            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(src, dst)
            files_to_package.append(str(rel_root / file))

    # 创建 zip 文件
    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_package:
            file_path = build_dir / file
            zipf.write(file_path, Path(skill_name) / file)

    # 清理打包目录
    shutil.rmtree(build_dir)

    print(f"打包完成: {output_path}")
    print(f"技能名称: {skill_name}")
    print(f"技能版本: {meta['version']}")
    print(f"文件数量: {len(files_to_package)}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Auto-RedNote 技能打包脚本")
    parser.add_argument("skill_path", help="技能文件夹路径", default=".")
    parser.add_argument("-o", "--output", help="输出 .skill 文件路径")
    parser.add_argument("--validate-only", action="store_true", help="仅验证，不打包")

    args = parser.parse_args()

    # 验证技能
    if not validate_skill(args.skill_path):
        exit(1)

    if args.validate_only:
        print("验证完成")
        return

    # 打包技能
    output = package_skill(args.skill_path, args.output)
    print(f"\n技能文件已生成: {output}")


if __name__ == "__main__":
    main()
