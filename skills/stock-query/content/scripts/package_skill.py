#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查询技能打包脚本
将技能打包为 .skill 文件用于发布
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# 颜色定义
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def log_info(msg):
    print(f"  {msg}")

def log_step(msg):
    print(f"\n{CYAN}>>> {msg}{RESET}")

def clean_directory(skill_dir):
    """清理不需要的文件和目录"""
    log_step("清理构建产物")

    patterns_to_remove = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.pytest_cache',
        '.git',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        'node_modules',
        '.venv',
        'venv'
    ]

    for root, dirs, files in os.walk(skill_dir):
        for pattern in patterns_to_remove:
            if '*' in pattern:
                # 处理通配符
                ext = pattern.replace('*', '')
                for f in files:
                    if f.endswith(ext):
                        try:
                            os.remove(os.path.join(root, f))
                            log_info(f"已删除: {os.path.relpath(os.path.join(root, f), skill_dir)}")
                        except:
                            pass
            else:
                # 处理目录名
                if pattern in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, pattern))
                        log_info(f"已删除目录: {os.path.relpath(os.path.join(root, pattern), skill_dir)}")
                    except:
                        pass

def collect_files(skill_dir):
    """收集要打包的文件"""
    log_step("收集打包文件")

    files_to_package = []

    for root, dirs, files in os.walk(skill_dir):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']]

        for file in files:
            # 排除构建产物
            if file in ['.DS_Store', 'Thumbs.db']:
                continue
            if file.endswith(('.pyc', '.pyo', '.log')):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, skill_dir)
            files_to_package.append(rel_path)
            log_info(f"  + {rel_path}")

    return files_to_package

def create_package(skill_dir, output_path, files):
    """创建 .skill 包"""
    log_step("创建技能包")

    skill_name = os.path.basename(skill_dir)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            file_path = os.path.join(skill_dir, file)
            zf.write(file_path, file)
            log_info(f"  添加: {file}")

    log_success(f"技能包已创建: {output_path}")

def verify_package(output_path):
    """验证包内容"""
    log_step("验证包内容")

    with zipfile.ZipFile(output_path, 'r') as zf:
        file_list = zf.namelist()

        # 检查必需文件
        required_files = ['SKILL.md', '_meta.json']
        missing = []

        for req in required_files:
            if req not in file_list:
                missing.append(req)

        if missing:
            log_error(f"缺少必需文件: {', '.join(missing)}")
            return False

        log_success("必需文件完整")

        # 列出所有文件
        log_info(f"包内文件数: {len(file_list)}")

        # 验证没有危险文件
        dangerous = [f for f in file_list if any(x in f for x in ['password', 'secret', '.env', '.key'])]
        if dangerous:
            log_warning(f"发现可能的敏感文件: {dangerous}")

        # 验证 JSON 文件可解析
        for json_file in ['_meta.json']:
            if json_file in file_list:
                try:
                    json.loads(zf.read(json_file).decode('utf-8'))
                    log_success(f"{json_file} 格式正确")
                except:
                    log_error(f"{json_file} 格式错误")
                    return False

    return True

def get_package_info(output_path, skill_dir):
    """获取包信息"""
    with zipfile.ZipFile(output_path, 'r') as zf:
        meta = json.loads(zf.read('_meta.json').decode('utf-8'))

        skill_md = zf.read('SKILL.md').decode('utf-8')

        # 提取 description
        import re
        desc_match = re.search(r'^description:\s*(.+)$', skill_md, re.MULTILINE)
        description = desc_match.group(1).strip() if desc_match else ""

    return {
        'name': meta.get('name', 'unknown'),
        'id': meta.get('id', 'unknown'),
        'version': meta.get('version', '1.0.0'),
        'description': description,
        'file': output_path,
        'size': os.path.getsize(output_path),
        'files': len(zf.namelist())
    }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill-directory> [output-directory]")
        print("示例: python package_skill.py stock-query")
        print("      python package_skill.py stock-query ./output")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    # 转换为绝对路径
    skill_dir = os.path.abspath(skill_dir)
    output_dir = os.path.abspath(output_dir)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("股票查询技能 - 打包工具")
    print("=" * 60)
    print(f"技能目录: {skill_dir}")
    print(f"输出目录: {output_dir}")

    # 检查技能目录是否存在
    if not os.path.isdir(skill_dir):
        log_error(f"技能目录不存在: {skill_dir}")
        sys.exit(1)

    # 检查必需文件
    if not os.path.exists(os.path.join(skill_dir, 'SKILL.md')):
        log_error("SKILL.md 不存在")
        sys.exit(1)

    if not os.path.exists(os.path.join(skill_dir, '_meta.json')):
        log_error("_meta.json 不存在")
        sys.exit(1)

    # 清理
    clean_directory(skill_dir)

    # 收集文件
    files = collect_files(skill_dir)

    if not files:
        log_error("没有找到要打包的文件")
        sys.exit(1)

    # 创建包名
    skill_name = os.path.basename(skill_dir)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"{skill_name}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建包
    create_package(skill_dir, output_path, files)

    # 验证包
    if not verify_package(output_path):
        log_error("包验证失败")
        sys.exit(1)

    # 输出信息
    info = get_package_info(output_path, skill_dir)

    print("\n" + "=" * 60)
    print("打包完成！")
    print("=" * 60)
    print(f"技能名称: {info['name']}")
    print(f"技能 ID: {info['id']}")
    print(f"版本: {info['version']}")
    print(f"描述: {info['description']}")
    print(f"包文件: {output_path}")
    print(f"包大小: {info['size'] / 1024:.2f} KB")
    print(f"包含文件: {info['files']} 个")
    print()

    log_success("技能已成功打包！")

    return 0

if __name__ == "__main__":
    sys.exit(main())
