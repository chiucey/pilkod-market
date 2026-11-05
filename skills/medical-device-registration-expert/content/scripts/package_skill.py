#!/usr/bin/env python3
"""
医疗器械注册专家技能打包脚本
将技能文件夹打包为 .skill 文件
"""

import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能路径不存在: {skill_path}")

    # 读取meta信息
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        skill_name = meta.get("id", skill_path.name)
        version = meta.get("version", "1.0.0")
    else:
        skill_name = skill_path.name
        version = "1.0.0"

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_{version}_{timestamp}.skill"

    # 打包
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_file.resolve())


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = package_skill(skill_path)
    print(f"✅ 技能已打包: {output_file}")