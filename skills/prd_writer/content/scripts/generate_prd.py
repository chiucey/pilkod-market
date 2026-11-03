#!/usr/bin/env python3
"""
PRD文档生成脚本

使用方法:
    python generate_prd.py --name "工位信息管理" --output "E:/copawws"

参数说明:
    --name: 产品/模块名称
    --output: 输出目录路径
    --template: 使用的模板文件路径（可选）
"""

import argparse
import os
import shutil
from datetime import datetime

# 默认模板路径
DEFAULT_TEMPLATE = "E:/copawws/PRD模版_ToB智能调度产品专用.md"
DEFAULT_OUTPUT = "E:/copawws"


def parse_args():
    parser = argparse.ArgumentParser(description='PRD文档生成工具')
    parser.add_argument('--name', '-n', type=str, required=True,
                        help='产品/模块名称')
    parser.add_argument('--output', '-o', type=str, default=DEFAULT_OUTPUT,
                        help=f'输出目录路径 (默认: {DEFAULT_OUTPUT})')
    parser.add_argument('--template', '-t', type=str, default=DEFAULT_TEMPLATE,
                        help=f'模板文件路径 (默认: {DEFAULT_TEMPLATE})')
    return parser.parse_args()


def generate_prd(name: str, output_dir: str, template_path: str):
    """生成PRD文档"""
    
    # 检查模板文件
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return None
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    safe_name = name.replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = os.path.join(output_dir, f"{safe_name}PRD.md")
    
    # 检查是否已存在
    if os.path.exists(output_file):
        response = input(f"⚠️ 文件已存在: {output_file}\n是否覆盖? (y/n): ")
        if response.lower() != 'y':
            print("❌ 已取消")
            return None
    
    # 复制模板作为基础
    shutil.copy(template_path, output_file)
    
    print(f"✅ PRD文档已生成: {output_file}")
    print(f"\n📝 下一步:")
    print(f"   1. 打开文件: {output_file}")
    print(f"   2. 根据需求修改模板内容")
    print(f"   3. 使用Mermaid预览工具验证图表: https://mermaid.live")
    
    return output_file


if __name__ == '__main__':
    args = parse_args()
    generate_prd(args.name, args.output, args.template)
