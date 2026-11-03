#!/usr/bin/env python3
"""
Auto-Updater Skill Packaging Script
将技能打包为可分发的 .skill 文件
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


def create_package(skill_path: Path, output_dir: Path) -> tuple[bool, str]:
    """创建技能包"""
    skill_name = skill_path.name

    # 验证必需文件
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        file_path = skill_path / filename
        if not file_path.exists():
            return False, f"缺少必需文件: {filename}"

    # 读取元数据
    meta_file = skill_path / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # 生成包文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}-{version}-{timestamp}.skill"
    package_path = output_dir / package_name

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建 ZIP 包
    try:
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加所有文件
            for root, dirs, files in os.walk(skill_path):
                # 排除隐藏文件和目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)

        return True, str(package_path)

    except Exception as e:
        return False, f"打包失败: {str(e)}"


def verify_package(package_path: Path) -> tuple[bool, str]:
    """验证包内容"""
    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            # 检查必需文件
            file_list = zf.namelist()

            required_files = ['SKILL.md', '_meta.json']
            for filename in required_files:
                if filename not in file_list:
                    return False, f"包内缺少文件: {filename}"

            # 验证 JSON 文件
            meta_content = zf.read('_meta.json')
            json.loads(meta_content)

            skill_content = zf.read('SKILL.md')
            if not skill_content.startswith(b'---'):
                return False, "SKILL.md 必须以 YAML frontmatter 开头"

            return True, "包验证通过"

    except zipfile.BadZipFile:
        return False, "无效的 ZIP 文件"
    except Exception as e:
        return False, f"验证失败: {str(e)}"


def main():
    """主打包流程"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <技能目录路径> [输出目录]")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"错误: 目录不存在: {skill_path}")
        sys.exit(1)

    # 默认输出到当前目录的 output 文件夹
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_path.name

    print(f"正在打包技能: {skill_name}")
    print("-" * 50)

    # 创建包
    success, result = create_package(skill_path, output_dir)

    if not success:
        print(f"错误: {result}")
        sys.exit(1)

    package_path = Path(result)
    print(f"✓ 包创建成功: {package_path.name}")

    # 验证包
    print("-" * 50)
    success, message = verify_package(package_path)
    print(f"{'✓' if success else '✗'} 包验证: {message}")

    if success:
        print("-" * 50)
        print("打包完成!")
        print(f"包路径: {package_path}")
        print(f"包大小: {package_path.stat().st_size / 1024:.2f} KB")
        sys.exit(0)
    else:
        print("打包验证失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
