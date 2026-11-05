"""
打包技能脚本
将技能文件夹打包成 .skill 文件
"""

import os
import zipfile
import json
from pathlib import Path
import shutil


def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    path = Path(skill_path)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (path / f).exists():
            print(f"缺少必需文件: {f}")
            return False

    # 验证 _meta.json
    with open(path / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            print("_meta.json 必须包含 id 和 version")
            return False

    # 验证 SKILL.md frontmatter
    with open(path / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            print("SKILL.md 必须以 YAML frontmatter 开头")
            return False

    return True


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = skill_path.parent
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_file = Path(output_dir) / f"{skill_name}.skill"

    # 验证技能结构
    if not validate_skill(skill_path):
        raise ValueError("技能结构验证失败")

    # 创建打包列表（排除脚本目录和临时文件）
    exclude_patterns = {'__pycache__', '.git', '.DS_Store', 'scripts'}
    files_to_package = []

    for root, dirs, files in os.walk(skill_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns]

        for file in files:
            if file.endswith('.pyc'):
                continue
            file_path = Path(root) / file
            rel_path = file_path.relative_to(skill_path)
            files_to_package.append(rel_path)

    # 创建 .skill 文件（本质是 zip）
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files_to_package:
            full_path = skill_path / file_path
            zf.write(full_path, file_path)
            print(f"  添加: {file_path}")

    print(f"\n打包完成: {output_file}")
    print(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")

    return str(output_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output = package_skill(skill_path, output_dir)
        print(f"\n技能包路径: {output}")
    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)
