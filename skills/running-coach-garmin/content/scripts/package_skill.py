#!/usr/bin/env python3
"""
打包脚本 - running-coach-garmin 技能
将技能打包为 .skill 文件用于分发
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

def ok(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def err(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def create_skill_package(skill_dir, output_dir=None):
    """将技能打包为 .skill 文件"""
    skill_path = Path(skill_dir).resolve()
    skill_name = skill_path.name

    # 默认输出到父目录的 dist/
    if output_dir is None:
        output_dir = skill_path.parent / 'dist'
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取 _meta.json 获取版本信息
    meta_path = skill_path / '_meta.json'
    if not meta_path.exists():
        err(f"_meta.json 不存在: {meta_path}")
        return None

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}.skill"
    temp_zip = output_dir / f"{skill_name}.zip"

    # 创建打包清单
    manifest = {
        'skill_name': skill_name,
        'skill_id': skill_id,
        'version': version,
        'packaged_at': datetime.now().isoformat(),
        'files': []
    }

    # 构建包内容
    ok(f"开始打包技能: {skill_name} v{version}")
    print(f"  输出文件: {output_file}")

    # 创建 ZIP 文件
    with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                rel_path = file_path.relative_to(skill_path)

                # 跳过 __pycache__ 等目录
                if '__pycache__' in str(rel_path):
                    continue
                if file.endswith('.pyc'):
                    continue

                # 添加到 ZIP
                arcname = str(rel_path)
                zf.write(file_path, arcname)

                # 计算文件哈希
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()[:16]

                manifest['files'].append({
                    'path': arcname,
                    'size': file_path.stat().st_size,
                    'hash': file_hash
                })

    # 重命名为 .skill
    if temp_zip.exists():
        temp_zip.rename(output_file)

    ok(f"打包完成!")
    print(f"\n{'='*60}")
    print(f"技能包信息:")
    print(f"  名称: {skill_name}")
    print(f"  ID: {skill_id}")
    print(f"  版本: {version}")
    print(f"  文件数: {len(manifest['files'])}")
    print(f"  输出: {output_file}")
    print(f"{'='*60}\n")

    return str(output_file)

def main():
    # 默认使用脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = Path(script_dir).parent

    # 可以通过命令行参数指定技能目录
    if len(sys.argv) > 1:
        skill_dir = Path(sys.argv[1])
        if not skill_dir.is_dir():
            err(f"技能目录不存在: {skill_dir}")
            return 1

    if not (skill_dir / 'SKILL.md').exists():
        err(f"SKILL.md 不存在于: {skill_dir}")
        return 1

    result = create_skill_package(skill_dir)
    return 0 if result else 1

if __name__ == '__main__':
    sys.exit(main())