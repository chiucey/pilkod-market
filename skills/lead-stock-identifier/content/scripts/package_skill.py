#!/usr/bin/env python3
"""
龙头股票识别技能 - 打包脚本
将技能打包为可发布的.skill文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_meta(skill_path: Path) -> dict:
    """读取meta信息"""
    meta_file = skill_path / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_skill_package(skill_path: Path, output_dir: Path) -> Path:
    """创建技能包"""
    skill_path = skill_path.resolve()
    output_dir = output_dir.resolve()

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取meta
    meta = get_meta(skill_path)

    # 生成包名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{meta['name']}_v{meta['version']}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 打包
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 排除临时文件
                if '__pycache__' in str(file_path):
                    continue
                if file_path.suffix == '.pyc':
                    continue

                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n📦 Package created: {package_path}")
    print(f"  Size: {package_path.stat().st_size / 1024:.1f} KB")

    return package_path


def extract_skill_package(package_path: Path, extract_dir: Path) -> bool:
    """解压技能包（用于验证）"""
    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            zf.extractall(extract_dir)
        return True
    except Exception as e:
        print(f"Extract failed: {e}")
        return False


def main():
    """主函数"""
    # 默认路径
    skill_path = Path(__file__).parent.parent.resolve()
    output_dir = skill_path.parent / "output"

    print("=" * 50)
    print("Lead Stock Identifier - Package Builder")
    print("=" * 50)
    print(f"\n📂 Skill path: {skill_path}")
    print(f"📤 Output dir: {output_dir}")

    # 创建包
    print("\n📦 Creating package...")
    package_path = create_skill_package(skill_path, output_dir)

    print("\n" + "=" * 50)
    print("✅ Package created successfully!")
    print(f"\nPackage location: {package_path}")
    print("\nTo install: Copy the .skill file to your skills directory")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())