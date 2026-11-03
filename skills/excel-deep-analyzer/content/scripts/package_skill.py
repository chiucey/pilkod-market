#!/usr/bin/env python3
"""
打包技能为可发布的.skill文件
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import zipfile


def package_skill(skill_path: str, output_dir: str = None):
    """打包技能"""
    skill_path = Path(skill_path)

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"错误: 技能路径不存在: {skill_path}")
        return False

    # 读取meta信息
    meta_path = skill_path / '_meta.json'
    if not meta_path.exists():
        print("错误: 缺少_meta.json文件")
        return False

    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 确定输出路径
    if output_dir is None:
        output_dir = Path('/workspace/temp-skills')
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}.skill"

    # 创建zip文件
    print(f"打包技能: {skill_name} (v{version})")
    print(f"输出文件: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)

                # 跳过打包脚本自身
                if 'package_skill' in str(file_path):
                    continue

                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✅ 打包完成!")
    print(f"   技能ID: {skill_id}")
    print(f"   版本: {version}")
    print(f"   文件: {output_file}")

    return True


def main():
    if len(sys.argv) < 2:
        skill_path = '/workspace/temp-skills/excel-deep-analyzer'
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    success = package_skill(skill_path, output_dir)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
