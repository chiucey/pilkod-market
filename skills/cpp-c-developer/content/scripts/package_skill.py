#!/usr/bin/env python3
"""
C/C++ Developer Skill - Package Script
打包技能为可分发的 .skill 文件
"""

import os
import sys
import json
import zipfile
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

def get_skill_name(skill_path: str) -> str:
    """从 SKILL.md frontmatter 获取技能名称"""
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        return None

    content = skill_md.read_text(encoding='utf-8')
    lines = content.split('\n')

    if lines[0].strip() != '---':
        return None

    end_idx = content.index('---', 3)
    frontmatter_text = content[3:end_idx].strip()

    for line in frontmatter_text.split('\n'):
        if line.startswith('name:'):
            return line.split(':', 1)[1].strip()
    return None

def get_meta(skill_path: str) -> dict:
    """获取元数据"""
    meta_file = Path(skill_path) / "_meta.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text(encoding='utf-8'))
    return {}

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为 .skill 文件"""
    skill_dir = Path(skill_path)
    skill_name = get_skill_name(skill_path)

    if not skill_name:
        print_error("无法从 SKILL.md 获取技能名称")
        return None

    meta = get_meta(skill_path)
    version = meta.get('version', '1.0.0')

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_name = f"{skill_name}_{version}_{timestamp}.skill"
    output_path = Path(output_dir) / output_name

    print_info(f"打包技能: {skill_name}")
    print_info(f"版本: {version}")
    print_info(f"输出: {output_path}")

    # 创建 zip 文件
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 遍历技能目录中的所有文件
            for file_path in skill_dir.rglob('*'):
                if file_path.is_file():
                    # 跳过隐藏文件和 __pycache__
                    if any(part.startswith('.') or part == '__pycache__'
                           for part in file_path.parts):
                        continue

                    arcname = file_path.relative_to(skill_dir)
                    zf.write(file_path, arcname)
                    print_info(f"  添加: {arcname}")

        print_success(f"打包完成: {output_path}")
        return str(output_path)

    except Exception as e:
        print_error(f"打包失败: {e}")
        return None

def verify_package(skill_path: str) -> bool:
    """验证生成的包"""
    print_info("验证打包结果...")

    # 读取原始 SKILL.md 的 frontmatter
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        return False

    original_content = skill_md.read_text(encoding='utf-8')

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for req_file in required_files:
        if not (Path(skill_path) / req_file).exists():
            print_error(f"缺少必需文件: {req_file}")
            return False

    print_success("打包验证通过")
    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print("="*60)
    print("C/C++ Developer Skill - 打包工具")
    print("="*60)

    if not verify_package(skill_path):
        sys.exit(1)

    output_path = package_skill(skill_path, output_dir)

    if output_path:
        print("\n" + "="*60)
        print(f"技能已成功打包: {output_path}")
        print("="*60)
    else:
        print_error("打包失败")
        sys.exit(1)
