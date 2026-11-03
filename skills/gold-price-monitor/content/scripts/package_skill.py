#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包成 .skill 文件
"""

import os
import shutil
import json
import sys
from pathlib import Path


def package_skill(skill_dir: str, output_dir: str = None):
    """打包技能目录"""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    if not skill_path.exists():
        print(f"❌ 技能目录不存在: {skill_dir}")
        return False

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_path / f).exists():
            print(f"❌ 缺少必要文件: {f}")
            return False

    # 读取 meta.json
    with open(skill_path / '_meta.json', 'r') as f:
        meta = json.load(f)

    # 生成输出文件名
    version = meta.get('version', '1.0.0')
    output_name = f"{skill_name}-{version}.skill"

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / output_name
    else:
        output_file = Path(f"{skill_name}/{output_name}")

    # 创建打包目录
    package_dir = Path('/tmp/skill_package')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    # 复制文件（排除 __pycache__ 等）
    exclude_patterns = ['__pycache__', '.pyc', '.git', '.DS_Store']
    for item in skill_path.rglob('*'):
        if item.is_file():
            # 检查是否应该排除
            should_exclude = any(pattern in str(item) for pattern in exclude_patterns)
            if should_exclude:
                continue

            # 计算相对路径
            rel_path = item.relative_to(skill_path)
            dest = package_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    # 创建 zip 包
    shutil.make_archive(
        str(package_dir / skill_name),
        'zip',
        package_dir
    )

    # 重命名为 .skill
    zip_file = package_dir / f"{skill_name}.zip"
    shutil.move(str(zip_file), str(output_file))

    # 清理临时目录
    shutil.rmtree(package_dir)

    print(f"✅ 技能打包完成: {output_file}")
    print(f"   技能ID: {meta.get('id')}")
    print(f"   版本: {version}")
    return True


if __name__ == '__main__':
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    package_skill(skill_dir, output_dir)
