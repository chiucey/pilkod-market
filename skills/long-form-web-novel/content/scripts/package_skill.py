#!/usr/bin/env python3
"""
技能打包脚本 - 将技能目录打包为.skill文件
"""

import os
import zipfile
import json
from datetime import datetime

def package_skill(skill_path, output_dir="."):
    """打包技能目录"""
    skill_name = os.path.basename(skill_path.rstrip('/'))
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 读取meta信息
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 创建zip包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除scripts目录（可选）
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arcname)

                # 添加元数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

    print(f"✅ 技能打包完成：{output_file}")
    print(f"   - 版本：v{meta['version']}")
    print(f"   - ID：{meta['id']}")
    return output_file

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    package_skill(skill_path, output_dir)