#!/usr/bin/env python3
"""Alpha-Eleven 技能打包脚本"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def get_version():
    """从_meta.json读取版本号"""
    meta_path = Path(__file__).parent.parent / '_meta.json'
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        return meta.get('version', '1.0.0')
    return '1.0.0'

def get_name():
    """从_meta.json读取技能名称"""
    meta_path = Path(__file__).parent.parent / '_meta.json'
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        return meta.get('id', 'alpha-eleven')
    return 'alpha-eleven'

def create_package():
    """创建技能包"""
    skill_dir = Path(__file__).parent.parent
    output_dir = Path('/workspace/temp-skills/output')
    output_dir.mkdir(exist_ok=True)

    name = get_name()
    version = get_version()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_name = f"{name}-{version}-{timestamp}.skill"
    output_path = output_dir / output_name

    # 创建zip包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除output和__pycache__
            dirs[:] = [d for d in dirs if d not in ['output', '__pycache__', '.git']]

            for file in files:
                if file.endswith('.skill') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print("=" * 50)
    print("Alpha-Eleven 技能打包完成")
    print("=" * 50)
    print(f"技能名称: {name}")
    print(f"版本号: {version}")
    print(f"打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出路径: {output_path}")
    print("=" * 50)

    return str(output_path)

if __name__ == '__main__':
    create_package()
