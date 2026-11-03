#!/usr/bin/env python3
"""
Skill打包脚本 - 将JPAF人格框架skill打包为可分发的.zip格式
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def load_meta(skill_dir: Path) -> dict:
    """加载_meta.json元数据"""
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing _meta.json in {skill_dir}")

    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_skill_structure(skill_dir: Path) -> list:
    """验证skill目录结构"""
    errors = []

    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_dir / f).exists():
            errors.append(f"Missing required file: {f}")

    # 检查_meta.json格式
    try:
        meta = load_meta(skill_dir)
        required_keys = ["id", "version"]
        for key in required_keys:
            if key not in meta:
                errors.append(f"Missing required key in _meta.json: {key}")
    except Exception as e:
        errors.append(f"Invalid _meta.json: {e}")

    # 检查SKILL.md格式
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md must start with YAML frontmatter (---)")
        if "name:" not in content:
            errors.append("SKILL.md missing 'name:' in frontmatter")
        if "description:" not in content:
            errors.append("SKILL.md missing 'description:' in frontmatter")

    return errors


def get_safe_files(skill_dir: Path) -> list:
    """获取要包含的安全文件列表"""
    files = []
    exclude_patterns = [
        "__pycache__",
        ".git",
        ".DS_Store",
        "*.pyc",
        "*.pyo",
        ".env",
    ]

    for root, dirs, filenames in os.walk(skill_dir):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns]

        for filename in filenames:
            if filename in exclude_patterns:
                continue
            if any(pattern in filename for pattern in exclude_patterns):
                continue

            full_path = Path(root) / filename
            rel_path = full_path.relative_to(skill_dir)
            files.append(rel_path)

    return files


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """打包skill为.zip文件"""
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    # 验证结构
    errors = validate_skill_structure(skill_dir)
    if errors:
        print("Validation errors:")
        for err in errors:
            print(f"  - {err}")
        raise ValueError("Skill validation failed")

    # 加载元数据
    meta = load_meta(skill_dir)

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_dir.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    output_name = f"{meta['id']}_v{meta['version']}_{timestamp}.zip"
    output_path = output_dir / output_name

    # 获取安全文件列表
    files = get_safe_files(skill_dir)

    # 创建zip文件
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = skill_dir / file_path
            zf.write(full_path, file_path)

    print(f"✓ Skill packaged successfully: {output_path}")
    print(f"  - Files included: {len(files)}")
    print(f"  - Version: {meta['version']}")
    print(f"  - ID: {meta['id']}")

    return output_path


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认打包当前目录
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    try:
        output_path = package_skill(skill_dir)
        print(f"\nPackage location: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
