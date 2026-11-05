#!/usr/bin/env python3
"""
酒店平面布置图技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import zipfile
import json
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(filepath: Path) -> str:
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def package_skill(skill_path: str, output_dir: str = "/workspace/temp-skills") -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_path.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 读取元数据
    meta_path = skill_path / "_meta.json"
    meta = {"id": "", "version": "1.0.0"}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))

    # 创建打包清单
    manifest = {
        "name": skill_name,
        "id": meta.get("id", ""),
        "version": meta.get("version", "1.0.0"),
        "packaged_at": timestamp,
        "files": []
    }

    # 打包文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(skill_path)

                # 添加到清单
                file_info = {
                    "path": str(rel_path),
                    "hash": get_file_hash(file_path),
                    "size": file_path.stat().st_size
                }
                manifest["files"].append(file_info)

                # 写入压缩包
                zipf.write(file_path, rel_path)

    # 保存清单
    manifest_path = output_dir / f"{skill_name}_{timestamp}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n" + "="*60)
    print("📦 技能打包报告")
    print("="*60)
    print(f"   技能名称: {skill_name}")
    print(f"   技能 ID: {meta.get('id', 'N/A')}")
    print(f"   版本: {meta.get('version', '1.0.0')}")
    print(f"   打包时间: {timestamp}")
    print(f"   文件数量: {len(manifest['files'])}")
    print(f"   输出文件: {output_file}")
    print("="*60)

    return str(output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/hotel-floor-plan-prompt"
    else:
        skill_path = sys.argv[1]

    output_file = package_skill(skill_path)
    print(f"\n✅ 打包完成！文件路径: {output_file}")