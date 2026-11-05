#!/usr/bin/env python3
"""
打包每日简报技能为 .skill 文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path

SKILL_DIR = Path("/workspace/temp-skills/daily-briefing")
OUTPUT_DIR = Path("/workspace/temp-skills")
SKILL_NAME = "daily-briefing"

def validate_skill():
    """验证技能包结构"""
    errors = []

    # 检查必需文件
    if not (SKILL_DIR / "SKILL.md").exists():
        errors.append("缺少 SKILL.md 文件")
    else:
        # 检查 frontmatter
        with open(SKILL_DIR / "SKILL.md", "r", encoding="utf-8") as f:
            content = f.read()
            if not content.startswith("---"):
                errors.append("SKILL.md 必须以 frontmatter (---) 开头")
            if "name:" not in content:
                errors.append("SKILL.md 缺少 name 字段")
            if "description:" not in content:
                errors.append("SKILL.md 缺少 description 字段")

    if not (SKILL_DIR / "_meta.json").exists():
        errors.append("缺少 _meta.json 文件")
    else:
        with open(SKILL_DIR / "_meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
            if "id" not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 version 字段")

    # 检查 dist 目录
    if not (SKILL_DIR / "dist").exists():
        errors.append("缺少 dist 目录")
    elif not (SKILL_DIR / "dist" / "index.html").exists():
        errors.append("缺少 dist/index.html 文件")

    return errors

def package_skill():
    """打包技能为 .skill 文件"""
    errors = validate_skill()
    if errors:
        print("验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 创建 .skill 文件
    skill_file = OUTPUT_DIR / f"{SKILL_NAME}.skill"

    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 添加 SKILL.md
        zf.write(SKILL_DIR / "SKILL.md", arcname="SKILL.md")

        # 添加 _meta.json
        zf.write(SKILL_DIR / "_meta.json", arcname="_meta.json")

        # 添加 dist 目录
        dist_dir = SKILL_DIR / "dist"
        for file in dist_dir.rglob("*"):
            if file.is_file():
                arcname = str(file.relative_to(SKILL_DIR))
                zf.write(file, arcname=arcname)

    print(f"技能打包成功: {skill_file}")
    print(f"文件大小: {skill_file.stat().st_size / 1024:.2f} KB")

    # 列出包含的文件
    with zipfile.ZipFile(skill_file, 'r') as zf:
        print("\n打包内容:")
        for name in sorted(zf.namelist()):
            info = zf.getinfo(name)
            print(f"  {name} ({info.file_size / 1024:.2f} KB)")

    return True

if __name__ == "__main__":
    package_skill()
