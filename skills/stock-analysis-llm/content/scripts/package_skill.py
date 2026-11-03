#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Analysis LLM Skill 打包脚本
将技能打包为 .skill 文件用于发布
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    """技能打包器"""

    # 打包时排除的文件/目录模式
    EXCLUDE_PATTERNS = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.git',
        '.svn',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        '.venv',
        'venv',
        'node_modules',
        '.idea',
        '.vscode',
    ]

    # 必需文件
    REQUIRED_FILES = ['SKILL.md', '_meta.json']

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path).resolve()
        self.output_path = None

    def validate_before_packaging(self) -> tuple[bool, list]:
        """打包前验证"""
        errors = []

        # 检查技能目录是否存在
        if not self.skill_path.exists():
            errors.append(f"技能目录不存在: {self.skill_path}")
            return False, errors

        if not self.skill_path.is_dir():
            errors.append(f"路径不是目录: {self.skill_path}")
            return False, errors

        # 检查必需文件
        for required in self.REQUIRED_FILES:
            file_path = self.skill_path / required
            if not file_path.exists():
                errors.append(f"缺少必需文件: {required}")

        # 检查 _meta.json 格式
        meta_file = self.skill_path / "_meta.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding='utf-8'))
                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
            except json.JSONDecodeError as e:
                errors.append(f"_meta.json 格式错误: {e}")

        # 检查 SKILL.md frontmatter
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            lines = content.split('\n')
            if not lines or lines[0].strip() != '---':
                errors.append("SKILL.md 必须以 --- 开头（frontmatter 标记）")
            else:
                # 检查是否有 name 和 description
                fm_text = content[3:content.find('---', 3)] if content.count('---') >= 2 else ""
                if 'name:' not in fm_text:
                    errors.append("SKILL.md frontmatter 缺少 name 字段")
                if 'description:' not in fm_text:
                    errors.append("SKILL.md frontmatter 缺少 description 字段")

        return len(errors) == 0, errors

    def should_exclude(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path)
        name = path.name

        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True

        return False

    def collect_files(self) -> list[tuple[Path, str]]:
        """收集要打包的文件"""
        files = []

        for root, dirs, filenames in os.walk(self.skill_path):
            root_path = Path(root)

            # 过滤目录
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

            for filename in filenames:
                file_path = root_path / filename
                if not self.should_exclude(file_path):
                    # 计算相对路径
                    rel_path = file_path.relative_to(self.skill_path)
                    files.append((file_path, str(rel_path)))

        return files

    def package(self, output_dir: str = None) -> tuple[bool, str]:
        """打包技能"""
        # 验证
        is_valid, errors = self.validate_before_packaging()
        if not is_valid:
            print("打包前验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False, ""

        # 获取版本号
        meta = json.loads((self.skill_path / "_meta.json").read_text(encoding='utf-8'))
        version = meta.get('version', 'unknown')
        skill_name = self.skill_path.name

        # 确定输出路径
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.skill_path.parent

        output_path.mkdir(parents=True, exist_ok=True)

        output_file = output_path / f"{skill_name}-{version}.skill"

        # 创建临时目录用于构建
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 收集并复制文件
            files = self.collect_files()
            print(f"收集到 {len(files)} 个文件:")

            for src_path, rel_path in files:
                dest_path = temp_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # 处理符号链接
                if src_path.is_symlink():
                    target = src_path.resolve()
                    if target.is_file():
                        shutil.copy2(target, dest_path)
                    else:
                        print(f"  跳过符号链接（目标不是文件）: {rel_path}")
                        continue
                else:
                    shutil.copy2(src_path, dest_path)

                print(f"  + {rel_path}")

            # 创建 ZIP 文件
            print(f"\n创建打包文件: {output_file}")
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for src_path, rel_path in files:
                    check_path = temp_path / rel_path
                    if check_path.exists():
                        zf.write(check_path, rel_path)

        # 验证打包文件
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"\n打包成功!")
            print(f"  文件: {output_file}")
            print(f"  大小: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

            # 验证 ZIP 内容
            with zipfile.ZipFile(output_file, 'r') as zf:
                file_list = zf.namelist()
                print(f"  包含: {len(file_list)} 个文件")

            return True, str(output_file)
        else:
            return False, ""

    def verify_package(self, package_path: str) -> tuple[bool, list]:
        """验证打包文件"""
        errors = []

        if not os.path.exists(package_path):
            errors.append("打包文件不存在")
            return False, errors

        if not package_path.endswith('.skill'):
            errors.append("打包文件扩展名应为 .skill")

        try:
            with zipfile.ZipFile(package_path, 'r') as zf:
                file_list = zf.namelist()

                # 检查必需文件
                for required in self.REQUIRED_FILES:
                    if required not in file_list:
                        errors.append(f"打包文件中缺少: {required}")

                # 检查文件结构（顶层应该是技能名称文件夹）
                if file_list:
                    first_path = file_list[0]
                    expected_prefix = f"{self.skill_path.name}/"
                    if not first_path.startswith(expected_prefix):
                        errors.append(f"打包结构可能不正确，首个文件应为 {expected_prefix}*")

        except zipfile.BadZipFile:
            errors.append("无效的 ZIP 文件格式")

        return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("  skill_path: 技能目录路径")
        print("  output_dir: 可选，输出目录（默认与技能目录同级）")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("技能打包工具")
    print("=" * 60)
    print(f"技能路径: {skill_path}")
    if output_dir:
        print(f"输出目录: {output_dir}")
    print()

    packager = SkillPackager(skill_path)

    # 先验证
    print("-" * 40)
    print("打包前验证:")
    is_valid, errors = packager.validate_before_packaging()
    if is_valid:
        print("  验证通过")
    else:
        print("  验证失败:")
        for error in errors:
            print(f"    - {error}")
        sys.exit(1)

    print()

    # 执行打包
    success, output_file = packager.package(output_dir)

    if success:
        print()
        print("-" * 40)
        print("打包文件验证:")
        is_valid, errors = packager.verify_package(output_file)
        if is_valid:
            print("  验证通过")
        else:
            print("  验证失败:")
            for error in errors:
                print(f"    - {error}")

        print()
        print("=" * 60)
        print("打包完成!")
        print(f"输出文件: {output_file}")
        print("=" * 60)
    else:
        print("打包失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
