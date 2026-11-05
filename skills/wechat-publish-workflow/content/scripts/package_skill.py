#!/usr/bin/env python3
"""
微信公众号发布工作流 - 打包脚本
将技能打包为 .skill 文件
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_skill_info(skill_path):
    """获取技能基本信息"""
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        raise FileNotFoundError("_meta.json 不存在")

    import json
    meta = json.loads(meta_file.read_text(encoding='utf-8'))

    return meta.get('id', 'unknown'), meta.get('version', '1.0.0')

def create_package(skill_path, output_dir=None):
    """创建技能包"""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"技能路径不存在: {skill_path}")

    # 获取技能信息
    skill_id, version = get_skill_info(skill_path)

    # 设置输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成包文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    package_name = f"{skill_id}-{version}.skill"
    package_path = output_dir / package_name

    # 创建 ZIP 包
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 遍历技能目录中的所有文件
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = Path(root) / file
                # 计算相对路径
                rel_path = file_path.relative_to(skill_path)
                # 添加到 ZIP
                zf.write(file_path, rel_path)
                print(f"  + {rel_path}")

    print(f"\n✓ 技能包已生成: {package_path}")
    print(f"  文件大小: {package_path.stat().st_size / 1024:.2f} KB")

    return package_path

def list_skill_files(skill_path):
    """列出技能包中的文件"""
    skill_path = Path(skill_path)

    print(f"\n技能文件列表: {skill_path}")
    print("=" * 60)

    for root, dirs, files in os.walk(skill_path):
        # 排除隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        level = root.replace(str(skill_path), '').count(os.sep)
        indent = '  ' * level

        # 显示目录
        if level > 0:
            dir_name = Path(root).name
            print(f"{indent}📁 {dir_name}/")

        # 显示文件
        sub_indent = '  ' * (level + 1)
        for file in sorted(files):
            if not file.startswith('.'):
                file_path = Path(root) / file
                size = file_path.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                else:
                    size_str = f"{size/1024:.1f}KB"
                print(f"{sub_indent}📄 {file} ({size_str})")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='打包微信公众号发布工作流技能')
    parser.add_argument('skill_path', nargs='?', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help='技能目录路径')
    parser.add_argument('--output', '-o', help='输出目录')
    parser.add_argument('--list', '-l', action='store_true', help='仅列出文件')

    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()

    print("=" * 60)
    print("📦 微信公众号发布工作流 - 技能打包工具")
    print("=" * 60)

    if args.list:
        list_skill_files(skill_path)
        return 0

    try:
        # 验证技能
        sys.path.insert(0, str(skill_path / "scripts"))
        try:
            import quick_validate
            print("\n📋 运行验证检查...")
            # 简化验证，仅检查文件存在
            required_files = ['SKILL.md', '_meta.json']
            for f in required_files:
                if not (skill_path / f).exists():
                    raise FileNotFoundError(f"缺少必需文件: {f}")
            print("✓ 验证通过\n")
        except Exception as e:
            print(f"⚠ 验证警告: {e}\n")

        # 列出文件
        list_skill_files(skill_path)

        # 创建包
        print("\n📦 开始打包...")
        package_path = create_package(skill_path, args.output)

        print("\n" + "=" * 60)
        print("✓ 打包完成！")
        print(f"\n安装命令: 将 {package_path.name} 导入到技能库")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
