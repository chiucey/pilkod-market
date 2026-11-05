"""
技能打包脚本
将技能打包成 .skill 文件用于分发
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = "dist") -> str:
    """
    打包技能到 .skill 文件

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录

    Returns:
        打包后的文件路径
    """
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # 读取元数据
    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_path.name}_v{version}_{timestamp}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 添加所有文件
        for root, dirs, files in os.walk(skill_path):
            # 跳过 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('__') and d not in ['dist', 'data', '__pycache__']]

            for file in files:
                # 跳过临时文件和隐藏文件
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"✓ 技能已打包: {output_file}")
    print(f"  - 技能ID: {skill_id}")
    print(f"  - 版本: {version}")
    print(f"  - 文件大小: {output_file.stat().st_size / 1024:.1f} KB")

    return str(output_file)


def list_skill_contents(skill_path: str) -> list:
    """列出技能包内容"""
    skill_path = Path(skill_path)
    contents = []

    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if not d.startswith('__') and d not in ['dist', 'data', '__pycache__']]

        for file in files:
            if file.startswith('.'):
                continue
            file_path = Path(root) / file
            rel_path = file_path.relative_to(skill_path)
            size = file_path.stat().st_size
            contents.append({
                'path': str(rel_path),
                'size': size,
                'type': 'dir' if file_path.is_dir() else 'file'
            })

    return contents


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='打包A股板块情绪分析技能')
    parser.add_argument('--path', default='/workspace/temp-skills/a-stock-sector-emotion',
                        help='技能目录路径')
    parser.add_argument('--output', default='/workspace/temp-skills/dist',
                        help='输出目录')

    args = parser.parse_args()

    print("=" * 50)
    print("技能打包工具")
    print("=" * 50)

    # 列出内容
    print(f"\n技能内容:")
    contents = list_skill_contents(args.path)
    for item in sorted(contents, key=lambda x: x['path']):
        size_str = f"{item['size']/1024:.1f} KB" if item['size'] > 0 else "-"
        print(f"  {item['path']} ({size_str})")

    # 打包
    print(f"\n正在打包...")
    output_file = package_skill(args.path, args.output)
    print(f"\n打包完成: {output_file}")

    return output_file


if __name__ == "__main__":
    main()
