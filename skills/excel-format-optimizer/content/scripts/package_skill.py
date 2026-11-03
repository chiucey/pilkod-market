#!/usr/bin/env python3
"""
Excel Format Optimizer - Package Script
打包技能为 .skill 文件用于分发
"""

import os
import json
import zipfile
import sys
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = ".") -> tuple[bool, str]:
    """打包技能目录为 .skill 文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        return False, f"路径不存在: {skill_path}"

    # 读取元数据
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "缺少 _meta.json"

    meta = json.loads(meta_file.read_text(encoding='utf-8'))
    skill_id = meta.get('id', skill_path.name)
    version = meta.get('version', '1.0.0')

    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = Path(output_dir) / f"{skill_path.name}_{version}_{timestamp}.skill"

    # 安全检查：禁止打包的文件
    forbidden_patterns = ['.env', '.pem', '.key', 'password', 'secret', '__pycache__']

    # 创建 zip 包
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_path):
                # 过滤目录
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

                for file in files:
                    filepath = Path(root) / file
                    rel_path = filepath.relative_to(skill_path)

                    # 安全检查
                    if any(p in str(filepath) for p in forbidden_patterns):
                        print(f"⚠️ 跳过安全检查文件: {rel_path}")
                        continue

                    zf.write(filepath, rel_path)

        return True, str(output_file)
    except Exception as e:
        return False, f"打包失败: {e}"


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"📦 打包技能: {skill_path}")
    print("=" * 50)

    success, result = package_skill(skill_path)

    if success:
        print(f"\n✅ 打包完成!")
        print(f"📁 输出文件: {result}")
        return 0
    else:
        print(f"\n❌ 打包失败: {result}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
