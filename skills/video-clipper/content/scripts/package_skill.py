#!/usr/bin/env python3
"""
打包脚本 - 将技能打包为 .skill 文件
"""
import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


def get_file_hashes(zip_path: str) -> dict:
    """计算打包文件的哈希值"""
    hashes = {}
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for info in zf.infolist():
            if not info.is_dir():
                content = zf.read(info.filename)
                hashes[info.filename] = {
                    'sha256': hashlib.sha256(content).hexdigest()[:16],
                    'size': len(content)
                }
    return hashes


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为 .skill 文件"""
    skill_dir = Path(skill_path)
    output_path = Path(output_dir)

    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)

    # 读取 meta 信息
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        print("❌ 错误: _meta.json 不存在")
        sys.exit(1)

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')
    skill_name = skill_dir.name

    # 生成打包文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_path / f"{skill_name}_v{skill_version}_{timestamp}.skill"

    # 创建 zip 文件
    print(f"\n📦 正在打包技能: {skill_name}")
    print("-" * 50)

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除隐藏目录和 __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_dir)
                zf.write(file_path, arc_name)
                print(f"  + {arc_name}")

    # 计算哈希
    hashes = get_file_hashes(str(output_file))

    # 生成 manifest
    manifest = {
        "skill_id": skill_id,
        "skill_name": skill_name,
        "version": skill_version,
        "packaged_at": datetime.now().isoformat(),
        "files": hashes,
        "total_files": len(hashes),
        "package_size": output_file.stat().st_size
    }

    manifest_path = output_path / f"{skill_name}_v{skill_version}_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    print(f"✅ 打包完成！")
    print(f"\n📦 技能包: {output_file}")
    print(f"📋 清单文件: {manifest_path}")
    print(f"📊 文件数量: {len(hashes)}")
    print(f"💾 包大小: {output_file.stat().st_size / 1024:.2f} KB")

    return str(output_file)


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print("=" * 50)
    print("🎁 技能打包工具")
    print("=" * 50)

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n✨ 技能已成功打包!")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
