#!/usr/bin/env python3
"""
技能打包脚本 - 生成 .skill 分发包
"""
import os
import zipfile
import json
import sys
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = "."):
    """打包技能为 .skill 文件"""

    # 验证目录结构
    if not os.path.exists(skill_path):
        print(f"错误: 路径不存在 {skill_path}")
        return False

    skill_name = os.path.basename(skill_path)
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        print("错误: _meta.json 不存在")
        return False

    # 读取版本信息
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    version = meta.get("version", "1.0.0")
    skill_id = meta.get("id", "unknown")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{version}_{timestamp}.skill")

    # 打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arc_name)

    print(f"✅ 技能已打包: {output_file}")
    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(path)