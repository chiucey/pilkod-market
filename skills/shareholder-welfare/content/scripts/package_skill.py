#!/usr/bin/env python3
"""
技能打包脚本
将 shareholder-welfare 技能打包为 .skill 文件
"""

import argparse
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path


class PackageResult:
    """打包结果容器"""
    def __init__(self):
        self.success = False
        self.output_path = None
        self.warnings = []
        self.errors = []
        self.included_files = []

    def add_warning(self, message):
        self.warnings.append(message)

    def add_error(self, message):
        self.errors.append(message)

    def print_report(self):
        """打印打包报告"""
        print("=" * 60)
        print("技能打包报告")
        print("=" * 60)

        if self.success:
            print(f"\n✅ 打包成功!")
            print(f"   输出文件: {self.output_path}")
        else:
            print(f"\n❌ 打包失败!")

        if self.included_files:
            print(f"\n📦 包含文件 ({len(self.included_files)}):")
            for f in self.included_files:
                print(f"   - {f}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"   ⚡ {msg}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for msg in self.errors:
                print(f"   ✗ {msg}")

        print("=" * 60)


def scan_skill_directory(skill_dir: Path) -> list:
    """
    扫描技能目录，收集所有需要打包的文件

    Args:
        skill_dir: 技能目录路径

    Returns:
        list: 需要打包的文件列表
    """
    files = []

    # 需要包含的文件和目录
    include_patterns = [
        "SKILL.md",
        "_meta.json",
        "scripts/",
        "references/",
        "assets/"
    ]

    # 排除的文件和目录
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".DS_Store",
        "*.log",
        "tmp/",
        "temp/",
        ".venv",
        "node_modules"
    ]

    for item in skill_dir.rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(skill_dir)

            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.endswith("/"):
                    # 目录排除
                    if pattern.rstrip("/") in str(relative_path).split("/"):
                        should_exclude = True
                        break
                else:
                    # 文件排除
                    if pattern in str(relative_path):
                        should_exclude = True
                        break

            if not should_exclude:
                files.append(relative_path)

    return sorted(files)


def validate_before_packaging(skill_dir: Path) -> PackageResult:
    """
    打包前的验证检查

    Args:
        skill_dir: 技能目录路径

    Returns:
        PackageResult: 验证结果
    """
    result = PackageResult()

    # 检查目录是否存在
    if not skill_dir.exists():
        result.add_error(f"技能目录不存在: {skill_dir}")
        return result

    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        file_path = skill_dir / filename
        if not file_path.exists():
            result.add_error(f"缺少必需文件: {filename}")

    # 检查 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            result.add_error("SKILL.md 必须以 frontmatter 开头")

        # 检查必需字段
        if not re.search(r"^name:", content, re.MULTILINE):
            result.add_error("SKILL.md 缺少 name 字段")

        if not re.search(r"^description:", content, re.MULTILINE):
            result.add_error("SKILL.md 缺少 description 字段")

    # 检查 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        try:
            with open(meta_json, "r", encoding="utf-8") as f:
                meta = json.load(f)

            if "id" not in meta:
                result.add_error("_meta.json 缺少 id 字段")

            if "version" not in meta:
                result.add_error("_meta.json 缺少 version 字段")

        except json.JSONDecodeError as e:
            result.add_error(f"_meta.json 格式错误: {e}")

    # 检查是否有 secrets 或敏感文件
    sensitive_patterns = [".env", ".pem", ".key", "credentials", "secret"]
    for pattern in sensitive_patterns:
        for item in skill_dir.rglob("*"):
            if pattern in item.name.lower():
                result.add_warning(f"发现可能的敏感文件: {item.relative_to(skill_dir)}")

    return result


def create_package(skill_dir: Path, output_path: Path, compression: str = "gz") -> PackageResult:
    """
    创建技能包

    Args:
        skill_dir: 技能目录路径
        output_path: 输出文件路径
        compression: 压缩方式 ("gz", "bz2", "xz", 或 "")

    Returns:
        PackageResult: 打包结果
    """
    result = PackageResult()

    # 扫描文件
    files = scan_skill_directory(skill_dir)
    result.included_files = [str(f) for f in files]

    if not files:
        result.add_error("没有找到需要打包的文件")
        return result

    # 创建临时目录用于构建包
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建 skill 内部目录结构
        skill_name = skill_dir.name
        package_root = temp_path / skill_name

        # 复制文件到临时目录
        for file_path in files:
            dest_path = package_root / file_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            source = skill_dir / file_path
            if source.is_file():
                shutil.copy2(source, dest_path)

        # 读取 _meta.json 获取版本信息
        meta_path = package_root / "_meta.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            version = meta.get("version", "1.0.0")
        else:
            version = "1.0.0"

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = f"{skill_name}_v{version}_{timestamp}.skill"

        if output_path is None:
            output_path = Path(default_output)
        elif output_path.is_dir():
            output_path = output_path / default_output

        # 创建 tar.gz 包
        try:
            # 确定压缩模式
            mode_map = {
                "gz": "w:gz",
                "bz2": "w:bz2",
                "xz": "w:xz",
                "": "w",
                None: "w:gz"
            }
            mode = mode_map.get(compression, "w:gz")

            with tarfile.open(output_path, mode) as tar:
                tar.add(package_root, arcname=skill_name)

            result.success = True
            result.output_path = str(output_path.resolve())

        except Exception as e:
            result.add_error(f"创建包时出错: {e}")

    return result


def package(skill_path: str, output_path: str = None, compression: str = "gz") -> bool:
    """
    打包技能

    Args:
        skill_path: 技能目录路径
        output_path: 输出文件路径（可选）
        compression: 压缩方式

    Returns:
        bool: 是否成功
    """
    skill_dir = Path(skill_path).resolve()

    print(f"\n打包技能: {skill_dir}")
    print(f"压缩方式: {compression or 'gz'}")

    # 打包前验证
    print("\n执行打包前验证...")
    validation_result = validate_before_packaging(skill_dir)

    if validation_result.errors:
        validation_result.success = False
        validation_result.print_report()
        return False

    # 创建包
    print("\n创建技能包...")
    output = Path(output_path) if output_path else None
    result = create_package(skill_dir, output, compression)
    result.print_report()

    return result.success


def extract_package(package_path: str, output_dir: str = None) -> bool:
    """
    解压技能包

    Args:
        package_path: 包文件路径
        output_dir: 输出目录（可选）

    Returns:
        bool: 是否成功
    """
    package_file = Path(package_path)
    output = Path(output_dir) if output_dir else Path(".")

    if not package_file.exists():
        print(f"错误: 包文件不存在: {package_path}")
        return False

    try:
        with tarfile.open(package_file, "r:*") as tar:
            # 验证包内容
            members = tar.getmembers()
            if not members:
                print("错误: 包文件为空")
                return False

            # 解压到输出目录
            tar.extractall(output)
            print(f"✅ 解压成功: {output / members[0].name}")

        return True

    except Exception as e:
        print(f"错误: 解压失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="打包或解压技能")
    parser.add_argument(
        "action",
        choices=["pack", "extract"],
        help="操作: pack (打包) 或 extract (解压)"
    )
    parser.add_argument(
        "path",
        help="技能目录路径（pack）或包文件路径（extract）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出路径"
    )
    parser.add_argument(
        "-c", "--compression",
        choices=["gz", "bz2", "xz", ""],
        default="gz",
        help="压缩方式（默认 gz）"
    )

    args = parser.parse_args()

    if args.action == "pack":
        success = package(args.path, args.output, args.compression)
    else:
        success = extract_package(args.path, args.output)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
