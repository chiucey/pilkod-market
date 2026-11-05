#!/usr/bin/env python3
"""
技能打包脚本 - 将技能目录打包为 .skill 文件
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name

    def package(self, output_dir=None):
        """打包技能为 .skill 文件"""
        print(f"📦 开始打包技能: {self.skill_name}")
        print("-" * 50)

        # 确定输出目录
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.skill_path.parent

        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"{self.skill_name}_{timestamp}.skill"

        # 收集所有文件
        files_to_package = self._collect_files()

        if not files_to_package:
            print("❌ 没有找到需要打包的文件")
            return None

        print(f"📁 发现 {len(files_to_package)} 个文件待打包:")
        for f in files_to_package:
            rel_path = f.relative_to(self.skill_path)
            print(f"   - {rel_path}")

        # 创建 .skill 文件 (ZIP格式)
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files_to_package:
                    rel_path = file_path.relative_to(self.skill_path)
                    zf.write(file_path, arcname=str(rel_path))
                    print(f"   ✅ 添加: {rel_path}")

            # 计算文件哈希
            file_hash = self._calculate_hash(output_file)
            file_size = output_file.stat().st_size

            print("\n" + "=" * 50)
            print("📊 打包完成")
            print("=" * 50)
            print(f"   📦 输出文件: {output_file.name}")
            print(f"   📏 文件大小: {file_size / 1024:.2f} KB")
            print(f"   🔐 SHA256: {file_hash[:16]}...")
            print(f"   🕐 时间戳: {timestamp}")

            # 生成 manifest.json
            manifest = self._create_manifest(files_to_package, file_hash, file_size, timestamp)
            manifest_path = output_path / f"{self.skill_name}_{timestamp}_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            print(f"   📋 清单文件: {manifest_path.name}")

            return str(output_file)

        except Exception as e:
            print(f"❌ 打包失败: {e}")
            return None

    def _collect_files(self):
        """收集所有需要打包的文件"""
        files = []

        # 必需文件
        required_files = ['SKILL.md', '_meta.json']
        for fname in required_files:
            fpath = self.skill_path / fname
            if fpath.exists():
                files.append(fpath)
            else:
                print(f"⚠️  警告: 缺少必需文件 {fname}")

        # 可选目录中的文件
        optional_dirs = ['references', 'scripts', 'assets', 'tests']
        for dirname in optional_dirs:
            dir_path = self.skill_path / dirname
            if dir_path.exists() and dir_path.is_dir():
                for fpath in dir_path.rglob('*'):
                    if fpath.is_file() and not fpath.name.startswith('.'):
                        files.append(fpath)

        return files

    def _calculate_hash(self, file_path):
        """计算文件 SHA256 哈希"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _create_manifest(self, files, file_hash, file_size, timestamp):
        """创建打包清单"""
        # 读取 meta.json
        meta = {}
        meta_path = self.skill_path / '_meta.json'
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

        # 读取 SKILL.md 获取信息
        skill_md = self.skill_path / 'SKILL.md'
        skill_info = {
            'name': self.skill_name,
            'version': meta.get('version', '1.0.0'),
            'author': meta.get('author', 'Unknown'),
            'created': meta.get('created_at', timestamp[:10]),
            'packaged_at': timestamp
        }

        return {
            'skill_info': skill_info,
            'package_info': {
                'file_name': f"{self.skill_name}_{timestamp}.skill",
                'file_hash': file_hash,
                'file_size': file_size,
                'timestamp': timestamp,
                'format': 'skill-package-v1'
            },
            'included_files': [
                str(f.relative_to(self.skill_path)) for f in files
            ],
            'tags': meta.get('tags', [])
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py /workspace/temp-skills/smart-file-assistant")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    packager = SkillPackager(skill_path)
    result = packager.package(output_dir)

    if result:
        print(f"\n✅ 打包成功: {result}")
        sys.exit(0)
    else:
        print("\n❌ 打包失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
