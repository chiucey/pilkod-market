#!/usr/bin/env python3
"""
技术交底书撰写技能 - 打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = "."):
    """打包技能为 .skill 文件"""
    skill_dir = Path(skill_path)

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    # 读取 meta 信息
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        skill_name = meta.get("id", "unknown")
        version = meta.get("version", "1.0.0")
    else:
        skill_name = skill_dir.name
        version = "1.0.0"

    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(output_dir) / f"tech_disclosure_writer_{version}_{timestamp}.skill"

    # 安全检查：确保不包含敏感文件
    forbidden_patterns = [
        "__pycache__",
        ".pyc",
        ".env",
        ".git",
        "secrets",
        "credentials"
    ]

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob("*"):
            if file_path.is_file():
                # 安全检查
                rel_path = file_path.relative_to(skill_dir)
                path_str = str(rel_path)

                if any(pattern in path_str for pattern in forbidden_patterns):
                    continue

                # 添加文件
                zf.write(file_path, rel_path)
                print(f"  + {rel_path}")

    print(f"\n打包完成: {output_file}")
    print(f"技能版本: {version}")
    return output_file

def main():
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"\n正在打包技能: {skill_path}")
    print("-" * 40)

    output_file = package_skill(skill_path, output_dir)
    print(f"\n输出文件: {output_file}")

if __name__ == "__main__":
    main()
