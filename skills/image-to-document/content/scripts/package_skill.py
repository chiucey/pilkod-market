#!/usr/bin/env python3
"""打包技能为 .skill 文件"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_version(skill_path: Path) -> str:
    """从 _meta.json 读取版本"""
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        return meta.get("version", "1.0.0")
    return "1.0.0"


def get_name(skill_path: Path) -> str:
    """获取技能名称"""
    return skill_path.name


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """打包技能"""
    skill_name = get_name(skill_path)
    version = get_version(skill_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # 输出文件名
    output_file = output_dir / f"{skill_name}-{version}.skill"

    # 安全检查：确保不包含敏感文件
    sensitive_patterns = [".env", "secrets", "credentials", ".pem", ".key", ".git"]

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # 检查敏感文件
                path_str = str(file_path)
                for pattern in sensitive_patterns:
                    if pattern in path_str:
                        print(f"跳过敏感文件: {file_path.relative_to(skill_path)}")
                        continue

                # 添加到 zip
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    return output_file


def main():
    skill_path = Path("/workspace/temp-skills/image-to-document")
    output_dir = Path("/workspace/temp-skills")

    print("=" * 50)
    print("技能打包工具")
    print("=" * 50)
    print(f"\n技能路径: {skill_path}")
    print(f"输出目录: {output_dir}")

    if not skill_path.exists():
        print(f"错误: 技能路径不存在")
        sys.exit(1)

    # 检查必要文件
    if not (skill_path / "SKILL.md").exists():
        print(f"错误: SKILL.md 不存在")
        sys.exit(1)

    if not (skill_path / "_meta.json").exists():
        print(f"错误: _meta.json 不存在")
        sys.exit(1)

    print(f"\n开始打包...")
    print("-" * 50)

    output_file = package_skill(skill_path, output_dir)

    print("-" * 50)
    print(f"\n打包完成!")
    print(f"输出文件: {output_file}")
    print(f"文件大小: {output_file.stat().st_size} bytes")


if __name__ == "__main__":
    main()