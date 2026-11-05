#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""
import os
import zipfile
import json
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """打包技能为 .skill 文件"""

    skill_name = skill_path.name
    version = "1.0.0"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{version}_{timestamp}.skill"

    # 创建 zip 文件（.skill 实际上是 zip 格式）
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    return output_file


def main():
    """打包主流程"""
    skill_path = Path('/workspace/temp-skills/email-sender')
    output_dir = Path('/workspace/temp-skills')

    print("=" * 50)
    print("技能打包工具")
    print("=" * 50)

    print(f"\n源路径: {skill_path}")
    print(f"输出目录: {output_dir}")

    print("\n打包内容:")
    output_file = package_skill(skill_path, output_dir)

    print(f"\n✅ 打包完成: {output_file}")
    print(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")

    # 验证打包内容
    print("\n验证打包内容:")
    with zipfile.ZipFile(output_file, 'r') as zf:
        for name in zf.namelist():
            info = zf.getinfo(name)
            print(f"  - {name} ({info.file_size} bytes)")

    print("=" * 50)

    return str(output_file)


if __name__ == '__main__':
    output = main()
    print(f"\n打包文件路径: {output}")
