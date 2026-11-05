#!/usr/bin/env python3
"""
技能打包脚本 - 专职社群运营师
将技能打包为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(msg, color=None):
    prefix = f"{color}{Colors.BOLD}" if color else ""
    suffix = Colors.END
    print(f"{prefix}{msg}{suffix}")

def get_skill_info(skill_dir):
    """获取技能信息"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def scan_included_files(skill_dir):
    """扫描要包含的文件"""
    included = []
    excluded_dirs = {'.git', '__pycache__', '.DS_Store', 'node_modules', '.venv'}

    for root, dirs, files in os.walk(skill_dir):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file.startswith('.') or file.endswith('.pyc'):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, skill_dir)
            included.append(rel_path)

    return sorted(included)

def validate_before_pack(skill_dir):
    """打包前验证"""
    issues = []

    # 检查必需文件
    if not os.path.exists(os.path.join(skill_dir, 'SKILL.md')):
        issues.append("缺少 SKILL.md")

    if not os.path.exists(os.path.join(skill_dir, '_meta.json')):
        issues.append("缺少 _meta.json")

    # 检查 _meta.json 格式
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                issues.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                issues.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            issues.append("_meta.json 格式错误")

    return issues

def package_skill(skill_dir, output_dir=None):
    """打包技能"""

    log(f"\n📦 打包技能: {os.path.basename(skill_dir)}", Colors.BLUE)
    log("=" * 50)

    # 打包前验证
    log("\n🔍 打包前验证:", Colors.BLUE)
    issues = validate_before_pack(skill_dir)
    if issues:
        for issue in issues:
            log(f"   ❌ {issue}", Colors.RED)
        log("\n❌ 验证失败，无法打包", Colors.RED)
        return False
    log("   ✅ 验证通过")

    # 获取技能信息
    meta = get_skill_info(skill_dir)
    skill_name = os.path.basename(skill_dir)
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 生成输出路径
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_v{version}_{timestamp}.skill")

    # 创建 ZIP 归档
    log(f"\n📁 扫描文件:", Colors.BLUE)
    files_to_include = scan_included_files(skill_dir)
    for f in files_to_include:
        log(f"   + {f}")

    log(f"\n🔨 创建归档:", Colors.BLUE)
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for rel_path in files_to_include:
                full_path = os.path.join(skill_dir, rel_path)
                zf.write(full_path, rel_path)
                log(f"   + {rel_path}")

        # 获取文件大小
        size = os.path.getsize(output_file)
        log(f"\n✅ 打包完成!", Colors.GREEN)
        log(f"   输出文件: {output_file}")
        log(f"   文件大小: {size:,} bytes")
        log(f"   包含文件: {len(files_to_include)} 个")

        return True

    except Exception as e:
        log(f"\n❌ 打包失败: {e}", Colors.RED)
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)  # 回到 skill 根目录

    output_dir = None
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    success = package_skill(skill_dir, output_dir)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
