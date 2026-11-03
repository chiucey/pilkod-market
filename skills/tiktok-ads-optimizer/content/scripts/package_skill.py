#!/usr/bin/env python3
"""
技能打包脚本 - 将TikTok广告优化技能打包为可分发格式
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPacker:
    """技能打包器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.output_dir = Path("/workspace/temp-skills/dist")
        self.ignore_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".git",
            ".DS_Store",
            "*.log",
            ".env",
            "node_modules",
            ".venv",
            "venv",
            "*.egg-info",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "dist",
            "build",
        ]

    def pack(self) -> str:
        """打包技能"""
        print("=" * 60)
        print("TikTok广告优化技能 - 打包工具")
        print("=" * 60)
        print()

        # 验证目录结构
        if not self.validate_structure():
            print("❌ 目录结构验证失败")
            return None

        # 读取元数据
        meta = self.read_meta()

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成打包文件名
        version = meta.get("version", "1.0.0")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_name = f"{self.skill_name}_v{version}_{timestamp}.skill"
        output_path = self.output_dir / output_name

        # 创建ZIP包
        print(f"📦 正在打包...")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            self.add_files_to_zip(zipf, self.skill_path, self.skill_path)

        # 创建manifest
        manifest = {
            "name": self.skill_name,
            "version": version,
            "packaged_at": datetime.now().isoformat(),
            "files": self.list_files(),
            "size": output_path.stat().st_size
        }

        manifest_path = self.output_dir / f"{self.skill_name}_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print()
        print("=" * 60)
        print("打包完成！")
        print("=" * 60)
        print(f"📦 包文件: {output_path}")
        print(f"📄 Manifest: {manifest_path}")
        print(f"📊 文件数量: {manifest['files']}")
        print(f"💾 包大小: {manifest['size'] / 1024:.2f} KB")
        print()

        return str(output_path)

    def validate_structure(self) -> bool:
        """验证技能目录结构"""
        print("🔍 验证目录结构...")

        # 检查必需文件
        required_files = ["SKILL.md", "_meta.json"]
        for filename in required_files:
            file_path = self.skill_path / filename
            if not file_path.exists():
                print(f"  ❌ 缺少文件: {filename}")
                return False
            print(f"  ✅ {filename}")

        # 检查目录
        for dirname in ["scripts", "references"]:
            dir_path = self.skill_path / dirname
            if dir_path.exists():
                print(f"  ✅ 目录: {dirname}")

        print()
        return True

    def read_meta(self) -> dict:
        """读取元数据"""
        meta_path = self.skill_path / "_meta.json"
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_files(self) -> int:
        """列出所有文件"""
        count = 0
        for root, dirs, files in os.walk(self.skill_path):
            # 过滤忽略模式
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            files = [f for f in files if not any(
                pattern.replace("*", "") in f for pattern in self.ignore_patterns
            )]
            count += len(files)
        return count

    def should_ignore(self, path: Path) -> bool:
        """检查是否应该忽略"""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern.startswith("*"):
                if pattern[1:] in path_str:
                    return True
            else:
                if pattern in path_str:
                    return True
        return False

    def add_files_to_zip(self, zipf: zipfile.ZipFile, base_path: Path, current_path: Path) -> None:
        """递归添加文件到ZIP"""
        for item in sorted(current_path.iterdir()):
            if self.should_ignore(item):
                continue

            if item.is_dir():
                self.add_files_to_zip(zipf, base_path, item)
            else:
                arcname = item.relative_to(base_path)
                zipf.write(item, arcname)
                print(f"  📄 {arcname}")


def unpack(skill_package: str, output_dir: str) -> bool:
    """解包技能"""
    print("=" * 60)
    print("解包技能包")
    print("=" * 60)
    print()

    skill_path = Path(skill_package)
    output_path = Path(output_dir)

    if not skill_path.exists():
        print(f"❌ 文件不存在: {skill_package}")
        return False

    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"📦 正在解包: {skill_package}")
    print(f"📂 输出目录: {output_path}")
    print()

    with zipfile.ZipFile(skill_path, 'r') as zipf:
        zipf.extractall(output_path)

    print()
    print("✅ 解包完成！")
    return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  打包: python package_skill.py pack <skill_path>")
        print("  解包: python package_skill.py unpack <skill_package> <output_dir>")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "pack":
        skill_path = sys.argv[2] if len(sys.argv) > 2 else "/workspace/temp-skills/tiktok-ads-optimizer"
        packer = SkillPacker(skill_path)
        packer.pack()

    elif command == "unpack":
        if len(sys.argv) < 4:
            print("❌ 请提供输出目录")
            sys.exit(1)
        skill_package = sys.argv[2]
        output_dir = sys.argv[3]
        unpack(skill_package, output_dir)

    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
