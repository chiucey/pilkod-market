#!/usr/bin/env python3
"""
WBS Generator Skill Packager
将WBS技能打包为可发布的.skill文件
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime

class SkillPackager:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.output_dir = self.skill_path.parent / "dist"

    def package(self):
        """打包技能"""
        print(f"打包技能: {self.skill_name}")
        print("=" * 50)

        # 检查必需文件
        if not self._check_required_files():
            print("\n❌ 打包失败: 缺少必需文件")
            return False

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        meta = self._load_meta()
        version = meta.get('version', '1.0.0') if meta else '1.0.0'
        output_file = self.output_dir / f"{self.skill_name}-{version}.skill"

        # 创建ZIP包
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                self._add_files_to_zip(zf, self.skill_path, self.skill_path)

            print(f"\n✅ 打包成功!")
            print(f"输出文件: {output_file}")
            print(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")
            return True

        except Exception as e:
            print(f"\n❌ 打包失败: {e}")
            return False

    def _check_required_files(self):
        """检查必需文件"""
        required_files = ['SKILL.md', '_meta.json']
        missing = []

        for file_name in required_files:
            if not (self.skill_path / file_name).exists():
                missing.append(file_name)

        if missing:
            print(f"缺少文件: {', '.join(missing)}")
            return False

        return True

    def _load_meta(self):
        """加载_meta.json"""
        meta_file = self.skill_path / "_meta.json"
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def _add_files_to_zip(self, zf, base_path, current_path):
        """递归添加文件到ZIP"""
        for item in current_path.iterdir():
            # 跳过输出目录
            if 'dist' in item.name or item.name.startswith('.'):
                continue

            if item.is_file():
                arcname = item.relative_to(base_path)
                zf.write(item, arcname)
                print(f"  添加: {arcname}")
            elif item.is_dir():
                self._add_files_to_zip(zf, base_path, item)

def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    packager = SkillPackager(skill_path)
    success = packager.package()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
