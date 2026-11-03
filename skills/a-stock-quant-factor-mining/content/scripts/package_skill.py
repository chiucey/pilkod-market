#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包腳本
將技能打包為可分發的 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_skill_package(skill_path_str, output_dir=None):
    """創建技能包"""
    skill_path = Path(skill_path_str)

    if not skill_path.exists():
        print(f"錯誤: 技能目錄不存在: {skill_path}")
        return False

    # 讀取元數據
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        skill_name = meta.get('name', skill_path.name)
        skill_version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        skill_version = '1.0.0'

    # 創建輸出目錄
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent

    output_path.mkdir(parents=True, exist_ok=True)

    # 生成包文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"{skill_name}_{skill_version}_{timestamp}.skill"
    package_path = output_path / package_name

    # 創建 zip 包
    print(f"正在打包技能: {skill_name}")
    print(f"版本: {skill_version}")
    print(f"輸出: {package_path}")

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 跳過隱藏目錄和臨時文件
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path.parent)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ 技能包創建成功: {package_path}")
    print(f"  大小: {package_path.stat().st_size / 1024:.2f} KB")

    return str(package_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/a-stock-quant-factor-mining"
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    create_skill_package(skill_path, output_dir)
