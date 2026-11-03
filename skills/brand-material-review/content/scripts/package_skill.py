#!/usr/bin/env python3
"""
品牌物料审核技能 - 打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_path: str = None) -> tuple[bool, str]:
    """打包技能为 .skill 文件"""

    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"/workspace/temp-skills/{skill_name}_{timestamp}.skill"

    # 收集所有文件
    files_to_include = []
    for root, dirs, files in os.walk(skill_dir):
        # 排除隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if not file.startswith('.'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(skill_dir)
                files_to_include.append((file_path, rel_path))

    # 创建 ZIP 文件
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, rel_path in files_to_include:
                zf.write(file_path, rel_path)

        return True, output_path
    except Exception as e:
        return False, str(e)

def verify_package(skill_path: str, zip_path: str) -> tuple[bool, list[str]]:
    """验证打包内容"""
    errors = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        file_list = zf.namelist()

        # 必须包含的文件
        required = ['SKILL.md', '_meta.json']
        for req in required:
            if req not in file_list:
                errors.append(f"缺少必需文件: {req}")

        # 检查是否有不该包含的文件
        for name in file_list:
            if any(part.startswith('.') for part in name.split('/')):
                errors.append(f"包含隐藏文件: {name}")

    return len(errors) == 0, errors

def main():
    skill_path = "/workspace/temp-skills/brand-material-review"

    print("=" * 50)
    print("品牌物料审核技能 - 打包工具")
    print("=" * 50)

    # 打包
    print("\n正在打包技能...")
    success, result = package_skill(skill_path)

    if not success:
        print(f"✗ 打包失败: {result}")
        return 1

    zip_path = result
    print(f"✓ 打包完成: {zip_path}")

    # 验证
    print("\n验证打包内容...")
    valid, errors = verify_package(skill_path, zip_path)

    if valid:
        print("✓ 打包内容验证通过")

        # 显示包含的文件
        with zipfile.ZipFile(zip_path, 'r') as zf:
            print("\n包含的文件:")
            for name in sorted(zf.namelist()):
                print(f"  - {name}")
    else:
        print("✗ 打包内容验证失败:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n" + "=" * 50)
    print(f"✓ 技能打包成功！")
    print(f"  输出文件: {zip_path}")
    print("=" * 50)

    return 0

if __name__ == "__main__":
    exit(main())
