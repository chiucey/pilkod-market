#!/usr/bin/env python3
"""
数学动画生成器 - 打包脚本
将技能打包为.skill文件用于分发
"""

import os
import re
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SKILL_DIR.parent

def extract_name_from_skill_md():
    """从SKILL.md的frontmatter中提取name字段"""
    skill_md_path = SKILL_DIR / 'SKILL.md'
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            return name_match.group(1).strip()

    return None

def scan_skill_files():
    """扫描技能目录，收集所有文件"""
    files = []
    for root, dirs, filenames in os.walk(SKILL_DIR):
        # 跳过隐藏目录和__pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for filename in filenames:
            if filename.startswith('.') or filename.endswith('.pyc'):
                continue
            filepath = Path(root) / filename
            rel_path = filepath.relative_to(SKILL_DIR)
            files.append({
                'path': str(rel_path),
                'full_path': str(filepath)
            })
    return files

def validate_skill():
    """验证技能包完整性"""
    required_files = ['SKILL.md', '_meta.json']
    missing = []

    for filename in required_files:
        if not (SKILL_DIR / filename).exists():
            missing.append(filename)

    if missing:
        raise ValueError(f"缺少必需文件: {', '.join(missing)}")

    # 验证_meta.json
    with open(SKILL_DIR / '_meta.json', 'r') as f:
        meta = json.load(f)

    if 'id' not in meta or 'version' not in meta:
        raise ValueError("_meta.json 必须包含 id 和 version 字段")

    return meta

def create_package():
    """创建技能包"""
    print("=" * 50)
    print("数学动画生成器 - 打包工具")
    print("=" * 50)
    print()

    # 验证技能
    print("[1/4] 验证技能完整性...")
    meta = validate_skill()
    print(f"    ✓ 技能ID: {meta['id']}")
    print(f"    ✓ 版本: {meta['version']}")
    print()

    # 扫描文件
    print("[2/4] 扫描技能文件...")
    files = scan_skill_files()
    print(f"    ✓ 找到 {len(files)} 个文件:")
    for f in files:
        print(f"      - {f['path']}")
    print()

    # 创建输出目录
    print("[3/4] 准备打包...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 生成包文件名
    skill_name = extract_name_from_skill_md() or 'unknown'
    version = meta['version']
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f"{skill_name}_{version}_{timestamp}.skill"
    output_path = OUTPUT_DIR / output_filename

    # 创建zip包
    print("[4/4] 创建技能包...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f['full_path'], f['path'])
            print(f"    + {f['path']}")

    print()
    print("=" * 50)
    print(f"✓ 打包完成！")
    print(f"  输出文件: {output_path}")
    print(f"  文件大小: {output_path.stat().st_size / 1024:.1f} KB")
    print("=" * 50)

    return str(output_path)

def main():
    try:
        output_path = create_package()
        return 0
    except Exception as e:
        print()
        print("=" * 50)
        print(f"✗ 打包失败: {e}")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
