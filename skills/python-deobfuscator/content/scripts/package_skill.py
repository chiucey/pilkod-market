#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Deobfuscator Skill 打包脚本
将技能打包为可分发的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else self.skill_path.parent / 'dist'
        self.skill_name = self.skill_path.name
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def package(self) -> str:
        """打包技能"""
        print("=" * 60)
        print("SKILL PACKAGER")
        print("=" * 60)
        print(f"\nSkill: {self.skill_name}")
        print(f"Source: {self.skill_path}")
        print(f"Output: {self.output_dir}")

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        output_file = self.output_dir / f"{self.skill_name}_{self.timestamp}.skill"

        # 收集要打包的文件
        files_to_package = self.collect_files()

        # 创建zip包
        print(f"\n[*] Packaging {len(files_to_package)} files...")
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_package:
                arcname = file_path.relative_to(self.skill_path)
                zf.write(file_path, arcname)
                print(f"    + {arcname}")

        # 验证包内容
        print("\n[*] Verifying package...")
        self.verify_package(output_file)

        print(f"\n[+] Package created: {output_file}")
        print(f"    Size: {output_file.stat().st_size:,} bytes")

        return str(output_file)

    def collect_files(self) -> list:
        """收集要打包的文件"""
        files = []

        # 遍历技能目录
        for item in self.skill_path.rglob('*'):
            if item.is_file():
                # 排除临时文件和系统文件
                if any(skip in item.name for skip in ['__pycache__', '.DS_Store', 'Thumbs.db']):
                    continue
                files.append(item)

        return sorted(files)

    def verify_package(self, zip_path: Path):
        """验证包内容"""
        required_files = ['SKILL.md', '_meta.json']

        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()

            for required in required_files:
                if required in names:
                    print(f"    [OK] {required}")
                else:
                    print(f"    [MISSING] {required}")

            # 检查脚本
            scripts = [n for n in names if n.startswith('scripts/') and n.endswith('.py')]
            if scripts:
                print(f"    [OK] {len(scripts)} script(s)")

            # 检查参考文档
            refs = [n for n in names if n.startswith('references/') and n.endswith('.md')]
            if refs:
                print(f"    [OK] {len(refs)} reference(s)")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    packager = SkillPackager(skill_path, output_dir)
    output_file = packager.package()

    print("\n" + "=" * 60)
    print("PACKAGING COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
