#!/usr/bin/env python3
"""
浏览器爬虫技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

def read_meta(skill_path: Path) -> dict:
    """读取技能元数据"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    return json.loads(meta_file.read_text(encoding="utf-8"))

def scan_files(skill_path: Path) -> list[Path]:
    """扫描技能目录中的所有文件"""
    files = []
    exclude_patterns = {
        '__pycache__',
        '.pyc',
        '.DS_Store',
        '.git',
        '.gitignore'
    }

    for item in skill_path.rglob('*'):
        if item.is_file():
            # 检查是否应该排除
            if any(pattern in str(item) for pattern in exclude_patterns):
                continue
            files.append(item.relative_to(skill_path))

    return files

def create_package(skill_path: Path, output_dir: Path) -> Path:
    """创建技能包"""
    meta = read_meta(skill_path)

    # 生成包名
    skill_name = meta.get("name", "unknown")
    version = meta.get("version", "1.0.0")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_name}_{version}_{timestamp}.skill"

    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / package_name

    # 创建 zip 文件
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        files = scan_files(skill_path)

        for file_path in files:
            full_path = skill_path / file_path
            zf.write(full_path, file_path)
            print(f"  Added: {file_path}")

    print(f"\nPackage created: {package_path}")
    return package_path

def verify_package(package_path: Path) -> bool:
    """验证打包结果"""
    if not package_path.exists():
        print("Package file not found!")
        return False

    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            files = zf.namelist()
            print(f"\nPackage contents ({len(files)} files):")
            for f in files:
                print(f"  - {f}")

            # 检查必含文件
            required = ["SKILL.md", "_meta.json"]
            for req in required:
                if req not in files:
                    print(f"Missing required file: {req}")
                    return False

            print("\nPackage verification: PASSED")
            return True
    except zipfile.BadZipFile:
        print("Invalid zip file!")
        return False

def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"Skill path not found: {skill_path}")
        sys.exit(1)

    print("=" * 50)
    print("浏览器爬虫技能打包")
    print("=" * 50)
    print(f"Source: {skill_path}")

    # 创建临时打包目录
    output_dir = Path("/workspace/temp-skills/packages")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        package_path = create_package(skill_path, output_dir)
        if verify_package(package_path):
            print("\n打包成功!")
            print(f"文件路径: {package_path}")
    except Exception as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
