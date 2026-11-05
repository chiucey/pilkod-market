#!/usr/bin/env python3
"""
对比展示生成脚本
在原XLSX文件基础上添加优化前后的对比展示
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, List
import os

def create_comparison_xlsx(
    original_data: Dict,
    optimized_data: Dict,
    output_path: str = None
) -> str:
    """
    创建对比展示XLSX文件

    Args:
        original_data: 原始数据字典
        optimized_data: 优化后数据字典
        output_path: 输出文件路径，默认在原文件名前加"优化后_"

    Returns:
        输出文件路径
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "优化对比"

    # 设置样式
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    original_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    optimized_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # 设置列宽
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 60
    ws.column_dimensions['C'].width = 60

    # 表头
    headers = ["字段", "优化前", "优化后"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # 字段数据
    fields = [
        ('平台', 'platform'),
        ('站点', 'site'),
        ('标题', 'title'),
        ('五点1', 'bullet_point_1'),
        ('五点2', 'bullet_point_2'),
        ('五点3', 'bullet_point_3'),
        ('五点4', 'bullet_point_4'),
        ('五点5', 'bullet_point_5'),
        ('关键词', 'keywords'),
    ]

    row = 2
    for field_name, field_key in fields:
        # 字段名
        cell_a = ws.cell(row=row, column=1, value=field_name)
        cell_a.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell_a.border = thin_border
        cell_a.font = Font(bold=True)

        # 原内容
        original_value = get_original_value(original_data, field_key)
        cell_b = ws.cell(row=row, column=2, value=original_value)
        cell_b.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
        cell_b.border = thin_border
        cell_b.fill = original_fill

        # 优化后内容
        optimized_value = get_optimized_value(optimized_data, field_key)
        cell_c = ws.cell(row=row, column=3, value=optimized_value)
        cell_c.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
        cell_c.border = thin_border
        cell_c.fill = optimized_fill

        row += 1

    # 设置行高
    for r in range(2, row):
        ws.row_dimensions[r].height = 45

    # 添加说明sheet
    ws_instructions = wb.create_sheet("优化说明")
    instructions = [
        ("优化标准说明", ""),
        ("", ""),
        ("1. 标题优化规则", ""),
        ("", "- 至少包含2个核心关键词"),
        ("", "- 将其中一个核心关键词前置后加逗号"),
        ("", "- 同样名词和词组不出现2次以上"),
        ("", "- 总字符控制在150左右"),
        ("", "- 如果原标题带括号内容，括号位置不变"),
        ("", ""),
        ("2. 五点优化规则", ""),
        ("", "- 语句通顺，符合美国人语言习惯"),
        ("", "- 避免重复介词和夸大产品性能"),
        ("", "- 不要有售后相关信息及价格描述"),
        ("", "- 需要埋入主关键词"),
        ("", "- 每一点要有小标题概括，小标题和内容之间用冒号隔开"),
        ("", "- 每一点写在同一行，方便复制粘贴"),
        ("", ""),
        ("3. 关键词优化规则", ""),
        ("", "- 重复单词需要去重"),
        ("", "- 去重后控制在200-220个字符数（仅计算字母）"),
        ("", "- 关键词用空格隔开，方便复制粘贴"),
        ("", ""),
        ("4. 通用规则", ""),
        ("", "- 剔除侵权词"),
        ("", "- 不要添加描述中不存在的认证信息"),
        ("", "- 如需换单位，数字需进行相应换算"),
    ]

    for i, (col1, col2) in enumerate(instructions, 1):
        ws_instructions.cell(row=i, column=1, value=col1)
        ws_instructions.cell(row=i, column=2, value=col2)

    ws_instructions.column_dimensions['A'].width = 25
    ws_instructions.column_dimensions['B'].width = 60

    # 保存文件
    if not output_path:
        output_path = os.path.join(
            os.path.dirname(original_data.get('_file_path', '.')),
            "优化后_" + os.path.basename(original_data.get('_file_path', 'output.xlsx'))
        )

    wb.save(output_path)
    return output_path


def get_original_value(data: Dict, field_key: str) -> str:
    """获取原始数据中指定字段的值"""
    if field_key == 'platform':
        return data.get('platform', '')
    elif field_key == 'site':
        return data.get('site', '')
    elif field_key == 'title':
        return data.get('title', '')
    elif field_key.startswith('bullet_point_'):
        idx = int(field_key.split('_')[-1]) - 1
        bullet_points = data.get('bullet_points', [])
        return bullet_points[idx] if idx < len(bullet_points) else ''
    elif field_key == 'keywords':
        return data.get('keywords', '')
    return ''


def get_optimized_value(data: Dict, field_key: str) -> str:
    """获取优化数据中指定字段的值"""
    if field_key == 'platform':
        return data.get('platform', data.get('original', {}).get('platform', ''))
    elif field_key == 'site':
        return data.get('site', data.get('original', {}).get('site', ''))
    elif field_key == 'title':
        return data.get('title', data.get('original', {}).get('title', ''))
    elif field_key.startswith('bullet_point_'):
        idx = int(field_key.split('_')[-1]) - 1
        bullet_points = data.get('bullet_points', data.get('original', {}).get('bullet_points', []))
        return bullet_points[idx] if idx < len(bullet_points) else ''
    elif field_key == 'keywords':
        return data.get('keywords', data.get('original', {}).get('keywords', ''))
    return ''


def main():
    """测试用主函数"""
    # 示例数据
    original = {
        'platform': 'Amazon',
        'site': 'US',
        'title': 'Wireless Bluetooth Earbuds (Black)',
        'bullet_points': [
            'Good quality earbuds',
            'Bluetooth headphones',
            'Long battery life',
            'Easy to use',
            'Perfect for sports'
        ],
        'keywords': 'wireless earbuds bluetooth earbuds earbuds wireless headphones'
    }

    optimized = {
        'platform': 'Amazon',
        'site': 'US',
        'title': 'Wireless Earbuds, Bluetooth 5.0 In-Ear Headphones with Charging Case - Hi-Fi Stereo Sound for Sports (Black)',
        'bullet_points': [
            'Premium Sound Quality: Advanced audio drivers deliver crystal-clear highs and deep bass',
            'Bluetooth 5.0 Connectivity: Seamless pairing with all Bluetooth-enabled devices',
            'Long Battery Life: Up to 8 hours playtime, extended to 32 hours with charging case',
            'Comfortable Fit: Ergonomic design with soft silicone ear tips for all-day wear',
            'Sport-Ready Design: Sweat-resistant and lightweight; perfect for workouts'
        ],
        'keywords': 'wireless earbuds bluetooth earbuds headphones earphones sport waterproof women men'
    }

    output_path = create_comparison_xlsx(original, optimized, "comparison_output.xlsx")
    print(f"对比文件已生成: {output_path}")


if __name__ == '__main__':
    main()
