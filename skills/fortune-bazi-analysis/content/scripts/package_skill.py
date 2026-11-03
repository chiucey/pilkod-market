#!/usr/bin/env python3
"""
技能打包脚本
将技能文件夹打包为 .skill 文件（ZIP 格式）
"""

import os
import sys
import json
import zipfile
import subprocess

def get_version_from_meta(skill_path):
    """从 _meta.json 读取版本号"""
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get('version', '1.0.0')
    return '1.0.0'

def get_name_from_meta(skill_path):
    """从 _meta.json 读取技能名称"""
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get('name', 'unknown-skill')
    return 'unknown-skill'

def package_skill(skill_path, output_dir="."):
    """打包技能为 .skill 文件"""
    skill_name = get_name_from_meta(skill_path)
    version = get_version_from_meta(skill_path)

    # 生成输出文件名
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 创建 ZIP 包
    print(f"打包技能: {skill_name} v{version}")
    print(f"输出文件: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('__')]

            for file in files:
                if file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✅ 打包完成: {output_file}")
    return output_file

def main():
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    # 可选输出目录参数
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # 首先运行验证
    print("=" * 50)
    print("运行验证...")
    print("=" * 50)

    validate_script = os.path.join(skill_path, "scripts", "validate.py")
    if os.path.exists(validate_script):
        result = subprocess.run([sys.executable, validate_script, skill_path],
                              capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("验证失败，停止打包！")
            sys.exit(1)
    else:
        print("验证脚本不存在，跳过验证")

    print("\n" + "=" * 50)
    print("开始打包...")
    print("=" * 50)

    package_skill(skill_path, output_dir)

if __name__ == "__main__":
    main()
