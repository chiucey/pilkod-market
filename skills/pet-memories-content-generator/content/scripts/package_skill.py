#!/usr/bin/env python3
"""
宠物情感经济内容生成器 - Skill打包脚本
生成可分发的.skill文件
"""

import os
import sys
import shutil
import json
import zipfile
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> dict:
    """打包Skill为可分发文件"""
    results = {
        "success": False,
        "output_path": None,
        "files_included": [],
        "errors": []
    }

    skill_name = os.path.basename(skill_path)

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    output_file = os.path.join(output_dir, f"{skill_name}.skill")
    temp_dir = os.path.join(output_dir, f"{skill_name}_temp")

    try:
        # 复制到临时目录（过滤敏感文件）
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        shutil.copytree(skill_path, temp_dir)

        # 过滤不需要的文件
        exclude_patterns = [
            "__pycache__",
            ".pyc",
            ".DS_Store",
            "Thumbs.db",
            ".git"
        ]

        for root, dirs, files in os.walk(temp_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            # 过滤文件
            for file in files:
                if any(pattern in file for pattern in exclude_patterns):
                    os.remove(os.path.join(root, file))

        # 创建zip包
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
                    results["files_included"].append(arcname)

        # 清理临时目录
        shutil.rmtree(temp_dir)

        results["success"] = True
        results["output_path"] = output_file

    except Exception as e:
        results["errors"].append(str(e))

    return results

def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/pet-memories-content-generator"
    else:
        skill_path = sys.argv[1]

    print("=" * 60)
    print("宠物情感经济内容生成器 - Skill打包")
    print("=" * 60)

    results = package_skill(skill_path)

    if results["success"]:
        print(f"\n✓ 打包成功!")
        print(f"输出路径: {results['output_path']}")
        print(f"包含文件数: {len(results['files_included'])}")
        print("\n文件列表:")
        for f in results["files_included"]:
            print(f"  - {f}")
    else:
        print(f"\n✗ 打包失败!")
        for error in results["errors"]:
            print(f"  错误: {error}")
        sys.exit(1)

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()