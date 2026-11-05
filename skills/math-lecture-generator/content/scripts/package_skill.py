#!/usr/bin/env python3
"""
打包脚本 - 将数学课件生成器技能打包为 .skill 文件
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_dir: str, output_dir: str = None):
    """
    打包技能为 .skill 文件

    Args:
        skill_dir: 技能目录路径
        output_dir: 输出目录路径，默认为 skill_dir 的父目录
    """
    skill_path = Path(skill_dir).resolve()
    skill_name = skill_path.name

    if not skill_path.exists():
        print(f"❌ 技能目录不存在: {skill_path}")
        return None

    # 确定输出目录
    if output_dir:
        output_path = Path(output_dir).resolve()
    else:
        output_path = skill_path.parent

    # 读取 meta 信息
    meta_file = skill_path / '_meta.json'
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        skill_id = meta.get('id', 'unknown')
        version = meta.get('version', '1.0.0')
    else:
        skill_id = 'unknown'
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_path / f"{skill_name}_{version}_{timestamp}.skill"

    # 打包
    print(f"📦 正在打包技能: {skill_name}")
    print(f"   技能ID: {skill_id}")
    print(f"   版本: {version}")
    print(f"   输出: {output_file}")

    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 遍历目录，收集所有文件
            for root, dirs, files in os.walk(skill_path):
                # 排除隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(skill_path)

                    # 安全检查：禁止符号链接逃逸
                    if file_path.is_symlink():
                        print(f"   ⚠️ 跳过符号链接: {arcname}")
                        continue

                    zf.write(file_path, arcname)
                    print(f"   ✅ 添加: {arcname}")

        print(f"\n✨ 打包完成！")
        print(f"📁 文件位置: {output_file}")
        print(f"📊 文件大小: {output_file.stat().st_size / 1024:.2f} KB")

        return str(output_file)

    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return None


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir> [output_dir]")
        print("示例: python package_skill.py ./math-lecture-generator")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = package_skill(skill_dir, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()