#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司基本信息Excel处理器
处理"公司基本信息查询.xlsx"文件，按照固定规则提取和筛选数据

处理规则：
1. 筛选O列（一级类别），仅保留"协鑫能科"的行
2. 仅保留D至I列（6列）和Z至AA列（2列），共8列
3. 输出新的Excel文件
"""

import pandas as pd
import sys
import os
from pathlib import Path


def process_company_info_excel(input_file_path):
    """
    处理公司基本信息Excel文件

    Args:
        input_file_path: 输入Excel文件路径

    Returns:
        str: 输出文件路径
    """
    # 读取Excel文件
    print(f"正在读取文件: {input_file_path}")
    df = pd.read_excel(input_file_path)

    print(f"原始数据: {len(df)} 行 × {len(df.columns)} 列")

    # 获取列名列表
    columns = list(df.columns)

    # 定义要保留的列
    # D至I列：索引3-8 (共6列)
    # Z至AA列：索引25-26 (共2列)
    d_to_i_cols = columns[3:9]
    z_to_aa_cols = columns[25:27]

    print("\n保留的列:")
    print("D至I列 (6列):")
    for i, col in enumerate(d_to_i_cols, 4):
        print(f"  列{i}: {col}")

    print("Z至AA列 (2列):")
    for i, col in enumerate(z_to_aa_cols, 26):
        print(f"  列{i}: {col}")

    # O列（索引14）是一级类别
    o_column_name = columns[14]
    print(f"\n筛选列: {o_column_name}")
    print(f"筛选值: 协鑫能科")

    # 筛选O列内容为"协鑫能科"的行
    filtered_df = df[df[o_column_name] == '协鑫能科'].copy()
    print(f"筛选后: {len(filtered_df)} 行")

    # 合并要保留的列
    selected_columns = d_to_i_cols + z_to_aa_cols
    result_df = filtered_df[selected_columns].copy()

    # 重置索引
    result_df.reset_index(drop=True, inplace=True)

    print(f"\n最终输出: {len(result_df)} 行 × {len(result_df.columns)} 列")

    # 确保输出目录存在
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    # 生成输出文件名
    input_name = Path(input_file_path).stem
    output_file = output_dir / f"协鑫能科_{input_name}_处理结果.xlsx"

    # 保存为新的Excel文件
    result_df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n✓ 文件已生成: {output_file}")

    return str(output_file)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python process_company_info.py <输入文件路径>")
        print("示例: python process_company_info.py 公司基本信息查询.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        sys.exit(1)

    try:
        output_file = process_company_info_excel(input_file)
        print("\n处理完成!")
        print(f"输出文件: {output_file}")
    except Exception as e:
        print(f"错误: 处理失败 - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
