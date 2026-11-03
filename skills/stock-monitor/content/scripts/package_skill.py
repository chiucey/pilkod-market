#!/usr/bin/env python3
"""
package_skill.py - Stock Monitor Skill 打包脚本
================================================
将技能打包为可分发的 .skill 文件
"""

import os
import json
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent / "dist"

# 需要排除的文件和目录
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.db",  # 运行时数据库
    ".DS_Store",
    "*.log",
    "*.txt",  # 排除日志和文本文件
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    "*.egg-info",
    ".pytest_cache",
    "__pypackages__",
]

# 允许的代码文件扩展名
ALLOWED_EXTENSIONS = {
    ".py",   # Python
    ".json", # JSON配置
    ".md",   # Markdown文档
    ".yaml", # YAML配置
    ".yml",  # YAML配置
    ".env",  # 环境变量模板
    ".csv",  # 数据文件
    ".sql",  # SQL文件
}

# 允许的目录
ALLOWED_DIRS = {
    "",
    "data",
    "providers",
    "providers/intelligence",
    "references",
    "scripts",
    "assets",
}


def should_exclude(path: str) -> bool:
    """检查路径是否应该被排除"""
    path_lower = path.lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if path_lower.endswith(pattern[1:]):
                return True
        elif pattern in path_lower:
            return True
    return False


def is_allowed_file(filepath: Path) -> bool:
    """检查文件是否允许打包"""
    if filepath.suffix in ALLOWED_EXTENSIONS:
        return True
    # 特殊处理根目录的必要文件
    if filepath.parent == SKILL_DIR:
        if filepath.name in ["SKILL.md", "_meta.json"]:
            return True
    return False


def collect_files():
    """收集需要打包的文件"""
    files = []

    for root, dirs, filenames in os.walk(SKILL_DIR):
        root_path = Path(root)
        rel_root = root_path.relative_to(SKILL_DIR)

        # 检查目录是否允许
        rel_str = str(rel_root)
        if rel_str != "." and not any(
            rel_str.startswith(allowed) for allowed in ALLOWED_DIRS
        ):
            # 跳过不在白名单的目录
            continue

        # 过滤目录
        dirs[:] = [d for d in dirs if not should_exclude(d)]

        for filename in filenames:
            filepath = root_path / filename

            # 跳过应该排除的文件
            if should_exclude(str(filepath.relative_to(SKILL_DIR))):
                continue

            # 跳过不允许的文件（除非是根目录的必要文件）
            if not is_allowed_file(filepath) and filepath.parent == SKILL_DIR:
                continue

            rel_path = filepath.relative_to(SKILL_DIR)
            files.append({
                "path": str(rel_path),
                "full_path": filepath,
                "size": filepath.stat().st_size,
            })

    return files


def create_manifest(files: list) -> dict:
    """创建打包清单"""
    manifest = {
        "skill_name": "stock-monitor",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "total_files": len(files),
        "total_size": sum(f["size"] for f in files),
        "files": [
            {
                "path": f["path"],
                "size": f["size"],
                "checksum": hashlib.md5(f["full_path"].read_bytes()).hexdigest(),
            }
            for f in files
        ],
    }
    return manifest


def package_skill():
    """打包技能"""
    print("=" * 60)
    print("Stock Monitor Skill - 打包工具")
    print("=" * 60)

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 收集文件
    print("\n[1/4] 扫描文件...")
    files = collect_files()
    print(f"      找到 {len(files)} 个文件")

    # 创建清单
    print("\n[2/4] 创建清单...")
    manifest = create_manifest(files)

    # 创建zip包
    output_file = OUTPUT_DIR / "stock-monitor-1.0.0.skill"
    print(f"\n[3/4] 打包到 {output_file}...")

    # 使用有效的时间戳（1980年后）
    valid_date = (2024, 1, 1, 0, 0, 0)

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        # 添加清单
        manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
        zf.writestr("manifest.json", manifest_json)

        # 添加文件（使用有效时间戳避免ZIP错误）
        for file_info in files:
            arcname = file_info["path"]
            # 读取文件内容并用有效时间戳创建ZipInfo
            with open(file_info["full_path"], "rb") as f:
                content = f.read()
            zip_info = zipfile.ZipInfo(arcname, date_time=valid_date)
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zip_info, content)
            print(f"      + {arcname}")

    # 计算打包后的信息
    package_size = output_file.stat().st_size
    print(f"\n[4/4] 打包完成!")
    print("=" * 60)
    print(f"输出文件: {output_file}")
    print(f"文件大小: {package_size / 1024:.1f} KB")
    print(f"包含文件: {len(files)} 个")
    print("=" * 60)

    return output_file


def verify_package(package_path: Path):
    """验证打包结果"""
    print("\n验证打包结果...")

    with zipfile.ZipFile(package_path, "r") as zf:
        file_list = zf.namelist()

        # 检查必要文件
        required = ["SKILL.md", "_meta.json", "manifest.json"]
        for req in required:
            if req not in file_list:
                print(f"  ❌ 缺少必要文件: {req}")
                return False
            print(f"  ✅ {req}")

        # 检查内容
        for filename in file_list:
            if filename.endswith("/"):
                continue
            info = zf.getinfo(filename)
            print(f"  {filename}: {info.file_size} bytes")

    print("\n验证通过!")
    return True


if __name__ == "__main__":
    output = package_skill()
    verify_package(output)
    print(f"\n打包文件位置: {output.absolute()}")
