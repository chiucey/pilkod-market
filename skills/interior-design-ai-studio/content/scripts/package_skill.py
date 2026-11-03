#!/usr/bin/env python3
"""
室内设计AI工作室 - 打包脚本
生成可分发的 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def get_version(meta_path: Path) -> str:
    """获取版本号"""
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        return meta.get('version', '1.0.0')
    return '1.0.0'

def package_skill(skill_path: str, output_dir: str = './dist') -> str:
    """打包技能到 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    version = get_version(skill_path / '_meta.json')
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = output_dir / f"{skill_path.name}-v{version}-{timestamp}.skill"

    # 创建压缩包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 排除隐藏文件和缓存
                if not any(p.startswith('.') for p in file_path.parts):
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)

    return str(output_file.absolute())

if __name__ == '__main__':
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    output = package_skill(skill_path)
    print(f"✓ Skill packaged: {output}")
