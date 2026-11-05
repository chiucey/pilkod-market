#!/usr/bin/env python3
"""
打包 stock-briefing 技能为 .skill 文件
"""

import os
import zipfile
import shutil
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SKILL_DIR)
OUTPUT_DIR = os.path.join(PARENT_DIR, 'dist')

def clean_build_artifacts(skill_path):
    """清理构建产物和缓存"""
    dirs_to_clean = ['__pycache__', '.git', 'temp', 'dist']
    for root, dirs, files in os.walk(skill_path):
        # 删除缓存目录
        for d in dirs:
            if d in dirs_to_clean:
                full_path = os.path.join(root, d)
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path, ignore_errors=True)
                    print(f"  已删除: {full_path}")
        # 删除 .pyc 文件
        for f in files:
            if f.endswith('.pyc') or f.endswith('.pyo'):
                full_path = os.path.join(root, f)
                os.remove(full_path)
                print(f"  已删除: {full_path}")

def package_skill(skill_path, output_path):
    """打包技能为 .skill 文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过缓存目录
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'temp', 'dist']]
            for file in files:
                # 跳过缓存文件
                if file.endswith('.pyc') or file.endswith('.pyo'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)
                print(f"  打包: {arcname}")
    
    return output_path

def main():
    skill_name = 'stock-briefing-L'
    skill_path = PARENT_DIR  # 直接使用父目录，即技能根目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(OUTPUT_DIR, f'{skill_name}_v2.0.0_{timestamp}.skill')
    
    print(f"\n{'='*60}")
    print(f"打包技能: {skill_name}")
    print(f"{'='*60}\n")
    
    # 清理
    print("【1/3】清理缓存文件...")
    clean_build_artifacts(skill_path)
    
    # 打包
    print("\n【2/3】打包技能...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    result = package_skill(skill_path, output_path)
    
    # 完成
    print(f"\n【3/3】打包完成!")
    print(f"\n✅ 技能文件已生成: {result}")
    print(f"📦 文件大小: {os.path.getsize(result) / 1024:.1f} KB")
    
    return result

if __name__ == '__main__':
    main()
