#!/usr/bin/env python3
"""
供应商信息提取技能 - 打包脚本
生成可分发的 .skill 文件
"""

import os
import zipfile
import shutil
import sys
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """
    打包技能文件夹为 .skill 文件

    Args:
        skill_path: 技能文件夹路径
        output_dir: 输出目录，默认为当前目录

    Returns:
        生成的 .skill 文件路径
    """
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = Path("/workspace/temp-skills")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 创建打包文件
    print(f"正在打包技能: {skill_name}")
    print(f"输出文件: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 跳过 __pycache__ 等
                if '__pycache__' in str(file_path):
                    continue
                # 计算相对路径
                arcname = file_path.relative_to(skill_path.parent)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n打包完成: {output_file}")
    return str(output_file)


def verify_package(package_path: str) -> bool:
    """
    验证打包文件完整性

    Args:
        package_path: .skill 文件路径

    Returns:
        验证是否通过
    """
    package_path = Path(package_path)

    if not package_path.exists():
        print(f"错误: 打包文件不存在: {package_path}")
        return False

    required_files = [
        "vendor-info-extractor/SKILL.md",
        "vendor-info-extractor/_meta.json"
    ]

    with zipfile.ZipFile(package_path, 'r') as zf:
        file_list = zf.namelist()

        for required in required_files:
            if required not in file_list:
                print(f"错误: 缺少必需文件: {required}")
                return False

    print("验证通过: 所有必需文件存在")
    return True


def main():
    skill_path = "/workspace/temp-skills/vendor-info-extractor"

    print("=" * 50)
    print("供应商信息提取技能 - 打包工具")
    print("=" * 50)

    try:
        # 打包
        package_path = package_skill(skill_path)

        # 验证
        print("\n[验证] 检查打包完整性...")
        if verify_package(package_path):
            print("\n" + "=" * 50)
            print(f"打包成功！")
            print(f"文件路径: {package_path}")
            print("=" * 50)
            return 0
        else:
            print("\n验证失败")
            return 1

    except Exception as e:
        print(f"\n错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
