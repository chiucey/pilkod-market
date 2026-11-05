#!/usr/bin/env python3
"""
技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import argparse
import hashlib
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path


def get_file_hash(file_path: Path) -> str:
    """计算文件的 SHA256 哈希"""
    sha256 = hashlib.sha256()
    sha256.update(file_path.read_bytes())
    return sha256.hexdigest()[:16]


def validate_skill_structure(skill_dir: Path) -> tuple:
    """验证技能目录结构"""
    errors = []
    warnings = []

    # 检查必需文件
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'

    if not skill_md.exists():
        errors.append("缺少 SKILL.md 文件")
    else:
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头")
        if 'name:' not in content:
            errors.append("SKILL.md 缺少 name 字段")
        if 'description:' not in content:
            errors.append("SKILL.md 缺少 description 字段")

    if not meta_json.exists():
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    # 检查目录名与 name 是否匹配
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            expected_name = meta.get('name', '')
            if expected_name and expected_name != skill_dir.name:
                warnings.append(
                    f"目录名 '{skill_dir.name}' 与 meta name '{expected_name}' 不匹配"
                )
        except:
            pass

    return errors, warnings


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """打包技能为 .skill 文件"""
    skill_dir = Path(skill_dir)

    if not skill_dir.exists() or not skill_dir.is_dir():
        raise FileNotFoundError(f"技能目录不存在: {skill_dir}")

    # 验证结构
    errors, warnings = validate_skill_structure(skill_dir)
    if errors:
        print("验证错误:")
        for err in errors:
            print(f"  ✗ {err}")
        raise ValueError("技能结构验证失败")

    if warnings:
        print("验证警告:")
        for warn in warnings:
            print(f"  ⚠ {warn}")

    # 读取元数据
    meta = json.loads((skill_dir / '_meta.json').read_text(encoding='utf-8'))
    skill_name = meta.get('name', skill_dir.name)
    skill_version = meta.get('version', '1.0.0')

    # 创建输出文件
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_dir.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{skill_name}.skill"

    # 创建 zip 包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    # 生成校验信息
    checksum = get_file_hash(output_file)
    manifest = {
        "name": skill_name,
        "version": skill_version,
        "packaged_at": datetime.now().isoformat(),
        "checksum": checksum,
        "files": [
            str(f.relative_to(skill_dir))
            for f in skill_dir.rglob('*')
            if f.is_file()
        ]
    }

    manifest_file = output_file.with_suffix('.skill.json')
    manifest_file.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print(f"✓ 技能已打包: {output_file}")
    print(f"✓ 校验和: {checksum}")

    return output_file


def main():
    parser = argparse.ArgumentParser(description='技能打包工具')
    parser.add_argument('skill_dir', help='技能目录路径')
    parser.add_argument('--output', '-o', help='输出目录')

    args = parser.parse_args()

    try:
        output_file = package_skill(Path(args.skill_dir), args.output)
        print(f"\n打包完成: {output_file}")
        return 0
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
