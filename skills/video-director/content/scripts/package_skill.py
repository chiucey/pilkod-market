"""
视频导演Skill打包脚本
Skill Packaging Script

将skill打包为可分发的.skill文件。
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime


class SkillPacker:
    """Skill打包器"""

    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else self.skill_path.parent / "dist"
        self.skill_name = self.skill_path.name
        self.manifest = {
            "name": self.skill_name,
            "created": datetime.now().isoformat(),
            "files": []
        }

    def package(self) -> str:
        """打包skill"""
        print(f"开始打包 skill: {self.skill_name}")
        print("=" * 60)

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 清理旧文件
        self._clean_output()

        # 收集所有文件
        files_to_package = self._collect_files()

        # 创建zip包
        output_file = self._create_archive(files_to_package)

        # 生成清单
        self._generate_manifest()

        # 复制_meta.json到输出目录
        meta_src = self.skill_path / "_meta.json"
        if meta_src.exists():
            shutil.copy(meta_src, self.output_dir / "_meta.json")

        print("\n" + "=" * 60)
        print(f"✅ 打包完成！")
        print(f"📦 输出文件: {output_file}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"📋 文件数量: {len(files_to_package)}")

        return str(output_file)

    def _clean_output(self) -> None:
        """清理输出目录"""
        output_file = self.output_dir / f"{self.skill_name}.skill"
        if output_file.exists():
            output_file.unlink()
            print(f"  ✓ 清理旧文件: {output_file}")

    def _collect_files(self) -> list[tuple[Path, str]]:
        """收集需要打包的文件"""
        files = []

        for root, dirs, filenames in os.walk(self.skill_path):
            root_path = Path(root)

            # 跳过 __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]

            for filename in filenames:
                file_path = root_path / filename

                # 计算相对路径
                rel_path = file_path.relative_to(self.skill_path)

                # 跳过 .skill 输出文件
                if rel_path.suffix == ".skill":
                    continue

                # 跳过 .pyc 文件
                if filename.endswith(".pyc"):
                    continue

                # 计算目标路径（使用正斜杠）
                target_path = str(rel_path).replace("\\", "/")

                files.append((file_path, target_path))
                print(f"  📄 {target_path}")

        return files

    def _create_archive(self, files: list[tuple[Path, str]]) -> Path:
        """创建zip归档"""
        output_file = self.output_dir / f"{self.skill_name}.skill"

        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for src_path, target_path in files:
                zf.write(src_path, target_path)
                self.manifest["files"].append(target_path)

        return output_file

    def _generate_manifest(self) -> None:
        """生成打包清单"""
        manifest_file = self.output_dir / f"{self.skill_name}_manifest.json"

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=2)

        print(f"  ✓ 清单已生成: {manifest_file}")


def main():
    """主函数"""
    import sys

    # 获取skill路径
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # 默认使用当前目录
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    packer = SkillPacker(skill_path)
    output_file = packer.package()

    print(f"\n打包文件位置: {output_file}")


if __name__ == "__main__":
    main()
