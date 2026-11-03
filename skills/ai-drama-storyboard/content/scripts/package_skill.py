#!/usr/bin/env python3
"""
打包技能脚本 - 生成 .skill 文件
"""

import json
import os
import shutil
import sys
import tarfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_dir: str, output_dir: str = "."):
    """打包技能目录为 .skill 文件"""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)

    if not skill_path.exists():
        print(f"❌ 错误: 技能目录不存在: {skill_dir}")
        return False

    # 读取元数据
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_id = meta.get('id', 'unknown')
        version = meta.get('version', '1.0.0')
    else:
        skill_id = 'unknown'
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_path / f"ai-drama-storyboard_v{version}_{timestamp}.skill"

    # 创建打包列表
    include_patterns = [
        'SKILL.md',
        '_meta.json',
        'references/',
        'scripts/',
        'assets/'
    ]

    # 打包
    print(f"📦 打包技能: {skill_path.name}")
    print(f"   输出文件: {output_file}")

    with tarfile.open(output_file, 'w:gz') as tar:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                tar.add(file_path, arcname=arcname)
                print(f"   + {arcname}")

    print(f"\n✅ 打包完成: {output_file}")
    print(f"   技能ID: {skill_id}")
    print(f"   版本: {version}")

    return True

if __name__ == "__main__":
    skill_dir = Path(__file__).parent.parent
    output_dir = Path(__file__).parent.parent

    success = package_skill(skill_dir, output_dir)
    sys.exit(0 if success else 1)
