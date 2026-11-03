#!/usr/bin/env python3
"""
Content Checker 技能打包脚本
将技能打包为 .skill 文件用于分发
"""

import os
import json
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime


def get_files_to_package(skill_path: Path) -> list:
    """获取需要打包的文件"""
    files = []

    # 需要包含的文件
    required_files = [
        'SKILL.md',
        '_meta.json',
    ]

    # 可选的目录
    optional_dirs = [
        'references',
        'scripts',
        'assets',
    ]

    # 检查必需文件
    for f in required_files:
        file_path = skill_path / f
        if file_path.exists():
            files.append(file_path)
        else:
            print(f"⚠️  警告: 缺少必需文件 {f}")

    # 检查可选目录
    for d in optional_dirs:
        dir_path = skill_path / d
        if dir_path.exists() and dir_path.is_dir():
            for item in dir_path.rglob('*'):
                if item.is_file():
                    # 跳过测试文件
                    if 'test_' in item.name or '_test.' in item.name:
                        continue
                    files.append(item)

    return files


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        print(f"❌ 错误: 技能路径不存在: {skill_path}")
        return None

    # 确定输出目录
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent / 'dist'

    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取 meta 信息
    meta_path = skill_path / '_meta.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        skill_name = meta.get('name', skill_path.name)
        skill_version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        skill_version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_dir / f"{skill_name}-{skill_version}.skill"

    # 获取要打包的文件
    files_to_package = get_files_to_package(skill_path)

    if not files_to_package:
        print("❌ 错误: 没有找到需要打包的文件")
        return None

    print(f"📦 打包技能: {skill_name} v{skill_version}")
    print(f"📁 输出文件: {output_file}")
    print(f"📋 包含文件数: {len(files_to_package)}")

    # 创建 .skill 文件 (实际上是 .zip)
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files_to_package:
            # 计算相对路径
            rel_path = file_path.relative_to(skill_path)

            # 安全检查: 不允许符号链接逃逸
            if '..' in str(rel_path):
                print(f"⚠️  跳过不安全的路径: {rel_path}")
                continue

            # 添加文件
            zf.write(file_path, rel_path)
            print(f"  + {rel_path}")

    # 验证打包结果
    with zipfile.ZipFile(output_file, 'r') as zf:
        file_list = zf.namelist()
        print(f"\n✅ 打包完成!")
        print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")
        print(f"   包含项目: {len(file_list)} 个")

    return str(output_file)


def list_skill_contents(skill_path: str):
    """列出技能内容"""
    skill_path = Path(skill_path)

    print(f"\n📂 技能内容: {skill_path.name}")
    print("=" * 50)

    # 必需文件
    print("\n📄 必需文件:")
    for f in ['SKILL.md', '_meta.json']:
        path = skill_path / f
        if path.exists():
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f}")

    # 可选目录
    for d in ['references', 'scripts', 'assets']:
        dir_path = skill_path / d
        if dir_path.exists() and dir_path.is_dir():
            items = list(dir_path.rglob('*'))
            files = [i for i in items if i.is_file()]
            print(f"\n📁 {d}/ ({len(files)} 个文件)")
            for f in files:
                rel = f.relative_to(dir_path)
                print(f"  - {rel}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py ./content-checker ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    # 列出内容
    list_skill_contents(skill_path)

    # 打包
    output_file = package_skill(skill_path, output_dir)

    if output_file:
        print(f"\n🎉 技能已打包到: {output_file}")
    else:
        sys.exit(1)
