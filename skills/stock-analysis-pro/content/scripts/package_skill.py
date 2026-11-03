#!/usr/bin/env python3
"""
stock-analysis-pro 技能打包脚本
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


def get_meta_info(skill_dir: str) -> dict:
    """读取_meta.json"""
    meta_file = Path(skill_dir) / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "0.0.0"}


def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """打包技能"""
    skill_dir = Path(skill_dir)
    meta = get_meta_info(skill_dir)

    skill_name = skill_dir.name
    version = meta.get("version", "0.0.0")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = f"{output_dir}/{skill_name}-v{version}-{timestamp}.skill"

    exclude_patterns = [
        '__pycache__', '.pyc', '.git', '.DS_Store',
        'Thumbs.db', '.pytest_cache'
    ]

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            for file in files:
                if any(pattern in file for pattern in exclude_patterns):
                    continue
                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_dir)
                zf.write(file_path, arc_name)

    print(f"✓ Skill packaged: {output_file}")
    return output_file


def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    output_file = package_skill(skill_dir, output_dir)
    print(f"\nPackage created: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
