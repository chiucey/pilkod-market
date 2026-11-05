#!/usr/bin/env python3
"""
打包脚本 - 将技能目录打包为 .skill 文件
"""
import os
import sys
import zipfile
from pathlib import Path
import json
import shutil

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """将技能目录打包为 .skill 文件"""
    skill_dir = Path(skill_path)
    output_path = Path(output_dir)

    if not skill_dir.exists() or not skill_dir.is_dir():
        raise ValueError(f"技能目录不存在: {skill_path}")

    # 获取技能名称
    skill_name = skill_dir.name

    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    output_file = output_path / f"{skill_name}.skill"

    # 收集要打包的文件（排除临时文件和构建产物）
    exclude_patterns = {
        '__pycache__', '.git', '.DS_Store', 'Thumbs.db',
        '*.pyc', '*.pyo', '*.log', 'node_modules',
        '.venv', 'venv', 'outputs',  # 排除输出目录
    }

    def should_include(path: Path) -> bool:
        name = path.name
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return False
            elif name == pattern:
                return False
        return True

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if should_include(Path(d))]

            for file in files:
                file_path = Path(root) / file
                if should_include(file_path):
                    # 计算相对路径
                    arcname = file_path.relative_to(skill_dir)
                    zf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    return str(output_file)


def validate_before_pack(skill_path: str) -> bool:
    """打包前验证"""
    skill_dir = Path(skill_path)

    # 检查必需文件
    required = ["SKILL.md", "_meta.json"]
    missing = [f for f in required if not (skill_dir / f).exists()]
    if missing:
        print(f"❌ 缺少必需文件: {missing}")
        return False

    # 检查 _meta.json 格式
    try:
        meta = json.loads((skill_dir / "_meta.json").read_text(encoding="utf-8"))
        if "id" not in meta or "version" not in meta:
            print("❌ _meta.json 必须包含 'id' 和 'version' 字段")
            return False
    except Exception as e:
        print(f"❌ _meta.json 读取失败: {e}")
        return False

    return True


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"正在打包技能: {skill_path}")

    if validate_before_pack(skill_path):
        output_file = package_skill(skill_path, output_dir)
        print(f"\n打包完成: {output_file}")
    else:
        print("\n打包失败，请先修复验证问题")
        sys.exit(1)
