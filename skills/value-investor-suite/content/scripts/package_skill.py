#!/usr/bin/env python3
"""
打包技能脚本 - 生成 .skill 分发文件
"""

import os
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(file_path: Path) -> str:
    """计算文件SHA256哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """
    打包技能为 .skill 文件
    返回生成的 .skill 文件路径
    """
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取元数据
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    skill_name = meta.get("name", skill_path.name)
    version = meta.get("version", "1.0.0")

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        # 遍历技能目录
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # 排除隐藏文件和 __pycache__
                if "__pycache__" in str(file_path) or file_path.name.startswith("."):
                    continue

                # 计算相对路径
                rel_path = file_path.relative_to(skill_path)
                zf.write(file_path, rel_path)
                print(f"  添加: {rel_path}")

    # 生成manifest
    manifest = {
        "name": skill_name,
        "version": version,
        "packaged_at": datetime.now().isoformat(),
        "files": []
    }

    # 添加文件哈希
    for file_path in skill_path.rglob("*"):
        if file_path.is_file() and "__pycache__" not in str(file_path):
            rel_path = str(file_path.relative_to(skill_path))
            manifest["files"].append({
                "path": rel_path,
                "hash": get_file_hash(file_path)
            })

    manifest_file = output_dir / f"{skill_name}.manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n打包完成: {output_file}")
    print(f"清单文件: {manifest_file}")

    return str(output_file)

def main():
    import sys

    if len(sys.argv) < 2:
        skill_path = "."
        output_dir = "."
    elif len(sys.argv) < 3:
        skill_path = sys.argv[1]
        output_dir = "."
    else:
        skill_path = sys.argv[1]
        output_dir = sys.argv[2]

    print(f"正在打包技能: {skill_path}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)

    try:
        output_file = package_skill(skill_path, output_dir)
        print("\n" + "=" * 50)
        print(f"成功！技能已打包为: {output_file}")
    except Exception as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
