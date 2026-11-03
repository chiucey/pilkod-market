#!/usr/bin/env python3
"""
贾维斯技能打包脚本
将技能打包为 .skill 文件用于分发
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.output_dir = self.skill_path.parent

    def package(self) -> str:
        """打包技能"""
        # 读取meta信息
        meta_path = self.skill_path / "_meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        skill_name = meta.get("name", "unknown")
        version = meta.get("version", "1.0.0")

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_name = f"{skill_name}-{version}.skill"
        output_path = self.output_dir / output_name

        print(f"打包技能: {skill_name}")
        print(f"版本: {version}")
        print(f"输出文件: {output_path}")

        # 创建zip包
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.skill_path.rglob("*"):
                if file_path.is_file():
                    # 计算相对路径
                    rel_path = file_path.relative_to(self.skill_path)
                    # 排除脚本目录
                    if not any(part == 'scripts' for part in rel_path.parts):
                        zf.write(file_path, rel_path)
                        print(f"  + {rel_path}")

        print(f"\n✅ 打包完成: {output_path}")
        return str(output_path)

    def validate_package(self, package_path: str) -> bool:
        """验证打包内容"""
        print(f"\n验证打包内容...")

        with zipfile.ZipFile(package_path, 'r') as zf:
            files = zf.namelist()

            # 检查必需文件
            required = ["SKILL.md", "_meta.json"]
            for item in required:
                if item not in files:
                    print(f"  ❌ 缺少必需文件: {item}")
                    return False

            print(f"  ✅ 包含 {len(files)} 个文件")
            for f in files:
                print(f"     - {f}")

        return True


def main():
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    packager = SkillPackager(skill_path)

    print("=" * 50)
    print("贾维斯技能打包")
    print("=" * 50)

    try:
        package_path = packager.package()

        if packager.validate_package(package_path):
            print("\n🟢 打包成功！")
            print(f"\n技能文件路径: {package_path}")
        else:
            print("\n🟡 打包完成但验证有问题")

    except Exception as e:
        print(f"\n❌ 打包失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
