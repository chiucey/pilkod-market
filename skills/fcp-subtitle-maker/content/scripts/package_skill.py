#!/usr/bin/env python3
"""
FCP Subtitle Maker Skill - Package Script
打包技能为 .skill 文件用于发布
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


# 需要排除的文件和目录模式
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '.git',
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    '.env',
    '.venv',
    'venv',
    'node_modules',
    '.idea',
    '.vscode',
    '*.swp',
    '*.swo',
    '*~',
]

# 敏感文件模式（如果存在则跳过整个打包）
FORBIDDEN_PATTERNS = [
    '.env',
    'credentials',
    'secrets',
    'id_rsa',
    '*.pem',
    '*.key',
    '*.sqlite',
    '*.db',
]


def should_exclude(path: str) -> bool:
    """检查路径是否应该被排除"""
    path_lower = path.lower()
    for pattern in EXCLUDE_PATTERNS:
        pattern_lower = pattern.lower()
        if pattern_lower.startswith('*'):
            # 通配符模式
            if path_lower.endswith(pattern_lower[1:]):
                return True
        else:
            # 目录/文件名模式
            if f'/{pattern_lower}/' in path_lower or path_lower.endswith(f'/{pattern_lower}'):
                return True
    return False


def has_forbidden_content(skill_path: Path) -> tuple[bool, list[str]]:
    """检查是否有禁止的内容"""
    forbidden_found = []
    for root, dirs, files in os.walk(skill_path):
        for f in files:
            f_lower = f.lower()
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.lower() in f_lower:
                    forbidden_found.append(os.path.join(root, f))

        for d in dirs:
            d_lower = d.lower()
            for pattern in ['.git', 'node_modules', 'venv', '__pycache__']:
                if d_lower == pattern:
                    forbidden_found.append(os.path.join(root, d))

    return len(forbidden_found) > 0, forbidden_found


def create_skill_package(skill_path: str, output_path: str = None) -> str:
    """
    创建技能包

    Args:
        skill_path: 技能目录路径
        output_path: 输出文件路径（可选，默认生成 timestamp.skill）

    Returns:
        生成的 .skill 文件路径
    """
    skill = Path(skill_path).resolve()

    if not skill.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # 读取 meta 信息
    meta_file = skill / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("Missing _meta.json")

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = skill.name
    skill_version = meta.get("version", "0.0.0")
    skill_id = meta.get("id", "unknown")

    # 确定输出路径
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{skill_name}_{skill_version}_{timestamp}.skill"
    else:
        output_path = str(output_path)

    # 确保输出目录存在
    output_dir = Path(output_path).parent
    if output_dir != Path('.'):
        output_dir.mkdir(parents=True, exist_ok=True)

    # 检查禁止内容
    has_forbidden, forbidden_list = has_forbidden_content(skill)
    if has_forbidden:
        print("Warning: Found potentially sensitive files:")
        for f in forbidden_list:
            print(f"  - {f}")
        print("These files will be excluded from the package.")

    # 创建临时目录用于构建包
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建包结构
        package_dir = temp_path / f"{skill_name}"
        package_dir.mkdir()

        # 复制文件（排除敏感文件）
        files_copied = []
        files_excluded = []

        for root, dirs, files in os.walk(skill):
            # 计算相对路径
            rel_root = Path(root).relative_to(skill)

            # 检查目录是否应该被排除
            dirs[:] = [d for d in dirs if not should_exclude(str(rel_root / d))]

            for f in files:
                src = Path(root) / f
                rel_path = rel_root / f

                # 检查是否应该排除
                if should_exclude(str(rel_path)):
                    files_excluded.append(str(rel_path))
                    continue

                # 检查是否包含敏感内容
                if any(pattern.lower() in str(rel_path).lower() for pattern in FORBIDDEN_PATTERNS):
                    files_excluded.append(str(rel_path))
                    continue

                # 复制文件
                dst = package_dir / rel_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                files_copied.append(str(rel_path))

        # 创建包
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_copied:
                full_path = package_dir / file_path
                arcname = file_path
                zf.write(full_path, arcname)

        # 打印统计信息
        print(f"\nPackage created: {output_path}")
        print(f"  Skill: {skill_name}")
        print(f"  Version: {skill_version}")
        print(f"  ID: {skill_id}")
        print(f"  Files: {len(files_copied)}")

        if files_excluded:
            print(f"  Excluded: {len(files_excluded)}")

        # 获取包大小
        file_size = Path(output_path).stat().st_size
        print(f"  Package size: {file_size / 1024:.1f} KB")

        return output_path


def extract_skill_package(skill_file: str, extract_to: str = None) -> str:
    """
    解压技能包（用于验证）

    Args:
        skill_file: .skill 文件路径
        extract_to: 解压目标目录

    Returns:
        解压后的目录路径
    """
    skill_path = Path(skill_file)

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_file}")

    if extract_to is None:
        extract_to = skill_path.stem  # 使用文件名（不含扩展名）作为目录名

    extract_path = Path(extract_to)
    extract_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(skill_path, 'r') as zf:
        zf.extractall(extract_path)

    print(f"Extracted to: {extract_path}")
    return str(extract_path)


def verify_package(skill_file: str) -> bool:
    """
    验证技能包完整性

    Args:
        skill_file: .skill 文件路径

    Returns:
        是否验证通过
    """
    skill_path = Path(skill_file)

    try:
        with zipfile.ZipFile(skill_path, 'r') as zf:
            # 检查必要文件是否存在
            required_files = ['SKILL.md', '_meta.json']
            names = zf.namelist()

            for req in required_files:
                # 检查根目录下是否有该文件（可能带前缀目录）
                found = any(n.endswith(f'/{req}') or n == req for n in names)
                if not found:
                    print(f"Missing required file: {req}")
                    return False

            # 检查 meta.json 格式
            for name in names:
                if name.endswith('_meta.json'):
                    meta_content = zf.read(name).decode('utf-8')
                    meta = json.loads(meta_content)
                    if 'id' not in meta or 'version' not in meta:
                        print(f"Invalid _meta.json in {name}")
                        return False

        print("Package verification passed")
        return True

    except zipfile.BadZipFile:
        print("Invalid ZIP file")
        return False
    except Exception as e:
        print(f"Verification error: {e}")
        return False


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python package_skill.py <skill_path> [output_path]")
        print("  python package_skill.py --verify <skill.skill>")
        print("  python package_skill.py --extract <skill.skill> [output_dir]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == '--verify':
        # 验证模式
        skill_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not skill_file:
            print("Error: Missing skill file path")
            sys.exit(1)
        success = verify_package(skill_file)
        sys.exit(0 if success else 1)

    elif cmd == '--extract':
        # 解压模式
        skill_file = sys.argv[2] if len(sys.argv) > 2 else None
        extract_to = sys.argv[3] if len(sys.argv) > 3 else None
        if not skill_file:
            print("Error: Missing skill file path")
            sys.exit(1)
        extract_skill_package(skill_file, extract_to)

    else:
        # 打包模式
        skill_path = cmd
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        create_skill_package(skill_path, output_path)


if __name__ == "__main__":
    main()
