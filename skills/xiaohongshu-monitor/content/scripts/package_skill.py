#!/usr/bin/env python3
"""打包技能为 .skill 文件"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能文件夹为 .skill 文件"""

    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    # 读取 meta 信息
    meta_path = skill_dir / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 生成输出文件名
    version = meta.get('version', '1.0.0')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = f"{skill_name}-{version}.{timestamp}.skill"
    output_path = Path(output_dir) / output_file

    # 创建 zip 包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # 跳过 __pycache__ 等目录
                if '__pycache__' in str(file_path):
                    continue
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    return str(output_path.absolute())

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    result = package_skill(skill_path, output_dir)
    print(f"✅ 技能已打包: {result}")