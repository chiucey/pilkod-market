#!/usr/bin/env python3
"""
Package Script — 技能打包工具
生成 .skill 文件用于发布
"""

import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime


def get_safe_files(root_path: Path) -> list[Path]:
    """获取需要打包的安全文件列表"""

    # 安全扫描：排除潜在危险文件
    exclude_patterns = [
        '__pycache__', '*.pyc', '.git', '.DS_Store',
        '*.pem', '*.key', '.env', 'secrets',
        'node_modules', '.venv'
    ]

    safe_files = []
    for f in root_path.rglob('*'):
        if f.is_file():
            # 检查是否在排除列表中
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(f):
                    should_exclude = True
                    break

            # 安全检查：不允许符号链接
            if f.is_symlink():
                print(f"⚠️ 跳过符号链接: {f}")
                continue

            # 检查路径安全性（防止 ../ 逃逸）
            try:
                resolved = f.resolve()
                if not str(resolved).startswith(str(root_path.resolve())):
                    print(f"⚠️ 跳过路径逃逸: {f}")
                    continue
            except Exception:
                continue

            if not should_exclude:
                safe_files.append(f)

    return safe_files


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能到 .skill 文件"""

    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取技能名称和版本
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        skill_name = meta.get("name", skill_path.name)
        version = meta.get("version", "1.0.0")
    else:
        skill_name = skill_path.name
        version = "1.0.0"

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}-{version}-{timestamp}.skill"

    # 获取安全文件列表
    safe_files = get_safe_files(skill_path)

    print(f"\n{'='*60}")
    print(f"打包技能: {skill_path.name}")
    print(f"{'='*60}\n")

    print(f"📦 包含文件 ({len(safe_files)} 个):")
    for f in sorted(safe_files):
        rel_path = f.relative_to(skill_path)
        print(f"  + {rel_path}")

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in safe_files:
            rel_path = f.relative_to(skill_path)
            zf.write(f, rel_path)

    print(f"\n✅ 打包完成: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size:,} bytes")

    return str(output_file)


def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py /workspace/temp-skills/my-skill")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n📤 技能产物: {output_file}")
        return 0
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
