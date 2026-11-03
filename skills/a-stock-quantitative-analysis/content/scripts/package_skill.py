#!/usr/bin/env python3
"""
A股短线量化分析技能 - 打包脚本
生成 .skill 归档文件用于发布
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_safe_files(skill_path: Path) -> list:
    """获取需要打包的安全文件列表"""
    safe_extensions = {'.md', '.json', '.py', '.txt', '.yml', '.yaml', '.csv'}
    exclude_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
    exclude_files = {'.DS_Store', 'Thumbs.db', '.gitignore'}

    safe_files = []

    for item in skill_path.rglob('*'):
        if item.is_file():
            # 检查是否在排除目录中
            if any(excluded in item.parts for excluded in exclude_dirs):
                continue

            # 检查文件名
            if item.name in exclude_files:
                continue

            # 检查扩展名或是否为特殊文件
            if item.suffix in safe_extensions or item.name in ['_meta.json', 'SKILL.md']:
                safe_files.append(item)

    return safe_files


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能路径不存在: {skill_path}")

    if not (skill_path / "SKILL.md").exists():
        raise FileNotFoundError("SKILL.md 文件不存在")

    if not (skill_path / "_meta.json").exists():
        raise FileNotFoundError("_meta.json 文件不存在")

    # 读取元数据
    with open(skill_path / "_meta.json", 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    skill_name = meta.get('name', skill_path.name)
    skill_version = meta.get('version', '1.0.0')
    output_file = Path(output_dir) / f"{skill_name}.skill"

    # 收集安全文件
    safe_files = get_safe_files(skill_path)

    if not safe_files:
        raise ValueError("没有找到要打包的文件")

    # 创建 zip 归档
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in safe_files:
            # 计算相对路径
            arcname = file_path.relative_to(skill_path)
            zf.write(file_path, arcname)

    # 生成打包报告
    report = {
        "skill_name": skill_name,
        "version": skill_version,
        "output_file": str(output_file),
        "files_count": len(safe_files),
        "files": [str(f.relative_to(skill_path)) for f in safe_files],
        "packed_at": datetime.now().isoformat()
    }

    return json.dumps(report, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
        print("使用默认路径:", skill_path)
    else:
        skill_path = Path(sys.argv[1])

    print(f"\n📦 打包技能: {skill_path}")
    print("=" * 50)

    try:
        report = package_skill(skill_path)
        report_data = json.loads(report)

        print(f"\n✅ 打包成功!")
        print(f"📁 输出文件: {report_data['output_file']}")
        print(f"📊 文件数量: {report_data['files_count']}")
        print(f"🕐 打包时间: {report_data['packed_at']}")

        print("\n📋 包含文件:")
        for f in report_data['files']:
            print(f"   - {f}")

        return 0
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
