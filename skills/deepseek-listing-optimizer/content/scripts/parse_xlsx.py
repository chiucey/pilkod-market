#!/usr/bin/env python3
"""
XLSX文件解析脚本
用于解析刊登文件并提取必要字段
"""

import openpyxl
from typing import Dict, List, Optional
import sys

def parse_xlsx_file(file_path: str) -> Dict:
    """
    解析XLSX文件并提取刊登相关字段

    Args:
        file_path: XLSX文件路径

    Returns:
        Dict包含以下字段:
        - platform: 平台
        - site: 站点
        - title: 标题
        - keywords: 关键词
        - description: 描述
        - bullet_points: 五点列表
    """
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        # 获取表头
        headers = []
        for cell in sheet[1]:
            headers.append(cell.value)

        # 字段映射（支持多种可能的列名）
        field_mapping = {
            'platform': ['平台', 'Platform', 'platform', 'PLATFORM'],
            'site': ['站点', 'Site', 'site', 'SITE', 'Country', 'country'],
            'title': ['标题', 'Title', 'title', 'TITLE', 'Product Title', 'Product Title'],
            'keywords': ['关键词', 'Keywords', 'keywords', 'KEYWORDS', 'Search Terms'],
            'description': ['描述', 'Description', 'description', 'DESCRIPTION', 'Product Description'],
            'bullet_points': ['五点', 'Bullet Points', 'Bullet Points', '五点描述', 'Bullets']
        }

        # 找到各列的索引
        column_indices = {}
        for field, possible_names in field_mapping.items():
            for i, header in enumerate(headers):
                if header in possible_names:
                    column_indices[field] = i
                    break

        # 提取数据
        result = {
            'platform': '',
            'site': '',
            'title': '',
            'keywords': '',
            'description': '',
            'bullet_points': []
        }

        # 提取基本字段
        for field, index in column_indices.items():
            if field == 'bullet_points':
                continue
            value = sheet.cell(row=2, column=index+1).value
            if value:
                result[field] = str(value).strip()

        # 提取五点
        if 'bullet_points' in column_indices:
            bp_col = column_indices['bullet_points']
            for row in range(2, min(7, sheet.max_row + 1)):  # 五点通常在前5行
                value = sheet.cell(row=row, column=bp_col+1).value
                if value:
                    result['bullet_points'].append(str(value).strip())

        # 检查必填字段
        missing_fields = []
        if not result['platform']:
            missing_fields.append('平台')
        if not result['site']:
            missing_fields.append('站点')
        if not result['title']:
            missing_fields.append('标题')

        if missing_fields:
            return {
                'success': False,
                'error': f'缺少必填字段: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'data': result
            }

        return {
            'success': True,
            'data': result
        }

    except FileNotFoundError:
        return {
            'success': False,
            'error': f'文件未找到: {file_path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'解析文件时出错: {str(e)}'
        }


def validate_data(data: Dict) -> tuple:
    """
    验证数据完整性

    Args:
        data: 解析后的数据字典

    Returns:
        (is_valid, warnings): 是否有效，警告信息列表
    """
    warnings = []
    is_valid = True

    # 检查必填字段
    required = ['platform', 'site', 'title']
    for field in required:
        if not data.get(field):
            warnings.append(f'缺少必填字段: {field}')
            is_valid = False

    # 检查可选字段
    optional = ['keywords', 'description', 'bullet_points']
    for field in optional:
        if not data.get(field):
            if field == 'bullet_points' and len(data.get('bullet_points', [])) == 0:
                warnings.append(f'可选字段为空: {field}（优化时将跳过）')
            elif field != 'bullet_points' and not data.get(field):
                warnings.append(f'可选字段为空: {field}（优化时将使用默认值）')

    return is_valid, warnings


def main():
    """主函数，用于命令行测试"""
    if len(sys.argv) < 2:
        print("用法: python parse_xlsx.py <file_path>")
        sys.exit(1)

    result = parse_xlsx_file(sys.argv[1])

    if result['success']:
        print("解析成功!")
        print("=" * 50)
        for key, value in result['data'].items():
            if key == 'bullet_points':
                print(f"{key}:")
                for i, bp in enumerate(value, 1):
                    print(f"  {i}. {bp}")
            else:
                print(f"{key}: {value}")
    else:
        print(f"解析失败: {result['error']}")
        if 'missing_fields' in result:
            print(f"缺失字段: {result['missing_fields']}")


if __name__ == '__main__':
    main()
