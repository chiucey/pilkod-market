#!/usr/bin/env python3
"""
简历大师技能打包脚本
将技能打包成可分发的 .skill 文件
"""

import os
import shutil
import json
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_info(skill_path: str) -> dict:
    """读取技能元信息"""
    meta_path = Path(skill_path) / "_meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}


def create_package(skill_path: str, output_dir: str = None) -> str:
    """创建技能包"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    meta = get_skill_info(skill_path)
    skill_id = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_name = f"{skill_name}_{skill_id}_{version}_{timestamp}.skill"

    if output_dir:
        output_path = Path(output_dir) / output_name
    else:
        output_path = Path.cwd() / output_name

    # 创建zip包
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)

                # 跳过 .skill 文件本身（如果存在）
                if str(arcname).endswith('.skill'):
                    continue

                zf.write(file_path, arcname)

    print(f"✓ 技能包已生成: {output_path}")
    return str(output_path)


def main():
    skill_path = "/workspace/temp-skills/resume-master"

    print("=" * 50)
    print("简历大师技能 - 打包工具")
    print("=" * 50)

    # 验证技能存在
    if not Path(skill_path).exists():
        print(f"✗ 技能目录不存在: {skill_path}")
        return 1

    # 验证必要文件
    required = ["SKILL.md", "_meta.json"]
    for f in required:
        if not (Path(skill_path) / f).exists():
            print(f"✗ 缺少必要文件: {f}")
            return 1

    # 创建打包输出目录
    output_dir = Path(skill_path).parent / "dist"
    output_dir.mkdir(exist_ok=True)

    # 打包
    print("\n正在打包...")
    output_path = create_package(skill_path, str(output_dir))

    print("\n" + "=" * 50)
    print("打包完成！")
    print(f"输出文件: {output_path}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
