#!/usr/bin/env python3
"""
技能打包脚本 - 将技能目录打包为.skill文件
"""

import os
import zipfile
import json
import sys
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path('/workspace/temp-skills/output')
EXCLUDE_PATTERNS = [
    '__pycache__', '*.pyc', '.git', '.DS_Store',
    '*.log', 'node_modules', '.venv', 'venv'
]

def should_include(path):
    """判断文件是否应该包含在打包中"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str or path_str.endswith(pattern):
            return False
    return True

def package_skill():
    """打包技能目录"""
    skill_name = SKILL_DIR.name
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 创建zip包
    print(f"📦 打包技能: {skill_name}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # 过滤目录
            dirs[:] = [d for d in dirs if should_include(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file
                if should_include(file_path):
                    arcname = file_path.relative_to(SKILL_DIR)
                    zf.write(file_path, arcname)
                    print(f"   + {arcname}")

    print(f"\n✅ 打包完成: {output_file}")
    return output_file

def main():
    try:
        output = package_skill()
        print(f"\n技能文件路径: {output}")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
