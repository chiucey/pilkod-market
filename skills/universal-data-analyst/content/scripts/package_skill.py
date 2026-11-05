#!/usr/bin/env python3
"""
Package Skill - 技能打包脚本

将技能打包为 .skill 文件（zip 格式）
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


def get_skill_meta(skill_path: Path) -> dict:
    """获取技能元数据"""
    meta_file = skill_path / "_meta.json"

    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {
        "name": skill_path.name,
        "version": "1.0.0"
    }


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """
    打包技能为 .skill 文件

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录，默认与技能目录同级

    Returns:
        Path: 生成的 .skill 文件路径
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    # 获取元数据
    meta = get_skill_meta(skill_path)

    # 确定输出路径
    if output_dir is None:
        output_dir = skill_path.parent

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    skill_name = meta.get("name", skill_path.name)
    skill_version = meta.get("version", "1.0.0")

    output_file = output_dir / f"{skill_name}-{skill_version}.skill"

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 复制技能文件（排除 __pycache__ 等）
        exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            '*.egg-info',
            '.pytest_cache',
            'node_modules'
        ]

        def should_include(path: Path) -> bool:
            name = path.name
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return False
                elif name == pattern:
                    return False
            return True

        # 复制文件
        for item in skill_path.rglob('*'):
            if not should_include(item):
                continue

            rel_path = item.relative_to(skill_path)
            dest_path = temp_path / rel_path

            if item.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)

        # 创建 zip 文件
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in temp_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zf.write(file_path, arcname)

    print(f"\n✅ 技能打包完成: {output_file}")
    print(f"   技能名称: {skill_name}")
    print(f"   版本: {skill_version}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")

    return output_file


def list_skill_contents(skill_file: Path) -> list:
    """列出 .skill 文件内容"""
    with zipfile.ZipFile(skill_file, 'r') as zf:
        return zf.namelist()


def verify_skill(skill_file: Path) -> bool:
    """验证 .skill 文件完整性"""
    try:
        with zipfile.ZipFile(skill_file, 'r') as zf:
            # 检查文件列表
            names = zf.namelist()

            # 必须包含的文件
            required = ['SKILL.md', '_meta.json']
            for r in required:
                if not any(r in n for n in names):
                    print(f"❌ 缺少必需文件: {r}")
                    return False

            # 验证 JSON 格式
            for name in names:
                if name.endswith('.json'):
                    try:
                        zf.read(name)
                    except:
                        print(f"❌ JSON 格式错误: {name}")
                        return False

        return True

    except zipfile.BadZipFile:
        print("❌ 文件不是有效的 ZIP 格式")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = Path.cwd()
    else:
        skill_path = Path(sys.argv[1])

    print(f"\n{'='*60}")
    print(f"Universal Data Analyst - 技能打包")
    print(f"技能路径: {skill_path}")
    print(f"{'='*60}")

    skill_path = skill_path.resolve()

    if not skill_path.exists():
        print(f"\n❌ 技能目录不存在: {skill_path}")
        sys.exit(1)

    # 打包
    try:
        output_file = package_skill(skill_path)

        # 验证
        print(f"\n{'='*60}")
        print(f"验证打包结果...")
        print(f"{'='*60}")

        if verify_skill(output_file):
            print(f"\n✅ 技能包验证通过")
            print(f"\n📦 文件位置: {output_file}")
            print(f"\n包含文件列表:")
            for name in list_skill_contents(output_file):
                print(f"   - {name}")

        return 0

    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
