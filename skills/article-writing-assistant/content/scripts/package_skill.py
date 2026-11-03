#!/usr/bin/env python3
"""
文章写作助手技能打包脚本
将技能打包为 .skill 文件用于发布
"""

import os
import json
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def scan_for_secrets(skill_path):
    """扫描可能包含敏感信息的文件"""
    secret_patterns = ['password', 'secret', 'token', 'api_key', 'credential']
    suspicious_files = []

    for root, dirs, files in os.walk(skill_path):
        # 跳过隐藏目录和常见构建目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]

        for file in files:
            if file.startswith('.'):
                continue

            file_path = os.path.join(root, file)

            # 检查文件名是否包含敏感词
            for pattern in secret_patterns:
                if pattern in file.lower():
                    suspicious_files.append(file_path)

            # 检查文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for pattern in secret_patterns:
                        if pattern in content and len(content) < 10000:  # 小文件才检查
                            suspicious_files.append(file_path)
                            break
            except:
                pass

    return suspicious_files

def validate_for_packaging(skill_path):
    """打包前的验证"""
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    # 验证 _meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查敏感文件
    suspicious = scan_for_secrets(skill_path)
    if suspicious:
        print("\n⚠️  警告：发现可能包含敏感信息的文件:")
        for f in suspicious:
            print(f"  - {f}")
        print("建议在打包前移除或确认这些文件不包含敏感信息。")

    return errors

def create_package(skill_path, output_dir=None):
    """创建技能包"""
    skill_name = os.path.basename(skill_path)

    # 验证
    errors = validate_for_packaging(skill_path)
    if errors:
        print("\n❌ 打包验证失败:")
        for error in errors:
            print(f"  - {error}")
        return None

    # 读取元数据
    meta_path = os.path.join(skill_path, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_name = f"{skill_name}_{meta['version']}_{timestamp}.skill"

    if output_dir:
        output_path = os.path.join(output_dir, output_name)
    else:
        output_path = os.path.join(os.path.dirname(skill_path), output_name)

    # 创建 ZIP 包
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(skill_path):
                # 跳过隐藏目录和构建目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_path)
                    zipf.write(file_path, arcname)

        print(f"\n✅ 技能包创建成功！")
        print(f"📦 包文件: {output_path}")
        print(f"📊 技能名称: {skill_name}")
        print(f"📊 版本: {meta['version']}")
        print(f"📊 技能ID: {meta['id']}")

        # 显示包内容
        print("\n📁 包内容:")
        with zipfile.ZipFile(output_path, 'r') as zipf:
            for info in zipf.infolist():
                size = info.file_size
                print(f"  - {info.filename} ({size} bytes)")

        return output_path

    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return None

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py /workspace/temp-skills/article-writing-assistant")
        print("示例: python package_skill.py /workspace/temp-skills/article-writing-assistant ./output")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"打包技能: {skill_path}")
    print("=" * 50)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    result = create_package(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
