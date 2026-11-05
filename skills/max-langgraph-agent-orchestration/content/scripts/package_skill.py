#!/usr/bin/env python3
"""
技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_safe_includes(skill_dir: Path) -> list[str]:
    """获取安全包含的文件模式"""
    return [
        "SKILL.md",
        "_meta.json",
        "scripts/",
        "references/",
        "assets/",
        "README.md",
        "LICENSE",
    ]


def create_package(skill_dir: Path, output_dir: Path) -> Path:
    """创建技能包"""
    skill_name = skill_dir.name
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    version = meta.get("version", "1.0.0")
    skill_id = meta.get("id", "unknown")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"{skill_name}_v{version}_{timestamp}.skill"
    output_path = output_dir / output_name

    # 创建 ZIP 包
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pattern in get_safe_includes(skill_dir):
            path = skill_dir / pattern
            if pattern.endswith("/"):
                # 目录模式
                dir_name = pattern.rstrip("/")
                if (skill_dir / dir_name).exists():
                    for file_path in (skill_dir / dir_name).rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(skill_dir)
                            zf.write(file_path, arcname)
            else:
                # 文件模式
                if path.exists():
                    zf.write(path, path.relative_to(skill_dir))

    return output_path


def main():
    """主打包流程"""
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else skill_dir.parent / "dist"

    if not skill_dir.exists():
        print(f"Error: Directory not found: {skill_dir}")
        sys.exit(1)

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        output_path = create_package(skill_dir, output_dir)
        print(f"✓ Package created: {output_path}")

        # 验证包内容
        with zipfile.ZipFile(output_path, "r") as zf:
            print(f"  Contents ({len(zf.namelist())} files):")
            for name in zf.namelist()[:5]:
                print(f"    - {name}")
            if len(zf.namelist()) > 5:
                print(f"    ... and {len(zf.namelist()) - 5} more")

    except Exception as e:
        print(f"✗ Package failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
