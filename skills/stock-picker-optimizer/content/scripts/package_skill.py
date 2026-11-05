#!/usr/bin/env python3
"""
打包技能到 .skill 文件
"""
import os
import json
import shutil
import zipfile
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "."):
    skill_path = Path(skill_dir)
    skill_name = skill_path.name
    output_file = Path(output_dir) / f"{skill_name}.skill"

    # 验证 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    # 验证 _meta.json 存在
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        raise FileNotFoundError(f"_meta.json not found in {skill_dir}")

    # 读取 meta 验证格式
    with open(meta_json, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta or 'version' not in meta:
        raise ValueError("_meta.json must contain 'id' and 'version' fields")

    # 创建打包目录
    temp_dir = Path("/tmp") / f"pkg_{skill_name}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    # 复制文件（排除隐藏文件和临时文件）
    for item in skill_path.rglob("*"):
        if item.is_file():
            relative = item.relative_to(skill_path)
            dest = temp_dir / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            # 跳过 .DS_Store 等系统文件
            if ".DS_Store" not in str(item) and "__pycache__" not in str(item):
                shutil.copy2(item, dest)

    # 创建 zip 归档
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in temp_dir.rglob("*"):
            if item.is_file():
                arcname = item.relative_to(temp_dir)
                zf.write(item, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"✅ Skill packaged successfully: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    package_skill(skill_dir, output_dir)
