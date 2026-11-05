"""打包脚本：将技能文件夹压缩为 .skill 文件"""

import os
import shutil
import sys
import zipfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(SKILL_DIR, "dist")


def package_skill():
    skill_name = os.path.basename(SKILL_DIR)
    output_path = os.path.join(OUTPUT_DIR, f"{skill_name}.skill")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(output_path):
        os.remove(output_path)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # 排除 __pycache__ 和 .pyc 文件
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

            for file in files:
                if file.endswith(".pyc"):
                    continue

                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, SKILL_DIR)
                zf.write(file_path, arc_name)

    print(f"技能已打包: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")
    return output_path


if __name__ == "__main__":
    package_skill()