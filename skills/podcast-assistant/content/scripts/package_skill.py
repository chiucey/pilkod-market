#!/usr/bin/env python3
"""播客助手技能打包脚本"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_meta(skill_path: Path) -> dict:
    """读取技能元数据"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")
    return json.loads(meta_file.read_text(encoding="utf-8"))


def scan_skill_files(skill_path: Path) -> list[Path]:
    """扫描技能目录中的所有文件"""
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.git',
        '.DS_Store',
        '*.log',
        '.env'
    ]

    files = []
    for item in skill_path.rglob('*'):
        if item.is_file():
            # 跳过排除项
            skip = False
            for pattern in exclude_patterns:
                if pattern.startswith('*.'):
                    if item.suffix == pattern[1:]:
                        skip = True
                        break
                elif pattern in str(item):
                    skip = True
                    break

            if not skip:
                files.append(item)

    return files


def create_package(skill_path: Path, output_dir: Path) -> Path:
    """创建技能包"""
    meta = get_skill_meta(skill_path)
    skill_name = meta.get("name", skill_path.name)
    version = meta.get("version", "1.0.0")

    # 生成文件名: skill-name_v1.0.0_20260401.skill
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{skill_name}_v{version}_{date_str}.skill"
    output_path = output_dir / filename

    # 创建ZIP包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 扫描文件
        for file_path in scan_skill_files(skill_path):
            # 计算相对路径
            rel_path = file_path.relative_to(skill_path)
            zf.write(file_path, rel_path)
            print(f"  + {rel_path}")

    return output_path


def main():
    skill_path = Path("/workspace/temp-skills/podcast-assistant")
    output_dir = Path("/workspace/temp-skills/packages")

    print("=" * 50)
    print("播客助手 - 技能打包")
    print("=" * 50)

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n技能路径: {skill_path}")
    print(f"输出目录: {output_dir}")
    print("\n打包文件:")

    try:
        output_path = create_package(skill_path, output_dir)
        print(f"\n打包成功: {output_path.name}")
        print(f"完整路径: {output_path}")
        return 0
    except Exception as e:
        print(f"\n打包失败: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
