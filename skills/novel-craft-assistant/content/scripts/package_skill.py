#!/usr/bin/env python3
"""
技能打包脚本 - 将技能目录打包为.skill文件
"""
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> dict:
    """打包技能目录"""
    skill_path = Path(skill_path)

    if not skill_path.exists() or not skill_path.is_dir():
        return {"success": False, "error": f"路径不存在或不是目录: {skill_path}"}

    # 读取meta
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return {"success": False, "error": "缺少_meta.json文件"}

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"meta.json解析失败: {e}"}

    skill_name = meta.get("name", skill_path.name)
    skill_version = meta.get("version", "1.0.0")
    skill_id = meta.get("id", "unknown")

    # 确定输出目录
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"{skill_name}_v{skill_version}_{timestamp}.skill"

    # 收集要打包的文件
    files_to_package = []
    for root, dirs, files in os.walk(skill_path):
        # 排除隐藏目录和__pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.startswith('.') or file.endswith('.pyc'):
                continue

            full_path = Path(root) / file
            rel_path = full_path.relative_to(skill_path)
            files_to_package.append({
                "path": full_path,
                "rel_path": rel_path
            })

    # 创建打包结构
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 复制文件
        for file_info in files_to_package:
            dest = tmp_path / file_info["rel_path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_info["path"], dest)

        # 生成MANIFEST.json
        manifest = {
            "name": skill_name,
            "id": skill_id,
            "version": skill_version,
            "packaged_at": datetime.now().isoformat(),
            "files": [str(f["rel_path"]) for f in files_to_package]
        }
        (tmp_path / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # 创建zip文件
        shutil.make_archive(
            str(output_file.with_suffix('')),
            'zip',
            tmp_path
        )

    # 重命名为.skill
    zip_file = output_file.with_suffix('.zip')
    if zip_file.exists():
        skill_file = output_file.with_suffix('.skill')
        shutil.move(str(zip_file), str(skill_file))
        return {
            "success": True,
            "output_file": str(skill_file),
            "files_count": len(files_to_package)
        }
    else:
        return {"success": False, "error": "打包失败"}

def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"正在打包技能: {skill_path}")

    result = package_skill(skill_path, output_dir)

    if result["success"]:
        print(f"\n✓ 打包成功!")
        print(f"  输出文件: {result['output_file']}")
        print(f"  包含文件: {result['files_count']} 个")
    else:
        print(f"\n✗ 打包失败: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
