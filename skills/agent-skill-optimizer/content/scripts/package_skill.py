#!/usr/bin/env python3
"""
Package Skill Script for Agent Skill Optimizer
Creates a distributable .skill archive with validation
"""

import os
import json
import zipfile
import hashlib
import sys
from pathlib import Path
from datetime import datetime

class SkillPacker:
    """技能打包器"""

    def __init__(self, skill_path, output_dir=None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else self.skill_path.parent
        self.excluded_patterns = [
            '__pycache__', '*.pyc', '.git', '.DS_Store',
            '*.log', 'node_modules', '.venv', '*.tmp'
        ]

    def package(self):
        """执行打包"""
        print(f"📦 打包技能: {self.skill_path}")
        print("=" * 60)

        # 读取元数据
        meta = self._load_meta()

        # 生成输出文件名
        skill_name = meta.get('id', self.skill_path.name)
        version = meta.get('version', '1.0.0')
        output_file = self.output_dir / f"{skill_name}.skill"

        # 创建 ZIP 归档
        self._create_archive(output_file, meta)

        # 生成校验和
        checksum = self._calculate_checksum(output_file)

        # 生成元数据清单
        manifest = {
            'file': output_file.name,
            'size': output_file.stat().st_size,
            'checksum': checksum,
            'created': datetime.now().isoformat(),
            'skill_name': meta.get('name', 'unknown'),
            'version': version,
            'files_included': self._list_files()
        }

        manifest_file = output_file.with_suffix('.json')
        manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

        print("\n" + "=" * 60)
        print("📦 打包完成！")
        print("=" * 60)
        print(f"  📁 归档文件: {output_file}")
        print(f"  📊 文件大小: {manifest['size']} bytes")
        print(f"  🔐 校验和: {checksum[:16]}...")
        print(f"  📋 清单文件: {manifest_file}")
        print(f"  📁 包含文件: {len(manifest['files_included'])} 个")

        return str(output_file)

    def _load_meta(self):
        """加载元数据"""
        meta_path = self.skill_path / "_meta.json"
        return json.loads(meta_path.read_text(encoding='utf-8'))

    def _create_archive(self, output_file, meta):
        """创建归档文件"""
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in self.skill_path.rglob('*'):
                if item.is_file() and not item.is_symlink():
                    # 检查是否应排除
                    if self._should_exclude(item):
                        continue

                    # 计算归档内的路径
                    arcname = item.relative_to(self.skill_path)
                    zf.write(item, arcname)
                    print(f"  + {arcname}")

    def _should_exclude(self, path):
        """检查是否应排除文件"""
        name = path.name
        for pattern in self.excluded_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False

    def _list_files(self):
        """列出所有包含的文件"""
        files = []
        for item in self.skill_path.rglob('*'):
            if item.is_file() and not item.is_symlink():
                if not self._should_exclude(item):
                    files.append(str(item.relative_to(self.skill_path)))
        return sorted(files)

    def _calculate_checksum(self, file_path):
        """计算文件校验和"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()


def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/agent-skill-optimizer"
    else:
        skill_path = sys.argv[1]

    packer = SkillPacker(skill_path)
    output_file = packer.package()

    print(f"\n✨ 打包成功！产出文件: {output_file}")


if __name__ == "__main__":
    main()
