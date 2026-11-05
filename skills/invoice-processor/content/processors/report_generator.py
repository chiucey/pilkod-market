#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报销报表生成器
生成美观的Excel报销明细表
"""
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报销报表生成器"""

    # 类型名称映射
    TYPE_MAPPING = {
        'flight': '交通-航空',
        'train': '交通-铁路',
        'hotel': '住宿',
        'meal': '餐饮',
        'insurance': '保险',
        'taxi': '交通-出租车',
        'ctrip_order': '携程订单',
        'other': '其他'
    }

    # 报表列配置
    MAIN_COLUMNS = [
        {'key': 'invoice_no', 'header': '发票号码', 'width': 18},
        {'key': 'type_name', 'header': '类型', 'width': 10},
        {'key': 'sub_type', 'header': '明细类型', 'width': 10},
        {'key': 'date', 'header': '日期', 'width': 12},
        {'key': 'description', 'header': '内容描述', 'width': 25},
        {'key': 'departure', 'header': '出发地', 'width': 10},
        {'key': 'arrival', 'header': '目的地', 'width': 10},
        {'key': 'amount', 'header': '金额', 'width': 12},
        {'key': 'invoice_no', 'header': '发票号', 'width': 18},
        {'key': 'remarks', 'header': '备注', 'width': 30},
        {'key': 'status', 'header': '状态', 'width': 10}
    ]

    # 表头样式
    HEADER_FONT = Font(bold=True, color='FFFFFF', size=11)
    HEADER_FILL = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    HEADER_ALIGNMENT = Alignment(horizontal='center', vertical='center')

    # 数据样式
    DATA_FONT = Font(size=10)
    DATA_ALIGNMENT = Alignment(horizontal='left', vertical='center')

    # 金额样式
    AMOUNT_ALIGNMENT = Alignment(horizontal='right', vertical='center')

    # 边框样式
    THIN_BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    def __init__(self):
        """初始化报表生成器"""
        self.workbook = None

    def generate_main_report(self, invoices: List[Dict]) -> pd.DataFrame:
        """
        生成主报销明细表

        Args:
            invoices: 发票列表

        Returns:
            pd.DataFrame: 报销明细DataFrame
        """
        # 准备数据
        data = []
        for invoice in invoices:
            inv_type = invoice.get('type', 'other')
            type_name = self.TYPE_MAPPING.get(inv_type, invoice.get('sub_type', '其他'))

            row = {
                '发票号码': invoice.get('invoice_no', ''),
                '类型': type_name,
                '明细类型': invoice.get('sub_type', ''),
                '日期': invoice.get('date', '')[:10] if invoice.get('date') else '',
                '内容描述': invoice.get('description', ''),
                '出发地': invoice.get('departure', '') or '',
                '目的地': invoice.get('arrival', '') or '',
                '金额': invoice.get('amount', 0),
                '备注': invoice.get('remarks', ''),
                '状态': self._get_status_text(invoice.get('status', 'extracted'))
            }
            data.append(row)

        df = pd.DataFrame(data)

        # 按类型和日期排序
        if not df.empty:
            df = df.sort_values(['类型', '日期'], ascending=[True, True])

        return df

    def generate_type_reports(self, invoices: List[Dict]) -> Dict[str, pd.DataFrame]:
        """
        按类型生成不同工作簿的报表

        Args:
            invoices: 发票列表

        Returns:
            Dict[str, pd.DataFrame]: 按类型分类的报表字典
        """
        type_reports = {}

        # 定义类型分类
        type_groups = {
            '交通-航空': [],
            '交通-铁路': [],
            '住宿': [],
            '餐饮': [],
            '保险': [],
            '其他': []
        }

        # 分类
        for invoice in invoices:
            inv_type = invoice.get('type', 'other')
            type_name = self.TYPE_MAPPING.get(inv_type, '其他')

            # 进一步细分
            if type_name == '交通-航空':
                type_key = '交通-航空'
            elif type_name == '交通-铁路':
                type_key = '交通-铁路'
            else:
                type_key = type_name

            if type_key not in type_groups:
                type_groups[type_key] = []

            type_groups[type_key].append(invoice)

        # 转换为DataFrame
        for type_key, inv_list in type_groups.items():
            if inv_list:
                type_reports[type_key] = self.generate_main_report(inv_list)

        return type_reports

    def generate_travel_report(self, trips: List[Dict], base_city: str = "南京") -> pd.DataFrame:
        """
        生成出差专项报表

        Args:
            trips: 出差行程列表
            base_city: 基准城市

        Returns:
            pd.DataFrame: 出差报表DataFrame
        """
        data = []

        for trip in trips:
            # 计算各类金额
            transport_amount = sum(
                inv.get('amount', 0) for inv in
                trip.get('outbound', []) + trip.get('return', [])
            )
            hotel_amount = sum(inv.get('amount', 0) for inv in trip.get('accommodations', []))
            insurance_amount = sum(inv.get('amount', 0) for inv in trip.get('insurance', []))
            meal_amount = sum(inv.get('amount', 0) for inv in trip.get('meals', []))
            other_amount = sum(inv.get('amount', 0) for inv in trip.get('other', []))

            row = {
                '出差序号': trip.get('trip_id', ''),
                '出发日期': trip.get('start_date', '')[:10] if trip.get('start_date') else '',
                '返回日期': trip.get('end_date', '')[:10] if trip.get('end_date') else '',
                '出差天数': trip.get('days', 1),
                '目的城市': trip.get('arrival_city', ''),
                '去程交通': transport_amount / 2 if trip.get('outbound') else 0,
                '返程交通': transport_amount / 2 if trip.get('return') else 0,
                '住宿费用': hotel_amount,
                '餐饮费用': meal_amount,
                '保险费用': insurance_amount,
                '其他费用': other_amount,
                '合计金额': trip.get('total_amount', 0),
                '缺失票据': '、'.join(trip.get('missing_items', [])) or '无',
                '备注': f"从{base_city}出发"
            }
            data.append(row)

        df = pd.DataFrame(data)
        return df

    def save_to_excel(self, main_df: pd.DataFrame, type_reports: Dict[str, pd.DataFrame],
                      travel_df: pd.DataFrame, output_path: str, base_city: str = "南京"):
        """
        保存到Excel文件，带格式美化

        Args:
            main_df: 主报表DataFrame
            type_reports: 分类报表字典
            travel_df: 出差报表DataFrame
            output_path: 输出文件路径
            base_city: 基准城市
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 主报表
            main_df.to_excel(writer, sheet_name='报销明细总表', index=False)

            # 分类报表
            for sheet_name, df in type_reports.items():
                # Excel sheet名称长度限制
                safe_name = sheet_name[:31]
                df.to_excel(writer, sheet_name=safe_name, index=False)

            # 出差报表
            travel_df.to_excel(writer, sheet_name='出差专项报表', index=False)

        # 美化Excel
        self._beautify_excel(output_path)

        logger.info(f"报表已保存: {output_path}")

    def _beautify_excel(self, file_path: str):
        """
        美化Excel格式

        Args:
            file_path: Excel文件路径
        """
        from openpyxl import load_workbook

        wb = load_workbook(file_path)

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]

            # 设置表头样式
            for cell in ws[1]:
                cell.font = self.HEADER_FONT
                cell.fill = self.HEADER_FILL
                cell.alignment = self.HEADER_ALIGNMENT
                cell.border = self.THIN_BORDER

            # 设置数据样式
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.font = self.DATA_FONT
                    cell.border = self.THIN_BORDER

                    # 金额列右对齐
                    if cell.column_letter == self._get_amount_column(ws):
                        cell.alignment = self.AMOUNT_ALIGNMENT
                        # 金额格式
                        if cell.value is not None:
                            cell.number_format = '#,##0.00'
                    else:
                        cell.alignment = self.DATA_ALIGNMENT

            # 自动调整列宽
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if cell.value:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            # 设置行高
            ws.row_dimensions[1].height = 25

            # 冻结首行
            ws.freeze_panes = 'A2'

        wb.save(file_path)

    def _get_amount_column(self, worksheet) -> str:
        """获取金额列的字母标识"""
        for cell in worksheet[1]:
            if cell.value == '金额':
                return cell.column_letter
            if cell.value == '合计金额':
                return cell.column_letter
            if cell.value == '交通费用':
                return cell.column_letter
        return 'H'  # 默认返回H列

    def _get_status_text(self, status: str) -> str:
        """获取状态文本"""
        status_map = {
            'extracted': '已提取',
            'extracted_with_llm': 'AI增强',
            'extracted_rule_only': '规则提取',
            'pending': '待处理',
            'missing': '缺失'
        }
        return status_map.get(status, status)

    def generate_summary(self, invoices: List[Dict], trips: List[Dict]) -> Dict[str, Any]:
        """
        生成汇总统计

        Args:
            invoices: 发票列表
            trips: 行程列表

        Returns:
            Dict: 汇总统计信息
        """
        # 按类型统计金额
        type_amounts = {}
        for invoice in invoices:
            inv_type = invoice.get('type', 'other')
            type_name = self.TYPE_MAPPING.get(inv_type, '其他')
            amount = invoice.get('amount', 0)

            if type_name not in type_amounts:
                type_amounts[type_name] = 0
            type_amounts[type_name] += amount

        # 计算总金额
        total_amount = sum(inv.get('amount', 0) for inv in invoices)

        return {
            'total_invoices': len(invoices),
            'total_amount': total_amount,
            'type_amounts': type_amounts,
            'total_trips': len(trips),
            'trips_amount': sum(trip.get('total_amount', 0) for trip in trips)
        }
