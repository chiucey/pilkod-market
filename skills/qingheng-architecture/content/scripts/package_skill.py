#!/usr/bin/env python3
"""
青衡架构技能打包器
将技能打包为可分发的.skill文件
"""

import hashlib
import json
import os
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class QinghengPackager:
    """青衡架构技能打包器"""

    # 打包时需要排除的文件和目录模式
    EXCLUDE_PATTERNS: Set[str] = {
        ".git",
        ".gitignore",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        "Thumbs.db",
        "node_modules",
        ".venv",
        "venv",
        "*.log",
        ".tmp",
        "tmp",
    }

    # 敏感文件模式（绝对排除）
    SENSITIVE_PATTERNS: Set[str] = {
        ".env",
        ".pem",
        ".key",
        "*.key",
        "credentials",
        "secrets",
        "id_rsa",
        "id_dsa",
    }

    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else Path(".")

        if not self.skill_path.exists():
            raise FileNotFoundError(f"技能路径不存在: {skill_path}")

        self.skill_name = self.skill_path.name
        self.package_info: Dict = {}

    def should_exclude(self, path: Path, is_dir: bool = False) -> bool:
        """检查路径是否应该被排除"""
        path_name = path.name

        # 检查排除模式
        for pattern in self.EXCLUDE_PATTERNS:
            if is_dir and pattern.rstrip("/") == path_name:
                return True
            if path.match(pattern):
                return True

        # 检查敏感文件模式
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in str(path):
                return True

        return False

    def collect_files(self) -> List[Path]:
        """收集需要打包的文件"""
        files = []

        for root, dirs, filenames in os.walk(self.skill_path):
            root_path = Path(root)

            # 过滤目录
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d, is_dir=True)]

            for filename in filenames:
                file_path = root_path / filename
                if not self.should_exclude(file_path):
                    # 计算相对路径
                    rel_path = file_path.relative_to(self.skill_path)
                    files.append((file_path, rel_path))

        return files

    def calculate_checksums(self, files: List[Path]) -> Dict[str, str]:
        """计算文件的SHA256校验和"""
        checksums = {}

        for file_path in files:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            checksums[str(file_path)] = sha256_hash.hexdigest()

        return checksums

    def create_manifest(self, files: List[tuple], checksums: Dict[str, str]) -> Dict:
        """创建打包清单"""
        file_list = []
        for abs_path, rel_path in files:
            file_info = {
                "path": str(rel_path),
                "size": abs_path.stat().st_size,
                "checksum": checksums[str(abs_path)],
            }
            file_list.append(file_info)

        manifest = {
            "skill_name": self.skill_name,
            "created_at": datetime.now().isoformat(),
            "files": file_list,
            "total_files": len(file_list),
            "total_size": sum(f["size"] for f in file_list),
        }

        return manifest

    def package(self) -> Path:
        """执行打包操作"""
        print(f"开始打包技能: {self.skill_name}")
        print("-" * 50)

        # 收集文件
        print("📁 收集文件...")
        files = self.collect_files()
        print(f"   找到 {len(files)} 个文件")

        if not files:
            raise ValueError("没有找到需要打包的文件")

        # 计算校验和
        print("🔐 计算校验和...")
        checksums = self.calculate_checksums([abs_p for abs_p, _ in files])

        # 创建清单
        print("📋 创建清单...")
        manifest = self.create_manifest(files, checksums)
        self.package_info = manifest

        # 创建临时目录用于打包
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 写入清单文件
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            # 复制文件
            print("📦 复制文件...")
            for abs_path, rel_path in files:
                dest_path = temp_path / "data" / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(abs_path, dest_path)

            # 创建tar.gz归档
            print("🗜️  创建归档...")
            output_file = self.output_dir / f"{self.skill_name}.skill"

            with tarfile.open(output_file, "w:gz") as tar:
                # 添加清单
                tar.add(manifest_path, arcname="manifest.json")

                # 添加数据文件
                data_dir = temp_path / "data"
                for file_path in data_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = f"data/{file_path.relative_to(data_dir)}"
                        tar.add(file_path, arcname=arcname)

            print(f"   输出文件: {output_file}")
            print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")

        # 验证打包结果
        print("✅ 验证打包结果...")
        if not self.verify_package(output_file):
            raise RuntimeError("打包验证失败")

        print("-" * 50)
        print(f"🎉 打包完成！")
        print(f"   技能名称: {self.skill_name}")
        print(f"   文件总数: {manifest['total_files']}")
        print(f"   总大小: {manifest['total_size'] / 1024:.2f} KB")
        print(f"   输出路径: {output_file}")

        return output_file

    def verify_package(self, package_path: Path) -> bool:
        """验证打包结果"""
        try:
            with tarfile.open(package_path, "r:gz") as tar:
                members = tar.getmembers()

                # 检查清单文件
                if "manifest.json" not in [m.name for m in members]:
                    print("   ❌ 缺少manifest.json")
                    return False

                # 检查数据目录
                data_files = [m for m in members if m.name.startswith("data/")]
                if not data_files:
                    print("   ❌ 缺少数据文件")
                    return False

                # 验证清单中的文件都存在
                manifest_data = tar.extractfile("manifest.json")
                if manifest_data:
                    manifest = json.loads(manifest_data.read().decode("utf-8"))
                    packaged_files = {m.name.replace("data/", "") for m in data_files}
                    manifest_files = {f["path"] for f in manifest["files"]}

                    missing = manifest_files - packaged_files
                    if missing:
                        print(f"   ❌ 缺少文件: {missing}")
                        return False

            return True
        except Exception as e:
            print(f"   ❌ 验证异常: {str(e)}")
            return False

    def extract_package(self, package_path: Path, extract_dir: Path) -> bool:
        """解压包到指定目录（用于测试）"""
        try:
            extract_dir = Path(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)

            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(extract_dir)

            print(f"   已解压到: {extract_dir}")
            return True
        except Exception as e:
            print(f"   ❌ 解压失败: {str(e)}")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <技能路径> [输出目录]")
        print("示例: python package_skill.py /workspace/temp-skills/qingheng-architecture")
        print("示例: python package_skill.py /workspace/temp-skills/qingheng-architecture /workspace/output")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        packager = QinghengPackager(skill_path, output_dir)
        output_file = packager.package()

        print("\n" + "=" * 50)
        print("打包摘要:")
        print(f"  输出文件: {output_file}")
        print(f"  技能名称: {packager.skill_name}")
        print(f"  文件数量: {packager.package_info.get('total_files', 0)}")
        print(f"  总大小: {packager.package_info.get('total_size', 0) / 1024:.2f} KB")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 打包失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
