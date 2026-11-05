#!/usr/bin/env python3
"""
Excel 多维度分组汇总脚本
功能：按指定维度分组统计、自动合并单元格、货币格式化
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter


class ExcelGroupSummary:
    """Excel 分组汇总处理器"""

    # 样式常量
    HEADER_FONT = Font(name='Microsoft YaHei', size=12, bold=True, color='FFFFFF')
    HEADER_FILL = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    HEADER_ALIGN = Alignment(horizontal='center', vertical='center')

    DATA_FONT = Font(name='Microsoft YaHei', size=11)
    DATA_ALIGN = Alignment(horizontal='left', vertical='center')
    CURRENCY_ALIGN = Alignment(horizontal='right', vertical='center')

    SUBTOTAL_FONT = Font(name='Microsoft YaHei', size=11, bold=True)
    TOTAL_FONT = Font(name='Microsoft YaHei', size=12, bold=True)
    TOTAL_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

    THIN_BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    def __init__(self, source_file: str, source_sheet: str, group_cols: List[str],
                 sum_col: str, output_file: str, merge_cols: Optional[List[str]] = None):
        self.source_file = source_file
        self.source_sheet = source_sheet
        self.group_cols = group_cols if isinstance(group_cols, list) else [g.strip() for g in group_cols.split(',')]
        self.sum_col = sum_col
        self.output_file = output_file
        self.merge_cols = merge_cols if merge_cols else []
        if isinstance(self.merge_cols, str):
            self.merge_cols = [m.strip() for m in self.merge_cols.split(',')]

        self.df: Optional[pd.DataFrame] = None
        self.wb: Optional[Workbook] = None
        self.ws = None

    def read_data(self) -> bool:
        """读取源 Excel 数据"""
        try:
            self.df = pd.read_excel(self.source_file, sheet_name=self.source_sheet)
            print(f"成功读取数据：{len(self.df)} 行, {len(self.df.columns)} 列")
            return True
        except FileNotFoundError:
            print(f"错误：文件不存在 - {self.source_file}")
            return False
        except ValueError as e:
            print(f"错误：Sheet 不存在 - {self.source_sheet}")
            print(f"可用 Sheet: {pd.ExcelFile(self.source_file).sheet_names}")
            return False
        except Exception as e:
            print(f"错误：读取文件失败 - {str(e)}")
            return False

    def validate_columns(self) -> bool:
        """验证列名是否存在"""
        missing_cols = []
        for col in self.group_cols:
            if col not in self.df.columns:
                missing_cols.append(col)
        if self.sum_col not in self.df.columns:
            missing_cols.append(self.sum_col)

        if missing_cols:
            print(f"错误：以下列名不存在 - {', '.join(missing_cols)}")
            print(f"可用列名: {', '.join(self.df.columns.tolist())}")
            return False
        return True

    def group_and_calculate(self) -> pd.DataFrame:
        """执行分组汇总计算"""
        # 确保金额列为数值类型
        self.df[self.sum_col] = pd.to_numeric(self.df[self.sum_col], errors='coerce').fillna(0)

        # 分组汇总
        grouped = self.df.groupby(self.group_cols)[self.sum_col].sum().reset_index()
        grouped.columns = self.group_cols + ['汇总金额']

        # 按分组列排序
        grouped = grouped.sort_values(by=self.group_cols)

        return grouped

    def create_workbook(self):
        """创建输出工作簿"""
        self.wb = Workbook()
        self.ws = self.ws = self.wb.active
        self.ws.title = "分组汇总"

    def write_header(self, columns: List[str]):
        """写入表头"""
        for col_idx, col_name in enumerate(columns, start=1):
            cell = self.ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = self.HEADER_ALIGN
            cell.border = self.THIN_BORDER

    def write_data(self, grouped_df: pd.DataFrame):
        """写入数据并处理合并"""
        columns = self.group_cols + ['汇总金额']
        self.write_header(columns)

        current_row = 2
        group_keys = {}  # 跟踪每个分组列的当前值和起始行

        for _, row in grouped_df.iterrows():
            # 写入数据行
            for col_idx, col_name in enumerate(columns, start=1):
                cell = self.ws.cell(row=current_row, column=col_idx)

                if col_name == '汇总金额':
                    cell.value = row['汇总金额']
                    cell.number_format = '¥#,##0'
                    cell.font = self.DATA_FONT
                    cell.alignment = self.CURRENCY_ALIGN
                else:
                    cell.value = row[col_name]
                    cell.font = self.DATA_FONT
                    cell.alignment = self.DATA_ALIGN

                cell.border = self.THIN_BORDER

            # 记录分组值
            for col_idx, col_name in enumerate(self.group_cols, start=1):
                val = row[col_name]
                if col_name not in group_keys:
                    group_keys[col_name] = {'value': val, 'start_row': current_row}
                elif group_keys[col_name]['value'] != val:
                    # 值改变了，合并之前的单元格
                    if col_name in self.merge_cols:
                        self.merge_cells_if_needed(col_name, group_keys[col_name])
                    group_keys[col_name] = {'value': val, 'start_row': current_row}

            current_row += 1

        # 处理最后一组的合并
        for col_name in self.group_cols:
            if col_name in self.merge_cols and col_name in group_keys:
                self.merge_cells_if_needed(col_name, group_keys[col_name])

        # 添加总计行
        self.write_total_row(current_row, grouped_df)

        # 调整列宽
        self.adjust_column_widths(columns)

    def merge_cells_if_needed(self, col_name: str, group_info: Dict[str, Any]):
        """合并单元格"""
        start_row = group_info['start_row']
        col_idx = self.group_cols.index(col_name) + 1

        if start_row < self.ws.max_row and start_row > 1:
            end_row = self.ws.max_row
            # 找到实际的结束行（直到值改变）
            first_val = self.ws.cell(row=start_row, column=col_idx).value
            actual_end = start_row
            for r in range(start_row + 1, self.ws.max_row + 1):
                if self.ws.cell(row=r, column=col_idx).value == first_val:
                    actual_end = r
                else:
                    break

            if actual_end > start_row:
                self.ws.merge_cells(
                    start_row=start_row, start_column=col_idx,
                    end_row=actual_end, end_column=col_idx
                )
                # 设置合并后单元格样式
                merged_cell = self.ws.cell(row=start_row, column=col_idx)
                merged_cell.alignment = Alignment(horizontal='center', vertical='center')

    def write_total_row(self, row: int, grouped_df: pd.DataFrame):
        """写入总计行"""
        total_value = grouped_df['汇总金额'].sum()

        for col_idx in range(1, len(self.group_cols) + 1):
            cell = self.ws.cell(row=row, column=col_idx)
            cell.value = '总计' if col_idx == len(self.group_cols) else ''
            cell.font = self.TOTAL_FONT
            cell.fill = self.TOTAL_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = self.THIN_BORDER

        total_cell = self.ws.cell(row=row, column=len(self.group_cols) + 1)
        total_cell.value = total_value
        total_cell.number_format = '¥#,##0'
        total_cell.font = self.TOTAL_FONT
        total_cell.fill = self.TOTAL_FILL
        total_cell.alignment = self.CURRENCY_ALIGN
        total_cell.border = self.THIN_BORDER

    def adjust_column_widths(self, columns: List[str]):
        """调整列宽"""
        for col_idx, col_name in enumerate(columns, start=1):
            col_letter = get_column_letter(col_idx)
            if col_name == '汇总金额':
                self.ws.column_dimensions[col_letter].width = 15
            else:
                # 根据表头长度设置宽度
                width = max(len(str(col_name)) * 2, 12)
                self.ws.column_dimensions[col_letter].width = min(width, 30)

    def save(self) -> bool:
        """保存工作簿"""
        try:
            self.wb.save(self.output_file)
            print(f"成功保存文件：{self.output_file}")
            return True
        except Exception as e:
            print(f"错误：保存文件失败 - {str(e)}")
            return False

    def execute(self) -> bool:
        """执行完整的分组汇总流程"""
        print("=" * 50)
        print("Excel 多维度分组汇总")
        print("=" * 50)

        # Phase 1: 读取数据
        print("\n[Phase 1] 读取源数据...")
        if not self.read_data():
            return False

        # Phase 2: 验证列名
        print("\n[Phase 2] 验证列名...")
        if not self.validate_columns():
            return False

        # Phase 3: 分组计算
        print("\n[Phase 3] 执行分组汇总...")
        grouped_df = self.group_and_calculate()
        print(f"分组结果：{len(grouped_df)} 个分组")

        # Phase 4: 创建工作簿
        print("\n[Phase 4] 生成汇总表...")
        self.create_workbook()
        self.write_data(grouped_df)

        # Phase 5: 保存
        print("\n[Phase 5] 保存文件...")
        if not self.save():
            return False

        print("\n" + "=" * 50)
        print("执行完成！")
        print("=" * 50)
        return True


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='Excel 多维度分组汇总')
    parser.add_argument('--source-file', required=True, help='源 Excel 文件路径')
    parser.add_argument('--source-sheet', required=True, help='源工作表名称')
    parser.add_argument('--group-cols', required=True, help='分组维度列名（逗号分隔）')
    parser.add_argument('--sum-col', required=True, help='需要汇总的金额列名')
    parser.add_argument('--output-file', required=True, help='输出文件路径')
    parser.add_argument('--merge-cols', default='', help='需要合并单元格的列名（逗号分隔）')

    args = parser.parse_args()

    processor = ExcelGroupSummary(
        source_file=args.source_file,
        source_sheet=args.source_sheet,
        group_cols=args.group_cols,
        sum_col=args.sum_col,
        output_file=args.output_file,
        merge_cols=args.merge_cols if args.merge_cols else None
    )

    success = processor.execute()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
