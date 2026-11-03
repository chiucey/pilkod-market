#!/usr/bin/env python3
"""
Package ASCII Art Chart Skill
将技能打包为可分发的 .skill 文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str, output_dir: str = "."):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def package(self) -> str:
        """打包技能并返回输出路径"""
        if not self.skill_path.exists():
            raise FileNotFoundError(f"Skill path not found: {self.skill_path}")

        # 读取元数据
        meta_file = self.skill_path / '_meta.json'
        if not meta_file.exists():
            raise FileNotFoundError("Missing _meta.json")

        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 生成输出文件名
        skill_name = self.skill_path.name
        version = meta.get('version', '1.0.0')
        output_name = f"{skill_name}-{version}.skill"
        output_path = self.output_dir / output_name

        # 创建打包列表
        files_to_package = []

        for root, dirs, files in os.walk(self.skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.skill_path)
                files_to_package.append((file_path, rel_path))

        # 创建 ZIP 文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, rel_path in files_to_package:
                zf.write(file_path, rel_path)

        print(f"Packaged {len(files_to_package)} files")
        print(f"Output: {output_path}")

        return str(output_path)

    def verify_package(self, package_path: str) -> bool:
        """验证打包内容"""
        try:
            with zipfile.ZipFile(package_path, 'r') as zf:
                files = zf.namelist()

                # 检查必需文件
                required = ['SKILL.md', '_meta.json']
                for req in required:
                    if not any(f.endswith(req) for f in files):
                        print(f"Missing required file: {req}")
                        return False

            return True
        except Exception as e:
            print(f"Verification failed: {e}")
            return False


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    packager = SkillPackager(skill_path, output_dir)

    try:
        output_path = packager.package()

        if packager.verify_package(output_path):
            print("✓ Package verified successfully")
        else:
            print("✗ Package verification failed")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
