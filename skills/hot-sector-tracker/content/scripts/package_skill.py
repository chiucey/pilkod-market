#!/usr/bin/env python3
"""打包技能为 .skill 文件"""
import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def package_skill(skill_path, output_dir=None):
    """将技能文件夹打包为 .skill 文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        print(f"错误: 技能路径不存在 {skill_path}")
        return None

    # 获取输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)

    # 读取 meta 获取版本
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        version = meta.get("version", "1.0.0")
        skill_id = meta.get("id", "unknown")
    else:
        version = "1.0.0"
        skill_id = "unknown"

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_path.name}_v{version}_{timestamp}.skill"

    # 创建 zip 包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/hot-sector-tracker"
    package_skill(skill_path)