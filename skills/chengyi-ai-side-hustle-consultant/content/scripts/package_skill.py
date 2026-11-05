#!/usr/bin/env python3
"""
打包脚本 - 将技能打包成.skill文件
"""
import os
import json
import shutil
import zipfile
import sys
from datetime import datetime

def get_skill_meta(skill_path):
    """读取技能元数据"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return None

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def package_skill(skill_path, output_dir=None):
    """打包技能"""
    skill_name = os.path.basename(skill_path)

    # 读取元数据
    meta = get_skill_meta(skill_path)
    if not meta:
        print("✗ 错误: 无法读取技能元数据")
        return False

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 确定输出路径
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(skill_path), 'dist')

    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_v{version}_{timestamp}.skill")

    # 创建zip文件
    print(f"\n{'='*60}")
    print(f"开始打包技能: {skill_name}")
    print(f"版本: {version}")
    print(f"输出: {output_file}")
    print('='*60 + '\n')

    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(skill_path):
                # 跳过dist目录
                if 'dist' in dirs:
                    dirs.remove('dist')

                for file in files:
                    file_path = os.path.join(root, file)

                    # 计算相对路径
                    rel_path = os.path.relpath(file_path, skill_path)

                    # 跳过临时文件和隐藏文件
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue

                    # 添加到zip
                    zipf.write(file_path, arcname=rel_path)
                    print(f"  + {rel_path}")

        # 生成manifest
        manifest = {
            "skill_id": skill_id,
            "name": skill_name,
            "version": version,
            "description": meta.get('description', ''),
            "author": meta.get('author', ''),
            "tags": meta.get('tags', []),
            "created_at": meta.get('created_at', ''),
            "packaged_at": datetime.now().isoformat(),
            "files": []
        }

        # 列出所有打包的文件
        with zipfile.ZipFile(output_file, 'r') as zipf:
            for info in zipf.infolist():
                manifest['files'].append({
                    "path": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size
                })

        # 保存manifest
        manifest_path = output_file.replace('.skill', '_manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print("✓ 打包完成！")
        print(f"  技能文件: {output_file}")
        print(f"  清单文件: {manifest_path}")
        print('='*60 + '\n')

        return True, output_file

    except Exception as e:
        print(f"\n✗ 打包失败: {str(e)}")
        return False, None

def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    success, output_file = package_skill(skill_path, output_dir)

    if success:
        print(f"\n打包成功！")
        print(f"输出文件: {output_file}")
    else:
        print(f"\n打包失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
