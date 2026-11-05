#!/usr/bin/env python3
"""
财务报告分析技能打包脚本
将技能打包为可分发的.skill文件
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_meta(skill_path: str) -> dict:
    """读取技能元数据"""
    meta_path = Path(skill_path) / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_skill_files(skill_path: str) -> list:
    """获取技能所有文件"""
    skill_files = []
    skill_path_obj = Path(skill_path)

    for root, dirs, files in os.walk(skill_path_obj):
        # 跳过隐藏目录和__pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.startswith('.'):
                continue

            file_path = Path(root) / file
            rel_path = file_path.relative_to(skill_path_obj)
            skill_files.append({
                "abs_path": str(file_path),
                "rel_path": str(rel_path),
                "size": file_path.stat().st_size
            })

    return skill_files


def check_sensitive_content(file_path: str) -> bool:
    """检查文件是否包含敏感内容"""
    sensitive_patterns = [
        "password", "secret", "api_key", "token",
        "credential", "private_key", "access_token"
    ]

    file_lower = file_path.lower()
    for pattern in sensitive_patterns:
        if pattern in file_lower:
            return True

    # 检查.env文件
    if file_path.endswith('.env'):
        return True

    return False


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为.skill文件"""
    skill_path_obj = Path(skill_path)
    skill_name = skill_path_obj.name

    # 读取元数据
    meta = get_skill_meta(skill_path)
    skill_version = meta.get("version", "1.0.0")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = Path(output_dir) / f"{skill_name}_v{skill_version}_{timestamp}.skill"

    # 获取文件列表
    skill_files = get_skill_files(skill_path)

    print(f"Packaging skill: {skill_name}")
    print(f"Version: {skill_version}")
    print(f"Output: {output_file}")
    print(f"Files to package: {len(skill_files)}")
    print("-" * 50)

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_info in skill_files:
            abs_path = file_info["abs_path"]
            rel_path = file_info["rel_path"]

            # 安全检查
            if check_sensitive_content(abs_path):
                print(f"  [SKIP] {rel_path} - sensitive content detected")
                continue

            zf.write(abs_path, rel_path)
            print(f"  [ADD] {rel_path} ({file_info['size']} bytes)")

    print("-" * 50)
    print(f"Package created successfully: {output_file}")

    # 验证包内容
    with zipfile.ZipFile(output_file, 'r') as zf:
        print(f"Verification: {len(zf.namelist())} files in archive")
        for name in zf.namelist()[:5]:
            print(f"  - {name}")
        if len(zf.namelist()) > 5:
            print(f"  ... and {len(zf.namelist()) - 5} more files")

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\nDone! Skill package: {output_file}")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
