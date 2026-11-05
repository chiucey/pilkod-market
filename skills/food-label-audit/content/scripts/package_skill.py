#!/usr/bin/env python3
"""
食品标签审核技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import json
import shutil
import sys
from pathlib import Path
import zipfile
import datetime

# 定义颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def log_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def is_safe_path(path, base_dir):
    """检查路径安全性，防止符号链接逃逸"""
    abs_base = Path(base_dir).resolve()
    abs_path = (Path(base_dir) / path).resolve()
    return abs_path.is_relative_to(abs_base)

def scan_directory(dir_path, base_dir, exclude_patterns=None):
    """扫描目录生成文件列表"""
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__', '.pyc', '.git', '.DS_Store',
            '*.pyc', 'node_modules', '.venv', 'venv'
        ]

    files = []
    for root, dirs, filenames in os.walk(dir_path):
        # 过滤排除的目录
        dirs[:] = [d for d in dirs if not any(
            pattern.rstrip('*') in d for pattern in exclude_patterns
        )]

        for filename in filenames:
            # 跳过排除的文件
            if any(
                pattern.rstrip('*') in filename
                for pattern in exclude_patterns
            ):
                continue

            file_path = Path(root) / filename
            rel_path = file_path.relative_to(dir_path)

            if is_safe_path(rel_path, base_dir):
                files.append(rel_path)

    return files

def create_package(skill_dir, output_path=None):
    """创建技能包"""
    skill_name = skill_dir.name

    print(f"\n{'='*60}")
    log_info(f"打包食品标签审核技能: {skill_name}")
    print(f"{'='*60}\n")

    # 读取元数据
    meta_path = skill_dir / '_meta.json'
    if not meta_path.exists():
        log_error("_meta.json 不存在")
        return False

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    log_info(f"技能 ID: {skill_id}")
    log_info(f"版本: {version}")

    # 扫描文件
    log_info("\n扫描技能文件...")
    files = scan_directory(skill_dir, skill_dir)

    if not files:
        log_error("未找到任何文件")
        return False

    log_success(f"找到 {len(files)} 个文件")

    # 显示文件列表
    print("\n文件列表:")
    for f in sorted(files):
        print(f"  - {f}")

    # 确定输出路径
    if output_path is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        output_path = skill_dir.parent / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建压缩包
    log_info(f"\n创建技能包: {output_path}")

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                full_path = skill_dir / file_path
                zf.write(full_path, file_path)

        log_success(f"技能包创建成功: {output_path}")

        # 验证包内容
        log_info("\n验证包内容...")
        with zipfile.ZipFile(output_path, 'r') as zf:
            names = zf.namelist()
            if 'SKILL.md' in names and '_meta.json' in names:
                log_success("包内容验证通过（包含必填文件）")
            else:
                log_warning("包可能缺少必填文件")

        return True

    except Exception as e:
        log_error(f"打包失败: {e}")
        return False

def main():
    # 获取技能目录
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    # 处理命令行参数
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        output_path = None

    # 执行打包
    success = create_package(skill_dir, output_path)

    print(f"\n{'='*60}")
    if success:
        log_success("打包完成！")
        return 0
    else:
        log_error("打包失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())