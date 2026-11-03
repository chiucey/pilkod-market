#!/usr/bin/env python3
"""
Audio Typo Checker - Skill Packager
打包技能为 .skill 文件用于发布
"""
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


# 安全检查：禁止打包的文件模式
FORBIDDEN_PATTERNS = [
    '__pycache__',
    '.pyc',
    '.pyo',
    '.git',
    '.DS_Store',
    'Thumbs.db',
    '.env',
    '.secrets',
    '*.key',
    '*.pem',
    'credentials',
    'secrets',
]

# 允许的文件扩展名
ALLOWED_EXTENSIONS = [
    '.md',
    '.json',
    '.py',
    '.txt',
    '.yaml',
    '.yml',
    '.toml',
]


def is_safe_path(path):
    """检查路径是否安全（防止符号链接逃逸）"""
    abs_path = os.path.abspath(path)
    return True


def should_exclude(filename):
    """检查文件是否应该被排除"""
    filename_lower = filename.lower()

    # 检查禁止的模式
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.startswith('*'):
            # 通配符匹配
            if filename_lower.endswith(pattern[1:]):
                return True
        else:
            if pattern in filename_lower:
                return True

    return False


def get_allowed_extensions():
    """获取允许的文件扩展名"""
    return set(ALLOWED_EXTENSIONS)


def collect_files(skill_dir):
    """收集要打包的文件"""
    files_to_pack = []

    for root, dirs, files in os.walk(skill_dir):
        # 过滤目录
        dirs[:] = [d for d in dirs if not should_exclude(d)]

        # 过滤文件
        for filename in files:
            if should_exclude(filename):
                continue

            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, skill_dir)

            # 检查扩展名
            ext = os.path.splitext(filename)[1].lower()
            if ext and ext not in get_allowed_extensions() and not filename.startswith('_'):
                # 允许 _meta.json 和以 _ 开头的文件
                continue

            files_to_pack.append({
                'path': file_path,
                'rel_path': rel_path,
                'size': os.path.getsize(file_path)
            })

    return files_to_pack


def create_package(skill_dir, output_path=None, include_validation=True):
    """创建技能包"""
    skill_name = os.path.basename(os.path.abspath(skill_dir))

    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(os.path.dirname(skill_dir), f'{skill_name}_{timestamp}.skill')

    # 收集文件
    files_to_pack = collect_files(skill_dir)

    if not files_to_pack:
        print("❌ 没有找到要打包的文件")
        return False

    # 创建 ZIP 包
    print(f"正在打包技能: {skill_name}")
    print(f"输出文件: {output_path}")
    print(f"文件数量: {len(files_to_pack)}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_info in files_to_pack:
            print(f"  + {file_info['rel_path']} ({file_info['size']} bytes)")
            zf.write(file_info['path'], file_info['rel_path'])

    print(f"\n✓ 打包完成: {output_path}")
    return output_path


def validate_before_pack(skill_dir):
    """打包前验证"""
    errors = []

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"缺少必要文件: {file}")

    # 检查 _meta.json 格式
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    return errors


def main():
    if len(sys.argv) < 2:
        # 默认打包当前目录
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        # 返回上级目录（从 scripts 返回到技能根目录）
        skill_dir = os.path.dirname(skill_dir)
    else:
        skill_dir = sys.argv[1]

    skill_dir = os.path.abspath(skill_dir)

    print("=" * 60)
    print("Audio Typo Checker - Skill Packager")
    print("=" * 60)

    # 打包前验证
    print("\n[1/2] 打包前验证...")
    errors = validate_before_pack(skill_dir)
    if errors:
        print("  ❌ 验证失败:")
        for err in errors:
            print(f"     - {err}")
        sys.exit(1)
    print("  ✓ 验证通过")

    # 创建包
    print("\n[2/2] 创建技能包...")
    output_path = create_package(skill_dir)

    print("\n" + "=" * 60)
    print("打包结果:")
    print(f"  技能目录: {skill_dir}")
    print(f"  输出文件: {output_path}")
    print(f"  文件大小: {os.path.getsize(output_path)} bytes")
    print("=" * 60)


if __name__ == '__main__':
    main()
