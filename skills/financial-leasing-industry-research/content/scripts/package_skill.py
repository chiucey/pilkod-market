#!/usr/bin/env python3
"""
金融租赁产业研究技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def scan_directory(path: Path, exclude_patterns: list = None) -> list:
    """扫描目录下的文件，排除指定模式"""
    if exclude_patterns is None:
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            ".DS_Store",
            "*.egg-info",
            ".pytest_cache",
        ]

    files = []
    for item in path.rglob("*"):
        if item.is_file():
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith("*."):
                    if item.suffix == pattern[1:]:
                        should_exclude = True
                        break
                elif pattern in str(item):
                    should_exclude = True
                    break

            if not should_exclude:
                files.append(item)

    return files


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    """验证技能是否有效"""
    # 检查必需文件
    if not (skill_path / "SKILL.md").exists():
        return False, "缺少 SKILL.md"
    if not (skill_path / "_meta.json").exists():
        return False, "缺少 _meta.json"

    # 验证 meta 内容
    try:
        meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
        if "id" not in meta or "version" not in meta:
            return False, "_meta.json 缺少 id 或 version"
    except Exception as e:
        return False, f"_meta.json 解析错误: {e}"

    return True, "验证通过"


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    # 验证
    valid, msg = validate_skill(skill_path)
    if not valid:
        raise ValueError(f"技能验证失败: {msg}")

    # 获取元数据
    meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
    skill_name = meta.get("name", skill_path.name)

    # 创建输出目录
    if output_dir is None:
        output_dir = Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{meta['version']}_{timestamp}.skill"

    # 创建 zip 压缩包
    files = scan_directory(skill_path)
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            # 计算相对路径
            arcname = file_path.relative_to(skill_path)
            zf.write(file_path, arcname)

    return output_file


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"打包技能: {skill_path}")

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"打包成功: {output_file}")

        # 显示文件大小
        size = output_file.stat().st_size
        print(f"文件大小: {size:,} 字节")

    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
