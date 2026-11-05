#!/usr/bin/env python3
"""
Skill打包脚本
"""
import os
import sys
import json
import shutil
import zipfile

def package_skill(skill_path, output_dir="."):
    """将Skill打包为.skill文件"""
    if not os.path.exists(skill_path):
        print(f"错误: 路径不存在 {skill_path}")
        return False

    skill_name = os.path.basename(skill_path.rstrip('/'))
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 读取meta
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        version = meta.get('version', '1.0.0')
    else:
        version = '1.0.0'

    # 创建打包目录
    temp_dir = f"/tmp/skill_package_{skill_name}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制文件（排除node_modules, __pycache__等）
    exclude_patterns = ['node_modules', '__pycache__', '.git', '*.pyc', '.DS_Store']
    for root, dirs, files in os.walk(skill_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns]

        for file in files:
            if any(file.endswith(p.replace('*', '')) for p in exclude_patterns if '*' in p):
                continue
            src = os.path.join(root, file)
            rel_path = os.path.relpath(src, skill_path)
            dst = os.path.join(temp_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # 创建.zip
    zip_path = f"/tmp/{skill_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arcname)

    # 移动到输出目录
    shutil.copy2(zip_path, output_file)

    # 清理
    shutil.rmtree(temp_dir)
    os.remove(zip_path)

    print(f"✓ 打包完成: {output_file}")
    print(f"  版本: {version}")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    package_skill(skill_path, output_dir)