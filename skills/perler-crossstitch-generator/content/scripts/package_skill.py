#!/usr/bin/env python3
"""
拼豆十字绣图纸生成器 - 技能打包脚本
将技能打包为 .skill 文件
"""

import os
import json
import zipfile
from pathlib import Path
import shutil
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_dir, output_dir=None):
        self.skill_dir = Path(skill_dir)
        self.output_dir = Path(output_dir) if output_dir else self.skill_dir.parent
        self.manifest = None

    def package(self):
        """打包技能"""
        print(f"打包技能: {self.skill_dir}")
        print("=" * 50)

        # 读取 manifest
        self.load_manifest()

        # 验证必需文件
        if not self.validate():
            print("验证失败，取消打包")
            return False

        # 创建打包文件名
        skill_name = self.manifest.get('id', self.skill_dir.name)
        version = self.manifest.get('version', '1.0.0')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = self.output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

        # 创建 zip 文件
        print(f"\n创建打包文件: {output_file.name}")
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            self.add_files_to_zip(zf, self.skill_dir, '')

        print(f"\n✅ 打包完成: {output_file}")
        print(f"   文件大小: {self.format_size(output_file.stat().st_size)}")

        return str(output_file)

    def load_manifest(self):
        """加载 manifest"""
        meta_file = self.skill_dir / '_meta.json'
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
            print(f"✓ 加载 manifest: {self.manifest.get('name', 'Unknown')}")
        else:
            self.manifest = {'id': self.skill_dir.name, 'version': '1.0.0'}
            print("⚠ 未找到 _meta.json，使用默认值")

    def validate(self):
        """验证技能结构"""
        required = ['SKILL.md', '_meta.json']
        for f in required:
            if not (self.skill_dir / f).exists():
                print(f"❌ 缺少必需文件: {f}")
                return False
        print("✓ 必需文件验证通过")
        return True

    def add_files_to_zip(self, zf, base_path, archive_path):
        """递归添加文件到 zip"""
        for item in sorted(base_path.iterdir()):
            # 跳过隐藏文件和 __pycache__
            if item.name.startswith('.') or item.name == '__pycache__':
                continue

            arc_name = f"{archive_path}/{item.name}" if archive_path else item.name

            if item.is_dir():
                self.add_files_to_zip(zf, item, arc_name)
            else:
                # 跳过大型二进制文件
                size = item.stat().st_size
                if size > 50 * 1024 * 1024:  # 50MB
                    print(f"⚠ 跳过大文件: {item.name} ({self.format_size(size)})")
                    continue

                zf.write(item, arc_name)
                print(f"  + {arc_name}")

    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def main():
    import sys

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    packager = SkillPackager(skill_dir)
    output_file = packager.package()

    if output_file:
        print(f"\n📦 打包文件位置: {output_file}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
