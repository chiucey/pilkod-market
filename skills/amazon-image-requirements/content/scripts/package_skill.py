#!/usr/bin/env python3
"""
技能打包脚本 - amazon-image-requirements
生成可发布的 .skill 文件
"""

import os
import json
import shutil
from pathlib import Path
import zipfile
import datetime

def get_skill_root():
    """返回技能根目录 (scripts 的父目录)"""
    script_dir = Path(__file__).parent.resolve()
    return script_dir.parent

def validate_skill():
    """验证技能结构和元数据"""
    root = get_skill_root()
    errors = []
    warnings = []
    
    # 检查必需文件
    if not (root / "SKILL.md").exists():
        errors.append("SKILL.md 不存在")
    
    if not (root / "_meta.json").exists():
        errors.append("_meta.json 不存在")
    else:
        try:
            with open(root / "_meta.json") as f:
                meta = json.load(f)
            if "id" not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if "version" not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")
    
    # 检查 frontmatter
    with open(root / "SKILL.md") as f:
        content = f.read()
    
    if not content.startswith("---"):
        errors.append("SKILL.md 必须以 frontmatter --- 开头")
    
    if "name:" not in content[:500]:
        errors.append("SKILL.md frontmatter 缺少 'name' 字段")
    
    if "description:" not in content[:1000]:
        errors.append("SKILL.md frontmatter 缺少 'description' 字段")
    
    return errors, warnings

def should_exclude(relative_path, exclude_dirs):
    """检查路径是否应该被排除"""
    parts = Path(relative_path).parts
    for part in parts:
        if part in exclude_dirs:
            return True
    return False

def package_skill():
    """打包技能为 .skill 文件"""
    root = get_skill_root()
    
    # 创建临时输出目录
    temp_output = root / "dist_temp"
    if temp_output.exists():
        shutil.rmtree(temp_output)
    temp_output.mkdir(exist_ok=True)
    
    # 读取元数据
    with open(root / "_meta.json") as f:
        meta = json.load(f)
    
    version = meta["version"]
    
    # 生成文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = temp_output / f"amazon-image-requirements_v{version}_{timestamp}.skill"
    
    # 要排除的目录
    exclude_dirs = {"__pycache__", ".git", ".minimax", "dist", ".DS_Store"}
    
    # 创建 ZIP 文件
    files_added = []
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.glob("**/*"):
            if not file_path.is_file():
                continue
            
            # 计算相对路径
            rel_path = file_path.relative_to(root)
            
            # 检查是否应该排除
            if should_exclude(rel_path, exclude_dirs):
                continue
            
            # 添加到 ZIP
            zf.write(str(file_path), str(rel_path))
            files_added.append(str(rel_path))
    
    # 移动到最终位置
    final_output = root / "dist" / output_file.name
    final_output.parent.mkdir(exist_ok=True)
    shutil.move(str(output_file), str(final_output))
    
    # 清理临时目录
    shutil.rmtree(temp_output)
    
    print(f"\n已添加 {len(files_added)} 个文件:")
    for f in sorted(files_added):
        print(f"  + {f}")
    
    print(f"\n技能打包完成: {final_output}")
    print(f"文件大小: {final_output.stat().st_size / 1024:.2f} KB")
    return str(final_output)

if __name__ == "__main__":
    print("=" * 50)
    print("amazon-image-requirements 技能打包工具")
    print("=" * 50)
    
    # 验证
    print("\n[1/2] 验证技能结构...")
    errors, warnings = validate_skill()
    
    if errors:
        print("\n错误:")
        for e in errors:
            print(f"  - {e}")
        exit(1)
    
    if warnings:
        print("\n警告:")
        for w in warnings:
            print(f"  - {w}")
    
    print("验证通过!")
    
    # 打包
    print("\n[2/2] 打包技能...")
    output_file = package_skill()
    
    print("\n" + "=" * 50)
    print(f"打包成功: {output_file}")
    print("=" * 50)