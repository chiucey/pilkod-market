#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import json
import os
import sys
import tarfile
from datetime import datetime
from pathlib import Path


def create_skill_package(skill_path: Path, output_dir: Path = None) -> Path:
    """创建技能包"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能路径不存在: {skill_path}")

    # 读取元数据
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json 不存在")

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    skill_name = meta.get("name", skill_path.name)
    skill_version = meta.get("version", "1.0.0")

    # 创建输出目录
    if output_dir is None:
        output_dir = skill_path.parent / "dist"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_{skill_version}_{timestamp}.skill"

    # 创建 tar.gz 包
    with tarfile.open(output_file, "w:gz") as tar:
        # 添加所有文件（排除 .git, __pycache__ 等）
        for root, dirs, files in os.walk(skill_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "node_modules", ".venv", "dist"]]

            for file in files:
                file_path = Path(root) / file
                # 排除构建产物和敏感文件
                if file.endswith((".pyc", ".pyo", ".so", ".pyd")):
                    continue
                if file.startswith("."):
                    continue

                # 计算相对路径
                arcname = file_path.relative_to(skill_path)
                tar.add(file_path, arcname=arcname)

    print(f"✓ 技能包已创建: {output_file}")
    print(f"  大小: {output_file.stat().st_size / 1024:.2f} KB")

    return output_file


def verify_package(package_path: Path) -> bool:
    """验证包内容"""
    print("\n验证包内容...")

    with tarfile.open(package_path, "r:gz") as tar:
        members = tar.getmembers()

        # 必须包含的文件
        required_files = ["SKILL.md", "_meta.json"]
        found_files = [m.name for m in members]

        for req in required_files:
            if req not in found_files:
                print(f"✗ 缺少必需文件: {req}")
                return False
            print(f"✓ 包含: {req}")

        # 显示所有文件
        print(f"\n共 {len(members)} 个文件:")
        for m in members:
            print(f"  - {m.name}")

    return True


def main():
    """主函数"""
    # 默认打包当前目录下的技能
    skill_path = Path(__file__).parent.parent

    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])

    print(f"打包技能: {skill_path}")
    print("=" * 50)

    try:
        # 创建包
        output_file = create_skill_package(skill_path)

        # 验证
        if verify_package(output_file):
            print("\n" + "=" * 50)
            print("✓ 打包成功!")
            print(f"输出文件: {output_file}")
            return 0
        else:
            print("\n✗ 包验证失败")
            return 1

    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
