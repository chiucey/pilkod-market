#!/usr/bin/env python3
"""
打包脚本 - 将技能打包为 .skill 文件
用法: python package_skill.py <skill_dir>
"""
import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def package_skill(skill_dir):
    """打包技能目录为 .skill 文件"""
    skill_dir = Path(skill_dir).resolve()

    if not skill_dir.exists():
        print(f"{RED}✗ 技能目录不存在: {skill_dir}{RESET}")
        return False

    if not skill_dir.is_dir():
        print(f"{RED}✗ 路径不是目录: {skill_dir}{RESET}")
        return False

    # 读取 meta 信息
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        skill_id = meta.get('id', skill_dir.name)
        version = meta.get('version', '1.0.0')
    else:
        skill_id = skill_dir.name
        version = '1.0.0'

    # 创建输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = skill_dir.parent / f"{skill_id}_v{version}.skill"

    # 安全检查 - 避免覆盖
    if output_file.exists():
        print(f"{YELLOW}⚠ 输出文件已存在: {output_file}{RESET}")
        output_file = skill_dir.parent / f"{skill_id}_v{version}_{timestamp}.skill"

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}技能打包工具{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"技能目录: {skill_dir}")
    print(f"技能ID:   {skill_id}")
    print(f"版本:     {version}")
    print(f"输出文件: {output_file}")

    # 收集要打包的文件
    files_to_package = []

    # 必须包含的文件
    required_files = ['SKILL.md', '_meta.json']
    for req in required_files:
        req_path = skill_dir / req
        if req_path.exists():
            files_to_package.append(req_path)
        else:
            print(f"{RED}✗ 缺少必需文件: {req}{RESET}")
            return False

    # 可选的 references 目录
    references_dir = skill_dir / "references"
    if references_dir.exists():
        for md_file in references_dir.glob("*.md"):
            files_to_package.append(md_file)

    # 可选的 scripts 目录
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for py_file in scripts_dir.glob("*.py"):
            files_to_package.append(py_file)

    # 可选的 assets 目录
    assets_dir = skill_dir / "assets"
    if assets_dir.exists():
        for asset_file in assets_dir.rglob("*"):
            if asset_file.is_file():
                files_to_package.append(asset_file)

    print(f"\n将打包以下文件:")
    print("-" * 60)
    for f in files_to_package:
        rel_path = f.relative_to(skill_dir)
        print(f"  + {rel_path}")
    print("-" * 60)

    # 创建 zip 文件
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_package:
                arcname = str(file_path.relative_to(skill_dir))
                zf.write(file_path, arcname)
                print(f"  {GREEN}✓{RESET} {arcname}")

        file_size = output_file.stat().st_size
        print(f"\n{GREEN}✓ 打包完成！{RESET}")
        print(f"输出文件: {output_file}")
        print(f"文件大小: {file_size / 1024:.2f} KB")

        # 输出 JSON manifest
        manifest = {
            "id": skill_id,
            "version": version,
            "files": [str(f.relative_to(skill_dir)) for f in files_to_package],
            "packaged_at": datetime.now().isoformat(),
            "output_file": str(output_file)
        }
        manifest_file = skill_dir / f"{skill_id}_manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"清单文件: {manifest_file}")

        return True

    except Exception as e:
        print(f"{RED}✗ 打包失败: {e}{RESET}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir>")
        print(f"当前目录: {Path(__file__).parent.parent}")
        sys.exit(1)

    skill_dir = sys.argv[1]
    success = package_skill(skill_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
