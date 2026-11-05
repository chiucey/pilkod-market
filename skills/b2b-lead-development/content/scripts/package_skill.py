#!/usr/bin/env python3
"""
B2B Lead Development Skill - Package Script
打包技能为可分发的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.skill_path.parent / 'dist'

    def package(self) -> str:
        """打包技能"""
        print(f"\n{'='*60}")
        print(f"打包技能: {self.skill_name}")
        print(f"{'='*60}\n")

        # 验证必要文件
        if not self.validate():
            print("✗ 验证失败，无法打包")
            return None

        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)

        # 生成输出文件名
        output_file = self.output_dir / f"{self.skill_name}_{self.timestamp}.skill"

        # 创建打包
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 打包目录结构
                self.add_directory_to_zip(zf, self.skill_path, self.skill_path)

            print(f"✓ 技能已打包: {output_file}")
            print(f"✓ 文件大小: {self.format_size(output_file.stat().st_size)}")

            # 生成清单
            self.generate_manifest(output_file)

            return str(output_file)

        except Exception as e:
            print(f"✗ 打包失败: {e}")
            return None

    def validate(self) -> bool:
        """验证技能包"""
        required_files = ['SKILL.md', '_meta.json']

        for file_name in required_files:
            file_path = self.skill_path / file_name
            if not file_path.exists():
                print(f"✗ 缺少必需文件: {file_name}")
                return False

        # 验证_meta.json
        try:
            meta = json.loads((self.skill_path / '_meta.json').read_text(encoding='utf-8'))
            if 'id' not in meta or 'version' not in meta:
                print("✗ _meta.json缺少id或version")
                return False
        except Exception as e:
            print(f"✗ _meta.json格式错误: {e}")
            return False

        print("✓ 验证通过")
        return True

    def add_directory_to_zip(self, zf: zipfile.ZipFile, base_path: Path, current_path: Path):
        """递归添加目录到zip"""
        # 安全检查：不允许符号链接逃逸
        resolved_base = base_path.resolve()
        resolved_current = current_path.resolve()

        if not str(resolved_current).startswith(str(resolved_base)):
            return

        # 排除的文件
        exclude_patterns = [
            '__pycache__',
            '.git',
            '.DS_Store',
            'Thumbs.db',
            '*.pyc',
            '*.pyo',
            '.env',
            '.venv',
            'node_modules',
            '.idea',
            '.vscode'
        ]

        for item in sorted(current_path.iterdir()):
            # 跳过排除项
            should_skip = False
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    if item.suffix == pattern[1:]:
                        should_skip = True
                        break
                elif pattern in item.name:
                    should_skip = True
                    break

            if should_skip:
                continue

            if item.is_file():
                arcname = str(item.relative_to(base_path))
                zf.write(item, arcname)
                print(f"  + {arcname}")
            elif item.is_dir():
                self.add_directory_to_zip(zf, base_path, item)

    def generate_manifest(self, output_file: Path):
        """生成打包清单"""
        meta = json.loads((self.skill_path / '_meta.json').read_text(encoding='utf-8'))

        manifest = {
            "skill_name": self.skill_name,
            "display_name": meta.get('display_name', self.skill_name),
            "version": meta['version'],
            "skill_id": meta['id'],
            "packaged_at": datetime.now().isoformat(),
            "files": []
        }

        # 列出所有文件
        with zipfile.ZipFile(output_file, 'r') as zf:
            for info in zf.infolist():
                manifest['files'].append({
                    "path": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size
                })

        manifest_path = output_file.with_suffix('.json')
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

        print(f"\n✓ 清单已生成: {manifest_path}")

    @staticmethod
    def format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    packager = SkillPackager(skill_path)
    output_file = packager.package()

    if output_file:
        print(f"\n打包完成!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
