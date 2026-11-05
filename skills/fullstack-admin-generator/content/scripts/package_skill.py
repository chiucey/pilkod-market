#!/usr/bin/env python3
"""技能打包脚本 - 将技能打包为 .skill 文件"""

import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能目录为 .skill 文件"""
    skill_path = Path(skill_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    # 生成输出文件名
    skill_name = skill_path.name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 创建 zip 包
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                if file.startswith("."):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_file)

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"✅ 技能打包成功: {output_file}")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)
