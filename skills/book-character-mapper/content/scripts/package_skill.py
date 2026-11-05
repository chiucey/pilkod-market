#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包脚本 - 生成可分发的 .skill 文件

功能：
1. 验证技能结构完整性
2. 创建 ZIP 压缩包
3. 生成 .skill 元数据文件
4. 输出打包报告
"""

import os
import json
import zipfile
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any

# 添加父目录到路径以便导入验证脚本
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.quick_validate import validate_skill


def get_included_files(skill_path: str) -> List[str]:
    """
    获取应包含在包中的文件列表
    排除：构建产物、临时文件、隐藏文件
    """
    excluded_patterns = [
        '__pycache__', '.git', '.DS_Store', '*.pyc', '*.pyo',
        '.venv', 'node_modules', '.pytest_cache'
    ]

    included = []

    for root, dirs, files in os.walk(skill_path):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'node_modules']]

        for file in files:
            # 排除隐藏文件和构建产物
            if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.log')):
                continue

            # 跳过 scripts 目录中的测试文件（保留验证和打包脚本）
            rel_path = os.path.relpath(os.path.join(root, file), skill_path)
            if rel_path.startswith('scripts/') and not (rel_path.endswith('quick_validate.py') or rel_path.endswith('package_skill.py')):
                continue

            included.append(rel_path)

    return sorted(included)


def create_package(skill_path: str, output_dir: str = None) -> Tuple[bool, str, Dict[str, Any]]:
    """
    创建技能打包文件
    返回: (是否成功, 输出路径, 打包元数据)
    """
    # 验证技能
    valid, errors = validate_skill(skill_path)
    if not valid:
        error_msgs = [str(e) for e in errors if e.level == "error"]
        return False, "", {"error": "Validation failed", "details": error_msgs}

    # 获取技能信息
    skill_name = os.path.basename(skill_path)

    with open(os.path.join(skill_path, '_meta.json'), 'r') as f:
        meta = json.load(f)

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_name = f"{skill_name}-{meta['version']}-{timestamp}.skill"
    output_path = os.path.join(output_dir, output_name)

    # 创建 ZIP 包
    files = get_included_files(skill_path)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            full_path = os.path.join(skill_path, file)
            arcname = os.path.join(skill_name, file)
            zf.write(full_path, arcname)

    # 收集打包元数据
    package_info = {
        "package_name": output_name,
        "package_path": output_path,
        "skill_id": meta.get('id', ''),
        "skill_version": meta.get('version', ''),
        "file_count": len(files),
        "files": files,
        "created_at": datetime.now().isoformat(),
        "size_bytes": os.path.getsize(output_path)
    }

    return True, output_path, package_info


def verify_package(package_path: str, skill_name: str) -> Tuple[bool, List[str]]:
    """
    验证打包文件的完整性
    返回: (是否有效, 问题列表)
    """
    issues = []

    if not os.path.exists(package_path):
        issues.append(f"Package file not found: {package_path}")
        return False, issues

    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            # 检查必要文件
            required = [f'{skill_name}/SKILL.md', f'{skill_name}/_meta.json']
            names = zf.namelist()

            for req in required:
                if req not in names:
                    issues.append(f"Missing required file in package: {req}")

            # 验证 JSON 格式
            for name in names:
                if name.endswith('.json'):
                    try:
                        data = zf.read(name).decode('utf-8')
                        json.loads(data)
                    except json.JSONDecodeError as e:
                        issues.append(f"Invalid JSON in {name}: {e}")

    except zipfile.BadZipFile:
        issues.append("Invalid ZIP format")
        return False, issues

    return len(issues) == 0, issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    print("=" * 50)

    # 创建打包
    success, output_path, info = create_package(skill_path, output_dir)

    if not success:
        print(f"\n✗ Packaging FAILED")
        print(f"Reason: {info.get('error', 'Unknown error')}")
        if 'details' in info:
            print("\nDetails:")
            for detail in info['details']:
                print(f"  - {detail}")
        sys.exit(1)

    # 验证包
    skill_name = os.path.basename(skill_path)
    valid, issues = verify_package(output_path, skill_name)

    if not valid:
        print(f"\n⚠ Package created but verification issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n✓ Package verified successfully")

    # 输出报告
    print("\n" + "=" * 50)
    print("PACKAGE REPORT")
    print("=" * 50)
    print(f"Output: {output_path}")
    print(f"Skill ID: {info['skill_id']}")
    print(f"Version: {info['skill_version']}")
    print(f"Files: {info['file_count']}")
    print(f"Size: {info['size_bytes']:,} bytes")
    print(f"Created: {info['created_at']}")

    print("\nIncluded files:")
    for f in info['files']:
        print(f"  + {f}")

    print("\n" + "=" * 50)
    print(f"✓ Packaging SUCCESSFUL")
    print(f"Package location: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
