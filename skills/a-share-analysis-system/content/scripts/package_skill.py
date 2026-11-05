#!/usr/bin/env python3
"""
A股分析预测系统 - 技能打包脚本
生成 .skill 文件用于分发
"""

import json
import os
import shutil
import sys
import tarfile
from pathlib import Path
from datetime import datetime

def create_package(skill_dir, output_dir=None):
    """创建技能包"""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = skill_path.parent / "packages"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成包文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"{skill_name}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 创建 tar.gz 包
    with tarfile.open(package_path, "w:gz") as tar:
        tar.add(skill_dir, arcname=skill_name)

    print(f"✓ 技能包已创建: {package_path}")
    return str(package_path), skill_name

def verify_package(package_path, skill_name):
    """验证包内容"""
    print("\n验证包内容...")

    with tarfile.open(package_path, "r:gz") as tar:
        members = tar.getmembers()

        # 检查必需文件 - 使用正确的arcname
        required_files = [
            f"{skill_name}/SKILL.md",
            f"{skill_name}/_meta.json"
        ]

        member_names = [m.name for m in members]

        for req_file in required_files:
            if req_file not in member_names:
                print(f"✗ 缺少必需文件: {req_file}")
                return False

        print(f"✓ 包含 {len(members)} 个文件/目录")
        for member in members[:10]:  # 只显示前10个
            print(f"  - {member.name}")

        if len(members) > 10:
            print(f"  ... 还有 {len(members) - 10} 个文件")

    return True

def main():
    skill_dir = "/workspace/temp-skills/a-share-analysis-system"

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]

    if not os.path.exists(skill_dir):
        print(f"✗ 技能目录不存在: {skill_dir}")
        return 1

    # 读取 meta.json 验证
    meta_path = os.path.join(skill_dir, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        print(f"技能 ID: {meta.get('id')}")
        print(f"版本: {meta.get('version')}")

    # 创建包
    try:
        package_path, skill_name = create_package(skill_dir)
        if verify_package(package_path, skill_name):
            print("\n✓ 打包成功!")
            return 0
        else:
            print("\n✗ 打包失败: 验证未通过")
            return 1
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
