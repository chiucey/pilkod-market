#!/usr/bin/env python3
"""
打包技能为 .skill 文件
"""

import os
import json
import shutil
import sys
from datetime import datetime


def get_skill_meta(skill_path: str) -> dict:
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def validate_for_package(skill_path: str) -> tuple[bool, list]:
    """打包前验证"""
    errors = []

    # 检查必要文件
    if not os.path.exists(os.path.join(skill_path, "SKILL.md")):
        errors.append("缺少 SKILL.md")
    if not os.path.exists(os.path.join(skill_path, "_meta.json")):
        errors.append("缺少 _meta.json")

    # 检查_meta.json
    meta = get_skill_meta(skill_path)
    if "id" not in meta:
        errors.append("_meta.json 缺少 id 字段")
    if "version" not in meta:
        errors.append("_meta.json 缺少 version 字段")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能"""
    skill_name = os.path.basename(skill_path)
    meta = get_skill_meta(skill_path)

    valid, errors = validate_for_package(skill_path)
    if not valid:
        print("打包验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 创建输出文件名
    version = meta.get("version", "1.0.0")
    skill_id = meta.get("id", "unknown")
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 复制整个目录到.skill文件（实际上是目录）
    if os.path.exists(output_file):
        shutil.rmtree(output_file)

    shutil.copytree(skill_path, output_file)

    # 添加打包信息
    pkg_info = {
        "packaged_at": datetime.now().isoformat(),
        "packaged_by": "skill-creator",
        "skill_id": skill_id,
        "version": version
    }

    with open(os.path.join(output_file, "_package.json"), 'w', encoding='utf-8') as f:
        json.dump(pkg_info, f, indent=2, ensure_ascii=False)

    return output_file


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    output = package_skill(skill_path, output_dir)
    print(f"✓ 技能已打包: {output}")