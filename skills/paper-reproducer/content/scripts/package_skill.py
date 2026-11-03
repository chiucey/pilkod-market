"""
论文复现技能打包脚本

将技能打包为可分发的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_skill_info(skill_path: str) -> dict:
    """从_meta.json读取技能信息"""
    meta_path = Path(skill_path) / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def is_safe_path(path: str) -> bool:
    """检查路径安全性，防止符号链接逃逸"""
    abs_path = os.path.abspath(path)
    return not abs_path.startswith('/proc') and not abs_path.startswith('/sys')


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为.skill文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name
    
    # 获取技能信息
    skill_info = get_skill_info(str(skill_path))
    skill_id = skill_info.get('id', 'unknown')
    version = skill_info.get('version', '1.0.0')
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(output_dir) / f"{skill_name}_{version}_{timestamp}.skill"
    
    # 创建zip包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 过滤不安全目录
            dirs[:] = [d for d in dirs if is_safe_path(os.path.join(root, d))]
            
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                
                # 跳过潜在的敏感文件
                if file in ['.env', '.gitignore', '*.pyc', '__pycache__']:
                    continue
                
                zf.write(file_path, arcname)
    
    return str(output_file)


def main():
    """主打包流程"""
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"✓ Skill packaged successfully: {output_file}")
    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
