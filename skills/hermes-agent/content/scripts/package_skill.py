#!/usr/bin/env python3
"""
HermesAgent 技能打包脚本

此脚本将技能打包为可分发的 .skill 文件。
"""

import json
import os
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else Path('dist')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.include_patterns = [
            '*.md',
            '*.json',
            '*.yaml',
            '*.yml',
            '*.py',
            '*.sh',
            '*.sql',
            '*.txt',
        ]

        self.exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            'node_modules',
            '.venv',
            'venv',
            '*.log',
            '*.tmp',
            '.pytest_cache',
            '.mypy_cache',
        ]

    def package(self) -> Path:
        """执行打包操作"""
        print(f"正在打包技能: {self.skill_path}")
        print("=" * 60)

        # 读取元数据
        meta = self._load_metadata()

        # 生成输出文件名
        output_name = f"{meta.get('name', 'unknown')}-{meta.get('version', '0.0.0')}.skill"
        output_path = self.output_dir / output_name

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 复制文件到临时目录
            self._copy_files(temp_path)

            # 生成打包清单
            self._generate_manifest(temp_path, meta)

            # 创建 tar.gz 归档
            self._create_archive(temp_path, output_path)

        print(f"\n✅ 打包完成: {output_path}")
        print(f"   文件大小: {output_path.stat().st_size / 1024:.2f} KB")

        return output_path

    def _load_metadata(self) -> Dict[str, Any]:
        """加载技能元数据"""
        meta_path = self.skill_path / '_meta.json'
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _copy_files(self, dest_path: Path) -> None:
        """复制技能文件到目标目录"""
        print("\n正在复制文件...")

        files_copied = 0
        for root, dirs, files in os.walk(self.skill_path):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]

            rel_root = Path(root).relative_to(self.skill_path)

            for file in files:
                # 检查是否应该排除
                if any(file.endswith(p.replace('*', '')) or p.replace('*', '') in file
                       for p in self.exclude_patterns):
                    continue

                src = Path(root) / file
                dst = dest_path / rel_root / file

                # 确保目标目录存在
                dst.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件
                shutil.copy2(src, dst)
                files_copied += 1
                print(f"   + {rel_root / file}")

        print(f"   共复制 {files_copied} 个文件")

    def _generate_manifest(self, temp_path: Path, meta: Dict[str, Any]) -> None:
        """生成打包清单"""
        manifest = {
            'name': meta.get('name', 'unknown'),
            'version': meta.get('version', '0.0.0'),
            'packaged_at': datetime.now().isoformat(),
            'files': []
        }

        # 收集所有文件信息
        for root, dirs, files in os.walk(temp_path):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(temp_path)

                manifest['files'].append({
                    'path': str(rel_path),
                    'size': file_path.stat().st_size,
                    'md5': self._calculate_md5(file_path)
                })

        # 写入清单文件
        manifest_path = temp_path / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"\n已生成清单: {len(manifest['files'])} 个文件")

    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件的 MD5 哈希"""
        import hashlib
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _create_archive(self, source_path: Path, output_path: Path) -> None:
        """创建 tar.gz 归档"""
        print(f"\n正在创建归档: {output_path.name}")

        with tarfile.open(output_path, 'w:gz') as tar:
            for item in source_path.rglob('*'):
                if item.is_file():
                    tar.add(item, arcname=str(item.relative_to(source_path)))

        print("归档创建完成")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not skill_path.exists():
        print(f"错误: 路径不存在 - {skill_path}")
        sys.exit(1)

    packager = SkillPackager(skill_path, output_dir)
    output_path = packager.package()

    print("\n" + "=" * 60)
    print("打包摘要")
    print("=" * 60)
    print(f"技能路径: {skill_path}")
    print(f"输出文件: {output_path}")
    print(f"技能版本: {packager._load_metadata().get('version', 'unknown')}")


if __name__ == '__main__':
    main()
