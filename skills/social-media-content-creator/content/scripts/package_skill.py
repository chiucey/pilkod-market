#!/usr/bin/env python3
"""
技能打包脚本 - 将技能目录打包为 .skill 文件
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path


def get_skill_meta(skill_dir: Path) -> dict:
    """读取技能元数据"""
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text(encoding="utf-8"))
    return {}


def should_include(path: Path) -> bool:
    """判断文件是否应该包含在包中"""
    # 排除规则
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "node_modules",
        ".venv",
        "venv",
        # 敏感文件
        "*.pem",
        "*.key",
        ".env",
        "secrets",
        "credentials",
    ]

    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern.startswith("*."):
            ext = pattern[1:]
            if path_str.endswith(ext):
                return False
        elif pattern in path_str:
            return False

    return True


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """
    将技能目录打包为 .skill 文件

    Returns:
        生成的 .skill 文件路径
    """
    skill_dir = skill_dir.resolve()
    skill_name = skill_dir.name

    if not skill_dir.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_dir}")

    # 读取元数据
    meta = get_skill_meta(skill_dir)
    skill_id = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_dir.parent

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建临时目录用于构建包
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 复制文件（排除不应包含的文件）
        for item in skill_dir.rglob("*"):
            if item.is_file() and should_include(item):
                relative_path = item.relative_to(skill_dir)
                dest_path = temp_path / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)

        # 创建 ZIP 包
        with zipfile.ZipFile(
            output_file, "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            for item in temp_path.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(temp_path)
                    zipf.write(item, arcname)

    return output_file


def list_package_contents(skill_file: Path) -> list:
    """列出包内容"""
    contents = []
    with zipfile.ZipFile(skill_file, "r") as zipf:
        for info in zipf.infolist():
            if not info.filename.endswith("/"):  # 排除目录
                contents.append(info.filename)
    return sorted(contents)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_dir = Path.cwd()
    else:
        skill_dir = Path(sys.argv[1])

    print(f"打包技能目录: {skill_dir}")
    print("=" * 50)

    try:
        # 打包
        print("\n正在打包...")
        output_file = package_skill(skill_dir)
        print(f"✓ 打包完成: {output_file}")

        # 显示包内容
        print("\n包内容:")
        contents = list_package_contents(output_file)
        for item in contents:
            print(f"  - {item}")

        # 显示文件大小
        size = output_file.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        print(f"\n文件大小: {size_str}")

        print("\n" + "=" * 50)
        print("✓ 打包成功！")
        print(f"\n输出文件: {output_file}")

        return 0

    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
