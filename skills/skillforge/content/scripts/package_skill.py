#!/usr/bin/env python3
"""
SkillForge - Skill 打包脚本

将 Skill 目录打包为可分发的 .skill 文件。
"""

import sys
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class SkillPacker:
    """Skill 打包器"""

    # 排除的文件和目录
    EXCLUDE_PATTERNS = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        ".env",
        ".venv",
        "node_modules",
        ".pytest_cache",
        ".tox",
    ]

    def __init__(self, skill_path: str, output_dir: Optional[str] = None):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir or ".").resolve()
        self.issues: List[str] = []

    def pack(self) -> Optional[Path]:
        """
        执行打包流程。
        返回: 打包后的 .skill 文件路径，失败返回 None
        """
        # 1. 验证 Skill 目录
        if not self.validate():
            self.print_error("验证失败，无法打包")
            return None

        # 2. 读取元数据
        meta = self.read_meta()

        # 3. 生成输出文件名
        skill_name = meta.get("name", self.skill_path.name)
        output_name = f"{skill_name}.skill"
        output_path = self.output_dir / output_name

        # 4. 创建 ZIP 包
        try:
            self.create_zip(output_path)
            self.print_success(f"打包成功: {output_path}")
            return output_path
        except Exception as e:
            self.print_error(f"打包失败: {e}")
            return None

    def validate(self) -> bool:
        """验证 Skill 目录"""
        # 检查目录存在
        if not self.skill_path.exists():
            self.issues.append(f"目录不存在: {self.skill_path}")
            return False

        if not self.skill_path.is_dir():
            self.issues.append(f"路径不是目录: {self.skill_path}")
            return False

        # 检查必需文件
        required_files = ["SKILL.md", "_meta.json"]
        for file in required_files:
            file_path = self.skill_path / file
            if not file_path.exists():
                self.issues.append(f"缺少必需文件: {file}")

        # 检查 SKILL.md 格式
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            if not content.startswith("---"):
                self.issues.append("SKILL.md 必须以 YAML frontmatter 开始")

        # 检查 _meta.json 格式
        meta = self.read_meta()
        if not meta:
            self.issues.append("_meta.json 格式错误或缺失")
        else:
            required_keys = ["id", "version"]
            for key in required_keys:
                if key not in meta:
                    self.issues.append(f"_meta.json 缺少必需字段: {key}")

        return len(self.issues) == 0

    def read_meta(self) -> Dict:
        """读取元数据"""
        meta_path = self.skill_path / "_meta.json"
        if not meta_path.exists():
            return {}

        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def should_exclude(self, path: Path) -> bool:
        """检查是否应该排除"""
        name = path.name

        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith("*."):
                ext = pattern[1:]
                if name.endswith(ext):
                    return True
            elif pattern in name:
                return True

        return False

    def collect_files(self, base_path: Path) -> List[Path]:
        """收集需要打包的文件"""
        files = []

        for item in base_path.rglob("*"):
            if item.is_file() and not self.should_exclude(item):
                files.append(item)

        return files

    def create_zip(self, output_path: Path) -> None:
        """创建 ZIP 包"""
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 如果已存在，先删除
        if output_path.exists():
            output_path.unlink()

        # 创建 ZIP
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            files = self.collect_files(self.skill_path)

            for file_path in files:
                # 计算相对于 skill 目录的路径
                arcname = str(file_path.relative_to(self.skill_path))
                zf.write(file_path, arcname)

        # 验证 ZIP
        with zipfile.ZipFile(output_path, "r") as zf:
            file_count = len(zf.namelist())
            total_size = sum(info.file_size for info in zf.infolist())
            print(f"  包含 {file_count} 个文件, 总计 {self.format_size(total_size)}")

    def format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ["B", "KB", "MB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"

    def print_error(self, msg: str) -> None:
        """打印错误"""
        print(f"[错误] {msg}")
        if self.issues:
            print("\n问题详情:")
            for issue in self.issues:
                print(f"  - {issue}")

    def print_success(self, msg: str) -> None:
        """打印成功"""
        print(f"[成功] {msg}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill-directory> [output-directory]")
        print("\n示例:")
        print("  python package_skill.py /path/to/skillforge")
        print("  python package_skill.py /path/to/skillforge ./output")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"正在打包 Skill: {skill_path}")
    print("-" * 50)

    packer = SkillPacker(skill_path, output_dir)
    output_path = packer.pack()

    if output_path:
        print("-" * 50)
        print(f"\n打包完成！")
        print(f"输出文件: {output_path}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
