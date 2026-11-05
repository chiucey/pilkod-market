#!/usr/bin/env python3
"""
打包脚本 - 将科学家代理技能打包为 .skill 文件
"""
import os
import shutil
import json
from pathlib import Path
import zipfile
import sys

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能路径不存在: {skill_path}")

    # 读取 meta 信息
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        skill_id = meta.get("id", "unknown")
        version = meta.get("version", "1.0.0")
    else:
        skill_id = "unknown"
        version = "1.0.0"

    # 创建输出文件名
    output_name = f"scientist-agent-{version}.skill"
    if output_dir:
        output_path = Path(output_dir) / output_name
    else:
        output_path = skill_path.parent / output_name

    # 创建 zip 包（排除临时文件和隐藏文件）
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 跳过隐藏文件和临时文件
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if file_path.name.endswith('.pyc'):
                    continue
                if '__pycache__' in str(file_path):
                    continue

                # 添加到 zip，保持相对路径
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_path}")
    print(f"   技能ID: {skill_id}")
    print(f"   版本: {version}")
    return str(output_path)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/scientist-agent"
    package_skill(path)
