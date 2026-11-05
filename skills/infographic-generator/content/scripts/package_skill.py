#!/usr/bin/env python3
"""
技能打包脚本 - 将技能文件夹打包为.skill文件
"""

import os
import sys
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为.skill文件"""
    skill_dir = Path(skill_path)

    if not skill_dir.exists():
        print(f"{RED}Error: Skill directory not found: {skill_dir}{RESET}")
        sys.exit(1)

    # 读取meta获取名称
    meta_file = skill_dir / '_meta.json'
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        skill_name = meta.get('id', skill_dir.name)
        version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_dir.name
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_name = f"{skill_dir.name}_{version}_{timestamp}.skill"

    if output_dir:
        output_path = Path(output_dir) / output_name
    else:
        output_path = skill_dir.parent / output_name

    # 创建zip包
    print(f"{BLUE}Packaging skill: {skill_dir.name}{RESET}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除隐藏文件和临时文件
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n{GREEN}✓ Skill packaged: {output_path}{RESET}")
    return str(output_path)

def extract_skill(skill_file: str, output_dir: str = None) -> bool:
    """解压.skill文件"""
    skill_path = Path(skill_file)

    if not skill_path.exists():
        print(f"{RED}Error: Skill file not found: {skill_path}{RESET}")
        return False

    if output_dir:
        extract_to = Path(output_dir)
    else:
        # 解压到同名文件夹
        extract_to = skill_path.parent / skill_path.stem

    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(skill_path, 'r') as zf:
        zf.extractall(extract_to)
        print(f"{GREEN}✓ Skill extracted to: {extract_to}{RESET}")

    return True

def list_skill_contents(skill_file: str):
    """列出.skill文件内容"""
    skill_path = Path(skill_file)

    if not skill_path.exists():
        print(f"{RED}Error: Skill file not found: {skill_path}{RESET}")
        return

    print(f"\n{BLUE}Contents of {skill_path.name}:{RESET}\n")

    with zipfile.ZipFile(skill_path, 'r') as zf:
        for info in zf.infolist():
            size = info.file_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size/1024/1024:.1f}MB"
            print(f"  {info.filename:<40} {size_str:>10}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  package: python package_skill.py <skill_dir> [output_dir]")
        print("  extract: python package_skill.py -x <skill_file> [output_dir]")
        print("  list:    python package_skill.py -l <skill_file>")
        sys.exit(1)

    if sys.argv[1] == '-x':
        extract_skill(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif sys.argv[1] == '-l':
        list_skill_contents(sys.argv[2])
    else:
        package_skill(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
