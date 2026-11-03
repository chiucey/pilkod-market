#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可分发的.skill文件
"""

import os
import sys
import zipfile
import hashlib
import json
from pathlib import Path
from datetime import datetime

# ANSI颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BOLD}ℹ{RESET} {msg}")

def print_step(msg):
    print(f"\n{BOLD}→ {msg}{RESET}")

def get_file_hash(filepath):
    """计算文件SHA256哈希"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_manifest(skill_path):
    """创建打包清单"""
    manifest = {
        "created_at": datetime.now().isoformat(),
        "files": []
    }

    # 遍历所有文件
    for filepath in sorted(skill_path.rglob('*')):
        if filepath.is_file():
            rel_path = filepath.relative_to(skill_path)

            # 跳过隐藏文件和__pycache__
            if any(part.startswith('.') or part == '__pycache__' for part in rel_path.parts):
                continue

            file_info = {
                "path": str(rel_path),
                "size": filepath.stat().st_size,
                "hash": get_file_hash(filepath)
            }
            manifest["files"].append(file_info)

    return manifest

def validate_before_pack(skill_path):
    """打包前验证"""
    errors = []

    # 检查SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md不存在")
    else:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append("SKILL.md必须以frontmatter开头")

        if 'name:' not in content:
            errors.append("SKILL.md缺少name字段")

        if 'description:' not in content:
            errors.append("SKILL.md缺少description字段")

    # 检查_meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json不存在")
    else:
        try:
            import json
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
        except Exception as e:
            errors.append(f"_meta.json格式错误: {e}")

    # 检查路径名称
    for filepath in skill_path.rglob('*'):
        if filepath.is_file():
            if not filepath.name.isascii():
                errors.append(f"文件名包含非ASCII字符: {filepath.name}")

    return errors

def package_skill(skill_path, output_dir=None):
    """打包技能"""

    if not skill_path.exists():
        print_error(f"技能路径不存在: {skill_path}")
        sys.exit(1)

    print(f"\n{BOLD}{'='*50}")
    print(f"技能打包工具")
    print(f"{'='*50}{RESET}\n")

    print_info(f"技能路径: {skill_path}")

    # 1. 验证
    print_step("执行打包前验证...")
    errors = validate_before_pack(skill_path)
    if errors:
        print_error("验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print_success("验证通过")

    # 2. 读取meta信息
    print_step("读取技能元信息...")
    with open(skill_path / "_meta.json", 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = meta.get('name', skill_path.name)
    skill_id = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')

    print_success(f"技能名称: {skill_name}")
    print_success(f"技能ID: {skill_id}")
    print_success(f"技能版本: {skill_version}")

    # 3. 创建manifest
    print_step("创建文件清单...")
    manifest = create_manifest(skill_path)
    manifest_path = skill_path / "_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print_success(f"包含 {len(manifest['files'])} 个文件")

    # 4. 打包
    print_step("创建压缩包...")

    if output_dir is None:
        output_dir = skill_path.parent

    output_path = Path(output_dir)
    zip_filename = f"{skill_name}.skill"
    zip_filepath = output_path / zip_filename

    # 如果已存在则删除
    if zip_filepath.exists():
        zip_filepath.unlink()

    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath in skill_path.rglob('*'):
            if filepath.is_file():
                rel_path = filepath.relative_to(skill_path)

                # 跳过临时文件
                if any(part.startswith('.') or part == '__pycache__' for part in rel_path.parts):
                    continue

                # 排除manifest本身（只在本地生成）
                if rel_path.name == '_manifest.json':
                    continue

                zipf.write(filepath, rel_path)

    print_success(f"打包完成: {zip_filepath}")

    # 5. 清理临时文件
    if manifest_path.exists():
        manifest_path.unlink()

    # 6. 输出摘要
    print(f"\n{BOLD}{'='*50}")
    print("打包摘要")
    print(f"{'='*50}{RESET}\n")

    print_success(f"输出文件: {zip_filepath}")
    print_success(f"技能名称: {skill_name}")
    print_success(f"技能ID: {skill_id}")
    print_success(f"版本: {skill_version}")
    print_success(f"文件数量: {len(manifest['files'])}")
    print_success(f"包大小: {zip_filepath.stat().st_size / 1024:.2f} KB")

    return zip_filepath

def main():
    if len(sys.argv) < 2:
        # 默认打包当前目录
        skill_path = Path.cwd()
    else:
        skill_path = Path(sys.argv[1])

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_path, output_dir)

if __name__ == "__main__":
    main()
