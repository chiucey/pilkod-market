#!/usr/bin/env python3
"""
金融租赁同业项目搜集技能 - 打包脚本
将技能打包为 .skill 文件，便于分发和安装
"""
import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path("/workspace/temp-skills")


def collect_skill_files(skill_dir: Path) -> list[Path]:
    """收集技能的所有文件（排除临时文件和隐藏文件）"""
    collected = []
    exclude_patterns = [
        "__pycache__",
        ".DS_Store",
        "Thumbs.db",
        "*.pyc",
        "*.pyo",
    ]

    def should_exclude(path: Path) -> bool:
        name = path.name
        for pattern in exclude_patterns:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
            if name == pattern:
                return True
        return False

    for item in skill_dir.rglob("*"):
        if should_exclude(item):
            continue
        if item.is_file():
            collected.append(item)

    return collected


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """打包技能为 .skill 文件"""
    skill_name = skill_dir.name
    meta_path = skill_dir / "_meta.json"

    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    skill_id = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")
    output_file = output_dir / f"{skill_name}_v{version}.skill"

    # 收集文件
    files = collect_skill_files(skill_dir)

    # 创建临时目录用于打包
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 写入清单文件
        manifest = {
            "name": skill_name,
            "id": skill_id,
            "version": version,
            "files": [
                str(f.relative_to(skill_dir)) for f in files
            ],
        }
        manifest_path = tmp_path / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # 创建 tar.gz 包
        with tarfile.open(output_file, "w:gz") as tar:
            # 添加清单
            tar.add(manifest_path, arcname="manifest.json")

            # 添加所有技能文件
            for file_path in files:
                arcname = str(file_path.relative_to(skill_dir))
                tar.add(file_path, arcname=arcname)

    return output_file


def main():
    print("=" * 50)
    print("金融租赁同业项目搜集技能 - 打包工具")
    print("=" * 50)

    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        output_file = package_skill(SKILL_DIR, output_dir)
        print(f"\n✅ 打包成功！")
        print(f"   输出文件: {output_file}")
        print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")
        return 0
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
