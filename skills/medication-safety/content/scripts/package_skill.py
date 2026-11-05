#!/usr/bin/env python3
"""
技能打包脚本
将medication-safety技能打包为可分发的格式
"""

import os
import json
import shutil
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent / 'dist'

def validate_skill():
    """验证技能结构"""
    print("正在验证技能结构...")

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = SKILL_DIR / file
        if not file_path.exists():
            raise FileNotFoundError(f"缺少必要文件: {file}")

    # 验证meta.json
    with open(SKILL_DIR / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            raise ValueError("_meta.json缺少id或version字段")

    # 验证SKILL.md frontmatter
    with open(SKILL_DIR / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            raise ValueError("SKILL.md必须以frontmatter开头")
        if 'name:' not in content or 'description:' not in content:
            raise ValueError("SKILL.md frontmatter缺少name或description字段")

    print("✓ 技能结构验证通过")
    return True

def package_skill():
    """打包技能"""
    print("正在打包技能...")

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 打包文件列表
    files_to_package = [
        'SKILL.md',
        '_meta.json',
        'references/drug_interactions.json',
        'scripts/check_interactions.py'
    ]

    for file in files_to_package:
        src = SKILL_DIR / file
        dst = OUTPUT_DIR / file
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✓ 已复制: {file}")

    # 创建打包信息
    package_info = {
        'name': 'medication-safety',
        'description': '用药安全检查技能 - 检查药物相互作用、禁忌食物和禁忌行为',
        'version': '1.0.0',
        'files': files_to_package,
        'created': '2024-03-21'
    }

    with open(OUTPUT_DIR / 'package_info.json', 'w', encoding='utf-8') as f:
        json.dump(package_info, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 打包完成！输出目录: {OUTPUT_DIR}")
    return OUTPUT_DIR

def main():
    """主函数"""
    print("=" * 50)
    print("    用药安全技能 - 打包工具")
    print("=" * 50)
    print()

    try:
        validate_skill()
        output_dir = package_skill()

        print("\n" + "=" * 50)
        print("打包成功！技能已准备就绪。")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
