#!/usr/bin/env python3
"""
技能打包脚本
用法：python package_skill.py <skill_root_dir> [输出目录]
输出：<skill_name>.skill（zip 格式）
"""

import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

EXCLUDE_PATTERNS = {
    '__pycache__', '.DS_Store', 'Thumbs.db', '.git', '.svn',
    '*.pyc', '*.pyo', '.env', '*.log', 'node_modules'
}


def should_exclude(path: Path) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat.startswith('*'):
            if path.name.endswith(pat[1:]):
                return True
        elif path.name == pat:
            return True
    return False


def package_skill(skill_root: Path, output_dir: Path = None) -> Path:
    if output_dir is None:
        output_dir = skill_root.parent

    skill_name = skill_root.name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'{skill_name}_{timestamp}.skill'

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_root.rglob('*'):
            if file_path.is_file() and not should_exclude(file_path):
                arcname = file_path.relative_to(skill_root.parent)
                zf.write(file_path, arcname)
                print(f'  + {arcname}')

    print(f'\n✅ 打包完成：{output_file}')
    print(f'   文件大小：{output_file.stat().st_size / 1024:.1f} KB')
    return output_file


if __name__ == '__main__':
    skill_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not skill_root.exists():
        print(f'❌ 路径不存在：{skill_root}')
        sys.exit(1)

    package_skill(skill_root, output_dir)
