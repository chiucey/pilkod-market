#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""
import os
import sys
import tarfile
import json
from pathlib import Path
from datetime import datetime

def collect_files(skill_path):
    """收集技能目录下的所有文件"""
    files = []

    for root, dirs, filenames in os.walk(skill_path):
        # 排除隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in filenames:
            # 排除隐藏文件和常见的构建垃圾
            if filename.startswith('.') or filename.endswith('.pyc'):
                continue

            file_path = Path(root) / filename
            rel_path = file_path.relative_to(skill_path)
            files.append((file_path, str(rel_path)))

    return files

def create_skill_package(skill_path, output_path=None):
    """创建 .skill 包"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        print(f"错误: 技能路径不存在 - {skill_path}")
        return False

    if output_path is None:
        # 默认输出到 skill-name_version.skill
        meta_path = skill_path / "_meta.json"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            version = meta.get('version', '1.0.0')
        else:
            version = '1.0.0'

        output_path = skill_path.parent / f"{skill_path.name}_{version}.skill"

    output_path = Path(output_path)

    print(f"正在打包技能: {skill_path.name}")
    print(f"输出文件: {output_path}")
    print("-" * 50)

    # 收集文件
    files = collect_files(skill_path)

    if not files:
        print("错误: 没有找到任何文件")
        return False

    print(f"包含文件 ({len(files)} 个):")
    for file_path, rel_path in files:
        print(f"  - {rel_path}")
    print()

    # 创建 tar.gz 包
    try:
        with tarfile.open(output_path, 'w:gz') as tar:
            for file_path, rel_path in files:
                tar.add(file_path, arcname=rel_path)

        size = output_path.stat().st_size
        print(f"✓ 打包成功!")
        print(f"  文件大小: {size / 1024:.2f} KB")
        print(f"  路径: {output_path}")
        return True

    except Exception as e:
        print(f"错误: 打包失败 - {e}")
        return False

def verify_package(package_path):
    """验证包内容"""
    package_path = Path(package_path)

    if not package_path.exists():
        print(f"警告: 打包文件不存在 - {package_path}")
        return False

    print("\n验证包内容:")
    try:
        with tarfile.open(package_path, 'r:gz') as tar:
            members = tar.getmembers()
            print(f"  文件数量: {len(members)}")

            has_skill_md = any('SKILL.md' in m.name for m in members)
            has_meta = any('_meta.json' in m.name for m in members)

            print(f"  包含 SKILL.md: {'✓' if has_skill_md else '✗'}")
            print(f"  包含 _meta.json: {'✓' if has_meta else '✗'}")

            return has_skill_md and has_meta

    except Exception as e:
        print(f"错误: 验证失败 - {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    output_path = None
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])

    success = create_skill_package(skill_path, output_path)

    if success and output_path:
        verify_package(output_path)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
