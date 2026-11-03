#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""
import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


DANGEROUS_PATTERNS = [
    ".env",
    ".pem",
    ".key",
    "credentials",
    "secrets",
    ".git",
    "__pycache__",
    ".DS_Store",
    "Thumbs.db",
    "node_modules",
    ".venv",
]


def is_safe_path(path: Path, base_path: Path) -> bool:
    """检查路径是否安全，排除敏感文件"""
    rel_path = path.relative_to(base_path)

    # 检查是否包含危险模式
    for part in rel_path.parts:
        if part in DANGEROUS_PATTERNS:
            return False
        if part.startswith('.') and part not in ['.']:
            return False

    # 检查文件扩展名
    if path.is_file():
        if path.suffix in ['.pyc', '.pyo', '.so', '.dll', '.exe']:
            return False

    return True


def scan_for_secrets(file_path: Path) -> bool:
    """扫描文件是否包含敏感信息"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        # 检查常见敏感信息模式
        dangerous_keywords = [
            "password", "api_key", "secret", "token",
            "private_key", "access_token", "auth_token"
        ]
        content_lower = content.lower()

        for keyword in dangerous_keywords:
            if keyword in content_lower and "=" in content:
                return True
    except Exception:
        pass
    return False


def get_file_hash(file_path: Path) -> str:
    """计算文件SHA256哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def package_skill(skill_path: Path, output_dir: Path = None) -> tuple[bool, str]:
    """打包技能为.skill文件"""
    skill_path = skill_path.resolve()

    if not skill_path.exists():
        return False, f"技能路径不存在: {skill_path}"

    # 读取meta信息
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "缺少 _meta.json 文件"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        skill_name = skill_path.name
        skill_version = meta.get("version", "1.0.0")
        skill_id = meta.get("id", "unknown")
    except Exception as e:
        return False, f"读取 _meta.json 失败: {e}"

    # 设置输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_v{skill_version}_{timestamp}.skill"

    # 创建zip文件
    files_info = []
    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_path):
                # 过滤目录
                dirs[:] = [d for d in dirs if is_safe_path(Path(root) / d, skill_path)]

                for file in files:
                    file_path = Path(root) / file

                    if not is_safe_path(file_path, skill_path):
                        print(f"跳过: {file_path.relative_to(skill_path)} (不安全)")
                        continue

                    # 跳过主meta文件本身（只在zip内添加内容）
                    if file_path == meta_file:
                        continue

                    # 检查敏感信息
                    if scan_for_secrets(file_path):
                        print(f"警告: {file_path.relative_to(skill_path)} 可能包含敏感信息")

                    # 添加到zip
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)

                    # 记录文件信息
                    files_info.append({
                        "path": str(arcname),
                        "hash": get_file_hash(file_path),
                        "size": file_path.stat().st_size
                    })

            # 添加元数据文件到zip
            zf.writestr("_meta.json", meta_file.read_text(encoding="utf-8"))

    except Exception as e:
        if output_file.exists():
            output_file.unlink()
        return False, f"打包失败: {e}"

    # 生成打包报告
    report = {
        "skill_name": skill_name,
        "skill_id": skill_id,
        "version": skill_version,
        "package_time": datetime.now().isoformat(),
        "file_count": len(files_info),
        "files": files_info,
        "package_hash": get_file_hash(output_file),
        "package_path": str(output_file)
    }

    report_file = output_dir / f"{skill_name}_v{skill_version}_{timestamp}_report.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return True, str(output_file)


def main():
    """主打包流程"""
    if len(sys.argv) < 2:
        skill_path = Path.cwd()
    else:
        skill_path = Path(sys.argv[1])

    print(f"打包技能: {skill_path}")
    print("=" * 50)

    success, result = package_skill(skill_path)

    if success:
        print(f"\n✓ 打包成功!")
        print(f"输出文件: {result}")
        return 0
    else:
        print(f"\n✗ 打包失败: {result}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
