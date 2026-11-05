#!/usr/bin/env python3
"""
项目管理技能打包脚本
生成 .skill 发布文件
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """打包技能到 .skill 文件"""

    skill_path = Path(skill_path)
    if output_dir is None:
        output_dir = Path("/workspace/temp-skills")

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # 读取元数据
    meta_path = skill_path / "_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    skill_name = skill_path.name
    skill_version = meta.get("version", "1.0.0")

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}-{skill_version}.skill"

    # 创建打包文件
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

    print(f"✓ Packaged: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    skill_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/project-management")
    output = package_skill(skill_path)
    print(f"Output: {output}")