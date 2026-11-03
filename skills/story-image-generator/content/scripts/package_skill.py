#!/usr/bin/env python3
"""
技能打包脚本
将 story-image-generator 技能打包为 .skill 文件

用法:
    python package_skill.py <skill_directory>
"""

import sys
import os
import zipfile
from pathlib import Path
import json
import argparse


def validate_skill_structure(skill_dir: Path) -> bool:
    """验证技能目录结构"""
    errors = []

    # 检查必填文件
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        file_path = skill_dir / filename
        if not file_path.exists():
            errors.append(f"缺少必填文件: {filename}")

    # 检查 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")

    # 检查 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        try:
            with open(meta_json, "r", encoding="utf-8") as f:
                meta = json.load(f)

            if "id" not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查 scripts 目录
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            if not os.access(script, os.R_OK):
                errors.append(f"脚本文件不可读: {script.name}")

    if errors:
        print("❌ 验证失败:")
        for error in errors:
            print(f"   - {error}")
        return False

    return True


def package_skill(skill_dir: Path, output_path: Path = None) -> bool:
    """打包技能为 .skill 文件"""
    skill_dir = skill_dir.resolve()

    if not skill_dir.exists():
        print(f"❌ 错误: 技能目录不存在: {skill_dir}")
        return False

    # 验证结构
    print("🔍 验证技能结构...")
    if not validate_skill_structure(skill_dir):
        return False

    # 确定输出路径
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_dir.name}.skill"

    # 打包
    print(f"📦 打包技能: {skill_dir.name}")
    print(f"   输出: {output_path}")

    try:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    # 跳过隐藏文件和备份目录
                    relative_path = file_path.relative_to(skill_dir)
                    if any(part.startswith('.') or part == '_original_backup' for part in relative_path.parts):
                        continue

                    arcname = str(relative_path)
                    zipf.write(file_path, arcname)
                    print(f"   + {arcname}")

        print(f"\n✅ 打包完成: {output_path}")
        return True

    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="打包技能为 .skill 文件")
    parser.add_argument("skill_dir", help="技能目录路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--validate-only", action="store_true", help="仅验证结构")

    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)

    if args.validate_only:
        print(f"🔍 验证技能: {skill_dir}")
        success = validate_skill_structure(skill_dir)
        sys.exit(0 if success else 1)

    success = package_skill(skill_dir, Path(args.output) if args.output else None)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()