#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_dir: Path) -> bool:
    """验证技能目录结构"""
    required_files = ["SKILL.md", "_meta.json"]

    for f in required_files:
        if not (skill_dir / f).exists():
            print(f"错误: 缺少必需文件 {f}")
            return False

    # 验证 _meta.json
    with open(skill_dir / "_meta.json") as f:
        meta = json.load(f)
        if "id" not in meta or "version" not in meta:
            print("错误: _meta.json 必须包含 id 和 version")
            return False

    # 验证 SKILL.md frontmatter
    with open(skill_dir / "SKILL.md") as f:
        content = f.read()
        if not content.startswith("---"):
            print("错误: SKILL.md 必须以 frontmatter 开始")
            return False
        if "name:" not in content or "description:" not in content:
            print("错误: SKILL.md frontmatter 必须包含 name 和 description")
            return False

    return True


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """打包技能目录为 .skill 文件"""

    skill_dir = Path(skill_dir)
    skill_name = skill_dir.name

    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_dir.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # 验证
    if not validate_skill(skill_dir):
        sys.exit(1)

    # 创建打包目录（排除临时文件和隐藏目录）
    temp_dir = output_dir / f".{skill_name}_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    shutil.copytree(skill_dir, temp_dir, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', '.DS_Store', '*.log'
    ))

    # 打包
    output_file = output_dir / f"{skill_name}.skill"
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"打包完成: {output_file}")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    package_skill(skill_dir, output_dir)
