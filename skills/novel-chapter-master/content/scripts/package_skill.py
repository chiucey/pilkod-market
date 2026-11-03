#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可发布的.skill文件
Package skill into distributable .skill archive
"""

import os
import json
import zipfile
import hashlib
import shutil
import sys
from pathlib import Path
from datetime import datetime


class SkillPacker:
    """技能打包器"""

    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else self.skill_path.parent / 'dist'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def package(self) -> dict:
        """打包技能并返回元数据"""
        print(f"\n{'='*60}")
        print(f"技能打包开始: {self.skill_path.name}")
        print(f"{'='*60}\n")

        # 读取元数据
        meta_file = self.skill_path / '_meta.json'
        if not meta_file.exists():
            raise FileNotFoundError("_meta.json 不存在")

        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        skill_id = meta.get('id', 'unknown')
        version = meta.get('version', '1.0.0')
        skill_name = meta.get('name', self.skill_path.name)

        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_name = f"{skill_name}_v{version}_{timestamp}.skill"
        output_path = self.output_dir / output_name

        # 收集要打包的文件
        files_to_package = self.collect_files()

        print(f"📦 打包文件列表 ({len(files_to_package)} 个文件):")
        for f in files_to_package:
            print(f"  - {f.relative_to(self.skill_path)}")

        # 创建ZIP文件
        print(f"\n📦 创建打包文件: {output_path.name}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_package:
                arcname = file_path.relative_to(self.skill_path)
                zf.write(file_path, arcname)

        # 计算校验和
        checksum = self.calculate_checksum(output_path)

        # 生成清单
        manifest = {
            'skill_id': skill_id,
            'name': skill_name,
            'version': version,
            'description': meta.get('description', ''),
            'author': meta.get('author', 'Unknown'),
            'created_at': meta.get('created_at', ''),
            'packaged_at': datetime.now().isoformat(),
            'file_count': len(files_to_package),
            'checksum': checksum,
            'output_file': str(output_path)
        }

        # 保存清单
        manifest_path = output_path.with_suffix('.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 打包完成!")
        print(f"   打包文件: {output_path}")
        print(f"   校验和: {checksum}")
        print(f"   文件数量: {len(files_to_package)}")

        return manifest

    def collect_files(self) -> list:
        """收集要打包的文件"""
        files = []

        # 遍历技能目录
        for root, dirs, filenames in os.walk(self.skill_path):
            root_path = Path(root)

            # 跳过 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for filename in filenames:
                # 跳过隐藏文件和临时文件
                if filename.startswith('.') or filename.endswith('.pyc'):
                    continue

                file_path = root_path / filename
                files.append(file_path)

        return sorted(files)

    def calculate_checksum(self, file_path: Path) -> str:
        """计算文件的SHA256校验和"""
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return sha256.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py ./novel-chapter-master")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        packer = SkillPacker(skill_path, output_dir)
        manifest = packer.package()

        print(f"\n{'='*60}")
        print("📋 打包清单")
        print(f"{'='*60}")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
