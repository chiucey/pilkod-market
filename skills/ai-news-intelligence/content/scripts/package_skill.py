#!/usr/bin/env python3
"""
AI 新闻情报系统技能 - 打包脚本
将技能打包为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def scan_files(directory: Path, exclude_patterns: set = None) -> list:
    """扫描目录中的所有文件，排除指定模式"""
    if exclude_patterns is None:
        exclude_patterns = {
            "__pycache__",
            "*.pyc",
            ".git",
            ".DS_Store",
            "*.log",
            ".venv",
            "node_modules",
        }

    files = []
    for item in directory.rglob("*"):
        if item.is_file():
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith("*"):
                    if item.name.endswith(pattern[1:]):
                        should_exclude = True
                        break
                elif pattern in str(item):
                    should_exclude = True
                    break

            if not should_exclude:
                # 计算相对路径
                rel_path = item.relative_to(directory)
                files.append((item, rel_path))

    return files


def validate_before_pack(skill_path: Path) -> tuple[bool, list[str]]:
    """打包前验证"""
    errors = []

    # 检查 SKILL.md
    if not (skill_path / "SKILL.md").exists():
        errors.append("缺少 SKILL.md")

    # 检查 _meta.json
    if not (skill_path / "_meta.json").exists():
        errors.append("缺少 _meta.json")
    else:
        try:
            meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
            if "id" not in meta or "version" not in meta:
                errors.append("_meta.json 必须包含 id 和 version")
        except:
            errors.append("_meta.json 格式错误")

    return len(errors) == 0, errors


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """打包技能为 .skill 文件"""

    # 验证
    valid, errors = validate_before_pack(skill_path)
    if not valid:
        print("❌ 打包前验证失败:")
        for error in errors:
            print(f"   • {error}")
        raise ValueError("打包前验证失败")

    # 创建输出目录
    if output_dir is None:
        output_dir = Path("/workspace/temp-skills")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取元数据
    meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
    skill_name = skill_path.name
    version = meta.get("version", "1.0.0")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建 ZIP 包
    files = scan_files(skill_path)

    print(f"📦 打包技能: {skill_name}")
    print(f"   版本: {version}")
    print(f"   文件数: {len(files)}")

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, rel_path in files:
            zf.write(file_path, rel_path)
            print(f"   + {rel_path}")

    print(f"\n✅ 打包完成: {output_file}")
    return output_file


def main():
    """主函数"""
    # 获取技能路径
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    try:
        output_file = package_skill(skill_path)
        print(f"\n📦 技能包路径: {output_file}")
        return 0
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
