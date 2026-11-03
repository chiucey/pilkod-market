#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可发布的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_meta(skill_path: Path) -> dict:
    """获取技能元数据"""
    meta_file = skill_path / "_meta.json"
    return json.loads(meta_file.read_text(encoding="utf-8"))


def scan_for_secrets(skill_path: Path) -> list[str]:
    """扫描可能包含敏感信息的文件"""
    dangerous = []
    patterns = [".env", "credentials", "secrets", ".pem", ".key", "id_rsa"]

    for f in skill_path.rglob("*"):
        if f.is_file():
            for pattern in patterns:
                if pattern in f.name.lower():
                    dangerous.append(str(f.relative_to(skill_path)))

    return dangerous


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """打包技能"""
    meta = get_meta(skill_path)

    # 检查敏感文件
    secrets = scan_for_secrets(skill_path)
    if secrets:
        print("⚠️ 警告：检测到可能包含敏感信息的文件:")
        for s in secrets:
            print(f"  - {s}")
        print("这些文件将被包含在打包中，请确认安全。\n")

    # 创建输出文件名
    skill_name = skill_path.name
    version = meta.get("version", "1.0.0")
    output_file = output_dir / f"{skill_name}_v{version}.skill"

    # 创建 ZIP 打包
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    return output_file


def main():
    skill_path = Path("/workspace/temp-skills/ethics-safety-filter")
    output_dir = Path("/workspace/temp-skills/dist")

    print("=" * 50)
    print("技能打包")
    print("=" * 50)
    print(f"\n技能路径: {skill_path}")
    print(f"输出目录: {output_dir}\n")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 打包
    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n✓ 打包完成: {output_file}")
        print(f"  文件大小: {output_file.stat().st_size:,} bytes")
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
