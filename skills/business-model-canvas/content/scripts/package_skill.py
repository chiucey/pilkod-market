#!/usr/bin/env python3
"""
技能打包脚本 - 将技能文件夹打包为 .skill 文件
"""
import os
import zipfile
import json
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    skill_path = Path(skill_path)

    # 检查必要文件
    if not (skill_path / "SKILL.md").exists():
        print("❌ 缺少 SKILL.md 文件")
        return False

    if not (skill_path / "_meta.json").exists():
        print("❌ 缺少 _meta.json 文件")
        return False

    # 验证 _meta.json
    with open(skill_path / "_meta.json") as f:
        meta = json.load(f)

    if "id" not in meta:
        print("❌ _meta.json 缺少 id 字段")
        return False

    if "version" not in meta:
        print("❌ _meta.json 缺少 version 字段")
        return False

    # 验证 SKILL.md frontmatter
    with open(skill_path / "SKILL.md") as f:
        content = f.read()

    if not content.startswith("---"):
        print("❌ SKILL.md 必须以 frontmatter 开头")
        return False

    print("✅ 技能结构验证通过")
    return True

def package_skill(skill_path: str, output_path: str = None):
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    if output_path is None:
        output_path = str(skill_path.parent / f"{skill_path.name}.skill")

    print(f"\n📦 开始打包技能: {skill_path.name}")

    # 验证
    if not validate_skill(skill_path):
        sys.exit(1)

    # 创建 zip 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除空目录和临时文件
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__']]

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✅ 技能已打包: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_path]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_path, output_path)
