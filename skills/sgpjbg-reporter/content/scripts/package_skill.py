"""
打包技能为可分发的 .skill 文件
"""

import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


def package_skill(skill_path: str, output_dir: str = "/workspace/temp-skills") -> str:
    """将技能打包为 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取 meta 信息
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_name = meta.get('id', skill_path.name)
        version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_path.name}_v{version}_{timestamp}.skill"

    # 创建 zip 打包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏目录和 __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)

                # 安全检查：防止符号链接逃逸
                if '..' in str(arcname):
                    print(f"⚠️ 跳过不安全的文件: {arcname}")
                    continue

                zf.write(file_path, arcname)

    # 复制到标准名称
    standard_name = output_dir / f"{skill_path.name}.skill"
    shutil.copy(output_file, standard_name)

    return str(standard_name)


def main():
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = "/workspace/temp-skills/sgpjbg-reporter"

    print(f"打包技能: {skill_path}\n")

    try:
        output_file = package_skill(skill_path)
        print(f"✅ 打包成功!")
        print(f"📦 输出文件: {output_file}")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()