#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""
import json
import os
import shutil
import sys
import tempfile
import zipfile

def get_skill_meta(skill_path):
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_safe_path(path, base):
    """检查路径是否安全（防止符号链接逃逸）"""
    return os.path.realpath(path).startswith(os.path.realpath(base))

def package_skill(skill_path, output_dir="."):
    """打包技能为 .skill 文件"""
    skill_name = os.path.basename(skill_path.rstrip('/\\'))
    meta = get_skill_meta(skill_path)
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 输出文件名
    output_file = os.path.join(output_dir, f"{skill_name}_{skill_id}_{version}.skill")

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_skill = os.path.join(tmpdir, skill_name)
        os.makedirs(tmp_skill)

        # 复制文件（排除临时文件和隐藏文件）
        exclude_patterns = {'.git', '__pycache__', '.DS_Store', '*.pyc', '.env'}
        for root, dirs, files in os.walk(skill_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in exclude_patterns and not d.startswith('.')]

            for file in files:
                if file.startswith('.') or any(file.endswith(ext) for ext in ['.pyc', '.log']):
                    continue

                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, skill_path)
                dst = os.path.join(tmp_skill, rel_path)

                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

        # 创建 zip 包（使用 .skill 扩展名）
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp_skill):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, tmp_skill)
                    zf.write(file_path, arc_name)

    print(f"✅ 技能已打包: {output_file}")
    print(f"   技能ID: {skill_id}")
    print(f"   版本: {version}")
    return output_file


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # 转为绝对路径
    skill_path = os.path.abspath(skill_path)
    output_dir = os.path.abspath(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = package_skill(skill_path, output_dir)
    print(f"\n打包完成！")
    print(f"输出文件: {output_file}")


if __name__ == "__main__":
    main()
