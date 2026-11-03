#!/usr/bin/env python3
"""
技能打包脚本 - 生成可分发的.skill文件
"""
import os
import shutil
import sys
import json
from pathlib import Path
from datetime import datetime


def collect_files(skill_path):
    """收集技能目录下的所有文件"""
    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # 排除隐藏目录和特殊目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

        for filename in filenames:
            if filename.startswith('.') or filename.endswith('.pyc'):
                continue
            full_path = Path(root) / filename
            rel_path = full_path.relative_to(skill_path)
            files.append({
                'path': str(rel_path),
                'full_path': str(full_path)
            })
    return files


def create_package(skill_path, output_path=None):
    """创建技能包"""
    skill_path = Path(skill_path)

    # 读取meta信息
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        print("Error: _meta.json not found")
        sys.exit(1)

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 确定输出路径
    if output_path is None:
        skill_name = skill_path.name
        output_path = skill_path.parent / f"{skill_name}.skill"

    output_path = Path(output_path)

    # 收集文件
    files = collect_files(skill_path)

    print(f"Skill: {meta.get('name', 'unknown')}")
    print(f"Version: {meta.get('version', '1.0.0')}")
    print(f"Files to package: {len(files)}")
    print("-" * 50)

    for f in files:
        print(f"  + {f['path']}")

    # 创建临时打包目录
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 复制文件
        for f in files:
            dest = tmpdir / f['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f['full_path'], dest)

        # 添加manifest
        manifest = {
            'name': meta.get('name', 'unknown'),
            'id': meta.get('id', 'unknown'),
            'version': meta.get('version', '1.0.0'),
            'created': datetime.now().isoformat(),
            'files': [f['path'] for f in files]
        }

        with open(tmpdir / 'manifest.json', 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # 打包
        shutil.make_archive(
            str(output_path.with_suffix('')),
            'zip',
            tmpdir
        )

        # 重命名为.skill
        zip_path = output_path.with_suffix('.zip')
        if output_path.exists():
            output_path.unlink()
        shutil.move(str(zip_path), str(output_path))

    print("-" * 50)
    print(f"✓ Package created: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.2f} KB")

    return output_path


def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    create_package(skill_path, output_path)


if __name__ == "__main__":
    main()
