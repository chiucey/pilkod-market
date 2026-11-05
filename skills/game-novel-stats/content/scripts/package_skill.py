#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包成 .skill 文件
"""

import json
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def validate_skill(skill_dir: Path) -> tuple[bool, list]:
    """验证技能结构"""
    errors = []

    # 检查必需文件
    if not (skill_dir / "SKILL.md").exists():
        errors.append("缺少 SKILL.md 文件")
    if not (skill_dir / "_meta.json").exists():
        errors.append("缺少 _meta.json 文件")

    # 检查 _meta.json
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if "id" not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if "version" not in meta:
                    errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    # 检查 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 frontmatter (---) 开头")

            # 简单检查 frontmatter
            if 'name:' not in content or 'description:' not in content:
                errors.append("SKILL.md frontmatter 缺少 name 或 description")

    return len(errors) == 0, errors


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """打包技能目录"""
    skill_dir = Path(skill_dir)

    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 验证
    is_valid, errors = validate_skill(skill_dir)
    if not is_valid:
        print("验证失败:")
        for err in errors:
            print(f"  - {err}")
        raise ValueError("技能结构验证失败")

    # 读取 meta 信息
    with open(skill_dir / "_meta.json", 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = meta.get("name", skill_dir.name)
    skill_version = meta.get("version", "1.0.0")

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}-{skill_version}.skill"

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # 跳过 __pycache__ 等
                if '__pycache__' in str(file_path):
                    continue
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print(f"✅ 技能打包成功: {output_file}")
    return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="打包技能为 .skill 文件")
    parser.add_argument("skill_dir", help="技能目录路径")
    parser.add_argument("--output", "-o", help="输出目录（可选）")

    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    output_dir = Path(args.output) if args.output else None

    try:
        output_file = package_skill(skill_dir, output_dir)
        print(f"\n打包完成!")
        print(f"文件位置: {output_file.absolute()}")
    except Exception as e:
        print(f"打包失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
