#!/usr/bin/env python3
"""
Package Skill Script
打包技能为 .skill 文件用于分发
"""

import os
import sys
import json
import zipfile
from pathlib import Path


def validate_skill(skill_path: Path) -> bool:
    """验证技能结构"""
    errors = []

    # 检查 SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 不存在")
    else:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md 必须以 frontmatter --- 开头")
        if "name:" not in content:
            errors.append("SKILL.md 缺少 name 字段")
        if "description:" not in content:
            errors.append("SKILL.md 缺少 description 字段")

    # 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json 不存在")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("✅ 验证通过")
    return True


def package_skill(skill_path: Path, output_path: Path = None) -> Path:
    """打包技能为 .skill 文件"""

    if output_path is None:
        output_path = skill_path.parent / f"{skill_path.name}.skill"

    # 收集所有要打包的文件
    files_to_package = []
    for root, dirs, files in os.walk(skill_path):
        # 跳过 __pycache__ 等目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.startswith('.') or file.endswith('.pyc'):
                continue
            file_path = Path(root) / file
            rel_path = file_path.relative_to(skill_path)
            files_to_package.append((file_path, rel_path))

    print(f"\n📦 打包文件列表 ({len(files_to_package)} 个文件):")
    for fp, rp in files_to_package:
        print(f"  + {rp}")

    # 创建 zip 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, rel_path in files_to_package:
            zf.write(file_path, rel_path)

    print(f"\n✅ 打包完成: {output_path}")
    print(f"   文件大小: {output_path.stat().st_size / 1024:.1f} KB")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()

    if not skill_path.exists():
        print(f"❌ 路径不存在: {skill_path}")
        sys.exit(1)

    print(f"📁 技能路径: {skill_path}")
    print("=" * 50)

    # 验证
    if not validate_skill(skill_path):
        sys.exit(1)

    # 打包
    output_path = package_skill(skill_path)

    print("=" * 50)
    print(f"\n🎉 技能打包成功!")
    print(f"   产出文件: {output_path}")

    return output_path


if __name__ == "__main__":
    main()
