#!/usr/bin/env python3
"""
打包脚本 - 将技能打包为 .skill 文件
"""
import os
import sys
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def get_skill_info(skill_path):
    """从 SKILL.md 和 _meta.json 获取技能信息"""
    skill_path = Path(skill_path)

    # 读取 _meta.json
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        skill_id = meta.get('id', 'unknown')
        version = meta.get('version', '1.0.0')
    else:
        skill_id = 'unknown'
        version = '1.0.0'

    # 从 SKILL.md 提取名称
    skill_file = skill_path / "SKILL.md"
    if skill_file.exists():
        content = skill_file.read_text(encoding='utf-8')
        # 提取 frontmatter 中的 name
        import re
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else skill_path.name
    else:
        name = skill_path.name

    return name, skill_id, version

def package_skill(skill_path, output_dir=None):
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        print_error(f"Skill path does not exist: {skill_path}")
        return None

    # 获取技能信息
    name, skill_id, version = get_skill_info(skill_path)

    print_info(f"Packaging skill: {name}")
    print_info(f"ID: {skill_id}, Version: {version}")

    # 设置输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    output_file = output_dir / f"{name}.skill"

    # 创建 .skill 文件 (实际上是一个 zip 文件)
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 遍历技能目录
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(skill_path)

                    # 排除 __pycache__ 和 .pyc 文件
                    if '__pycache__' in str(arcname) or str(arcname).endswith('.pyc'):
                        continue

                    zf.write(file_path, arcname)

        print_success(f"Package created: {output_file}")

        # 显示包内容
        print_info("Package contents:")
        with zipfile.ZipFile(output_file, 'r') as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    print(f"  - {info.filename}")

        # 输出文件大小
        size = output_file.stat().st_size
        print_info(f"Package size: {size} bytes")

        return str(output_file)

    except Exception as e:
        print_error(f"Failed to create package: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 50)
    print("Skill Packager")
    print("=" * 50)

    result = package_skill(skill_path, output_dir)

    if result:
        print_success("Packaging completed successfully!")
        print(f"\nSkill file: {result}")
    else:
        print_error("Packaging failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
