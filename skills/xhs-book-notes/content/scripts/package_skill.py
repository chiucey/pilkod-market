#!/usr/bin/env python3
"""
小红书书单笔记技能打包脚本
将技能文件夹打包为 .skill 文件用于发布
"""

import os
import zipfile
import json
import sys
from pathlib import Path


def validate_skill(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证技能结构"""
    errors = []

    # 检查必要文件
    if not (skill_dir / "SKILL.md").exists():
        errors.append("缺少 SKILL.md 文件")
    if not (skill_dir / "_meta.json").exists():
        errors.append("缺少 _meta.json 文件")

    # 检查 _meta.json 格式
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "id" not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            errors.append("SKILL.md 必须以 --- 开头")
        if "name:" not in content:
            errors.append("SKILL.md 缺少 name 字段")
        if "description:" not in content:
            errors.append("SKILL.md 缺少 description 字段")

    return len(errors) == 0, errors


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """打包技能为 .skill 文件"""
    skill_name = skill_dir.name
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    return output_file


def main():
    if len(sys.argv) < 2:
        # 默认打包当前目录下的技能
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    print(f"📦 开始打包技能: {skill_dir.name}")

    # 验证
    valid, errors = validate_skill(skill_dir)
    if not valid:
        print("❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("✅ 验证通过")

    # 打包
    output_dir = skill_dir.parent
    output_file = package_skill(skill_dir, output_dir)
    print(f"✅ 打包完成: {output_file}")


if __name__ == "__main__":
    main()
