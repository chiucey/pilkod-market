#!/usr/bin/env python3
"""
技能打包脚本 - 创建 .skill 文件
"""

import zipfile
import sys
import json
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取 meta 信息
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        skill_name = meta.get('name', skill_path.name)
        version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        version = '1.0.0'

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}_{version}.skill"

    # 打包文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 递归添加所有文件
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 排除 .skill 自身
                if file_path.suffix != '.skill':
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return str(output_file)


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n打包完成!")
        return 0
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
