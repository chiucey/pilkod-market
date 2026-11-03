#!/usr/bin/env python3
"""
法考错题分析技能 - 打包脚本

将技能文件夹打包为 .skill 文件，用于分发和发布。
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path: str, output_dir: str = "."):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir)
        self.errors = []
        self.warnings = []

        # 打包时忽略的文件/目录
        self.exclude_patterns = [
            '__pycache__',
            '.git',
            '.DS_Store',
            'Thumbs.db',
            '*.pyc',
            '*.pyo',
            '.venv',
            'node_modules',
            # 不打包脚本本身（仅用于开发）
            'scripts/quick_validate.py',
            'scripts/package_skill.py',
            'scripts/test_*.py',
        ]

    def package(self) -> str:
        """执行打包操作"""
        print(f"=" * 60)
        print(f"技能打包：{self.skill_path.name}")
        print(f"=" * 60)

        # 读取元数据
        meta = self.read_metadata()

        # 生成输出文件名
        skill_name = meta.get('id', self.skill_path.name)
        version = meta.get('version', '1.0.0')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = self.output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

        # 创建压缩包
        print(f"\n正在打包技能...")
        print(f"输出文件: {output_file}")

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            for root, dirs, files in os.walk(self.skill_path):
                # 过滤目录
                dirs[:] = [d for d in dirs if d not in self.exclude_patterns and not d.startswith('.')]

                for file in files:
                    # 过滤文件
                    if file.startswith('.') or file in self.exclude_patterns:
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_path)

                    # 检查是否是脚本目录中的开发文件
                    if 'scripts/' in str(arcname) and (file.startswith('test_') or file in ['quick_validate.py', 'package_skill.py']):
                        continue

                    try:
                        zf.write(file_path, arcname)
                        file_count += 1
                        print(f"  + {arcname}")
                    except Exception as e:
                        self.errors.append(f"添加文件失败 {arcname}: {e}")

        # 验证打包结果
        if self.validate_package(output_file):
            print(f"\n✓ 打包成功！共包含 {file_count} 个文件")
            print(f"  输出: {output_file}")
        else:
            print(f"\n✗ 打包验证失败")
            return None

        # 生成元数据清单
        manifest = {
            'name': meta.get('id'),
            'version': meta.get('version'),
            'author': meta.get('author', 'Unknown'),
            'created': meta.get('created', datetime.now().strftime('%Y-%m-%d')),
            'packaged_at': datetime.now().isoformat(),
            'file_count': file_count,
            'package_file': str(output_file.name)
        }

        manifest_path = output_file.with_suffix('.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"\n清单文件: {manifest_path}")
        print("=" * 60)

        return str(output_file)

    def read_metadata(self) -> dict:
        """读取元数据"""
        meta_path = self.skill_path / "_meta.json"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def validate_package(self, zip_path: Path) -> bool:
        """验证打包结果"""
        required_files = ['SKILL.md', '_meta.json']

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                names = zf.namelist()

                for req in required_files:
                    if req not in names:
                        self.errors.append(f"打包文件中缺少必填文件: {req}")
                        return False

                # 检查frontmatter
                skill_content = zf.read('SKILL.md').decode('utf-8')
                if not skill_content.startswith('---'):
                    self.errors.append("SKILL.md frontmatter 格式不正确")
                    return False

            return True
        except Exception as e:
            self.errors.append(f"验证打包结果失败: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        skill_path = "."
        output_dir = "."
    elif len(sys.argv) < 3:
        skill_path = sys.argv[1]
        output_dir = "."
    else:
        skill_path = sys.argv[1]
        output_dir = sys.argv[2]

    packager = SkillPackager(skill_path, output_dir)
    result = packager.package()

    if result:
        print(f"\n[SUCCESS] 技能包已生成: {result}")
        sys.exit(0)
    else:
        print("\n[ERROR] 打包失败:")
        for e in packager.errors:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
