#!/usr/bin/env python3
"""打包技能脚本 - 生成.skill归档文件"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(file_path: Path) -> str:
    """计算文件SHA256哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def package_skill(skill_path: str, output_dir: str = ".") -> tuple[bool, str]:
    """打包技能为.skill文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    if not skill_path.exists():
        return False, f"技能目录不存在: {skill_path}"

    # 读取meta信息
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "缺少_meta.json文件"

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')
    skill_name = meta.get('name', skill_path.name)

    # 创建打包目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}-{skill_version}-{timestamp}.skill"

    # 创建zip归档
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_path):
                # 排除__pycache__等目录
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

                for file in files:
                    file_path = Path(root) / file
                    # 计算相对路径
                    arcname = file_path.relative_to(skill_path)

                    # 安全检查：不允许符号链接逃逸
                    if '..' in str(arcname):
                        return False, f"检测到不安全的路径: {arcname}"

                    # 添加到归档
                    zf.write(file_path, arcname)

        return True, str(output_file)

    except Exception as e:
        return False, f"打包失败: {str(e)}"

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"打包技能: {skill_path}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)

    success, result = package_skill(skill_path, output_dir)

    if success:
        print(f"✅ 打包成功: {result}")
        return 0
    else:
        print(f"❌ 打包失败: {result}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
