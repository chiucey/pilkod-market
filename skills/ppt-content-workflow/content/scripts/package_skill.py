#!/usr/bin/env python3
"""
PPT内容工作流技能打包脚本
将技能打包为可分发的.skill文件
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


def scan_directory(path, exclude_patterns=None):
    """扫描目录下的所有文件，排除指定模式"""
    if exclude_patterns is None:
        exclude_patterns = [
            "__pycache__", "*.pyc", ".git", ".DS_Store",
            "node_modules", ".venv", "venv", ".idea"
        ]

    files = []
    for item in path.rglob("*"):
        if item.is_file():
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(item):
                    should_exclude = True
                    break

            if not should_exclude:
                # 计算相对路径
                rel_path = item.relative_to(path)
                files.append(rel_path)

    return files


def create_skill_package(skill_path, output_path=None):
    """创建.skill包"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        print(f"错误：技能目录不存在 - {skill_path}")
        return False

    # 读取meta信息
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        skill_name = skill_path.name
        skill_version = meta.get("version", "1.0.0")
    else:
        print("警告：_meta.json不存在，使用默认信息")
        skill_name = skill_path.name
        skill_version = "1.0.0"

    # 确定输出路径
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        output_path = f"{skill_name}_v{skill_version}_{timestamp}.skill"

    # 创建ZIP包
    files = scan_directory(skill_path)

    print(f"正在打包技能：{skill_name}")
    print(f"版本：{skill_version}")
    print(f"文件数量：{len(files)}")
    print("-" * 40)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = skill_path / file_path
            # 添加文件到ZIP
            zf.write(full_path, file_path)
            print(f"  + {file_path}")

    print("-" * 40)
    print(f"✅ 打包完成：{output_path}")
    print(f"   大小：{os.path.getsize(output_path) / 1024:.1f} KB")

    return True


def main():
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        # 默认当前目录
        script_dir = Path(__file__).parent.parent
        skill_path = script_dir

    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = create_skill_package(skill_path, output_path)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())