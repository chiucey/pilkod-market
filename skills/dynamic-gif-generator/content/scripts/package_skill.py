#!/usr/bin/env python3
"""
技能打包脚本 - dynamic-gif-generator
"""

import json
import os
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    errors = []

    # 检查SKILL.md
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 不存在")
    else:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 --- 开头")
            if 'name:' not in content:
                errors.append("SKILL.md 缺少 name 字段")
            if 'description:' not in content:
                errors.append("SKILL.md 缺少 description 字段")

    # 检查_meta.json
    meta_json = Path(skill_path) / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json 不存在")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json JSON格式错误")

    if errors:
        print("验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("验证通过!")
    return True


def package_skill(skill_path: str, output_path: str = None) -> str:
    """打包技能"""
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    if output_path is None:
        output_path = f"/workspace/temp-skills/{skill_name}.skill"

    # 创建zip包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_dir)
                zipf.write(file_path, arcname)
                print(f"添加: {arcname}")

    print(f"\n打包完成: {output_path}")
    return output_path


def main():
    skill_path = "/workspace/temp-skills/dynamic-gif-generator"

    # 验证
    if not validate_skill(skill_path):
        return

    # 打包
    output = package_skill(skill_path)
    print(f"\n技能已成功打包!")


if __name__ == "__main__":
    main()
