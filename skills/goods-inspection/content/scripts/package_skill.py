# -*- coding: utf-8 -*-
"""
验货比对技能打包脚本
将技能打包为可发布的格式
"""

import os
import zipfile
import json
import shutil
from datetime import datetime

def package_skill(skill_dir, output_dir=None):
    """打包技能到.skill文件"""
    
    skill_name = os.path.basename(skill_dir)
    
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)
    
    # 创建打包输出目录
    package_dir = os.path.join(output_dir, 'packages')
    os.makedirs(package_dir, exist_ok=True)
    
    # 生成包文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}_{timestamp}.skill"
    package_path = os.path.join(package_dir, package_name)
    
    print(f"打包技能: {skill_name}")
    print(f"输出路径: {package_path}")
    
    # 读取meta信息
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    print(f"  技能ID: {meta['id']}")
    print(f"  版本: {meta['version']}")
    
    # 创建ZIP包
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算相对路径
                arcname = os.path.relpath(file_path, os.path.dirname(skill_dir))
                zipf.write(file_path, arcname)
                print(f"  添加: {arcname}")
    
    print(f"\n✅ 打包完成: {package_path}")
    
    # 生成发布说明
    readme_path = os.path.join(package_dir, f"{skill_name}_README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""# {skill_name} 技能发布包

## 基本信息
- **技能名称**: {skill_name}
- **技能ID**: {meta['id']}
- **版本**: {meta['version']}
- **打包时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 技能描述
验货比对分析技能。将原文件（PDF设计稿、制令单、规格书等）与实物照片进行详细比对，生成专业的验货报告。

## 包含文件
""")
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, skill_dir)
                f.write(f"- {rel_path}\n")
        
        f.write(f"""
## 安装说明
1. 下载 {package_name} 文件
2. 导入到 Matrix Agent 技能库
3. 开始使用验货比对功能

## 触发短语
- "验货"
- "比对原文件和照片"
- "检查产品质量"
- "实物对比"
- "设计稿核对"
- "inspection"
- "quality check"

---
*此文件由 Matrix Agent 自动生成*
""")
    
    print(f"📄 发布说明: {readme_path}")
    
    return package_path, readme_path

if __name__ == "__main__":
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    package_path, readme_path = package_skill(skill_dir)
    print(f"\n打包文件: {package_path}")
