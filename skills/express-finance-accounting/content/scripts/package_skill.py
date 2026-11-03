#!/usr/bin/env python3
"""
快递财务技能 - 打包脚本
将技能打包为可分发的.skill文件
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_dir: str, output_dir: str = '/workspace/temp-skills') -> str:
    """打包技能为.skill文件"""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_dir}")

    # 读取元数据
    meta_path = skill_path / '_meta.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        skill_name = meta.get('id', skill_path.name)
        version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_path / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建zip打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_file)


def main():
    skill_dir = '/workspace/temp-skills/express-finance-accounting'
    output_file = package_skill(skill_dir)
    print(f"✓ 技能打包完成: {output_file}")
    return 0


if __name__ == '__main__':
    exit(main())
