#!/usr/bin/env python3
"""
Excel多源数据合并处理器
用于从多个Excel文件中匹配、提取、转换数据并生成新Excel
"""

import pandas as pd
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json


class ExcelMerger:
    """Excel多源数据合并处理器"""

    def __init__(self):
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.merge_rules: Dict = {}

    def read_excel(self, file_path: str, sheet_name: str = 0) -> pd.DataFrame:
        """读取Excel文件"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.dataframes[file_path] = df
            return df
        except Exception as e:
            raise ValueError(f"读取文件失败 {file_path}: {str(e)}")

    def analyze_file(self, file_path: str) -> Dict:
        """分析Excel文件结构"""
        df = self.read_excel(file_path)
        return {
            'file': file_path,
            'rows': len(df),
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'null_counts': df.isnull().sum().to_dict()
        }

    def merge_files(self,
                    left_file: str,
                    right_file: str,
                    left_key: str,
                    right_key: str,
                    how: str = 'inner',
                    suffixes: tuple = ('_x', '_y')) -> pd.DataFrame:
        """
        合并两个Excel文件

        参数:
            left_file: 左文件路径
            right_file: 右文件路径
            left_key: 左文件匹配键
            right_key: 右文件匹配键
            how: 合并方式 ('inner', 'left', 'right', 'outer')
            suffixes: 重名列后缀
        """
        left_df = self.dataframes.get(left_file)
        right_df = self.dataframes.get(right_file)

        if left_df is None:
            left_df = self.read_excel(left_file)
        if right_df is None:
            right_df = self.read_excel(right_file)

        # 确保匹配键数据类型一致
        left_df[left_key] = self._normalize_key(left_df[left_key])
        right_df[right_key] = self._normalize_key(right_df[right_key])

        result = pd.merge(
            left_df,
            right_df,
            left_on=left_key,
            right_on=right_key,
            how=how,
            suffixes=suffixes
        )
        return result

    def extract_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """提取指定列"""
        return df[columns]

    def transform_column(self,
                         df: pd.DataFrame,
                         new_col: str,
                         expression: str) -> pd.DataFrame:
        """
        根据表达式计算新列

        示例:
            expression: "quantity * price"
            expression: "date_end - date_start"
        """
        df[new_col] = df.eval(expression)
        return df

    def filter_rows(self, df: pd.DataFrame, condition: str) -> pd.DataFrame:
        """按条件筛选行"""
        return df.query(condition)

    def rename_column(self, df: pd.DataFrame, old_name: str, new_name: str) -> pd.DataFrame:
        """重命名列"""
        return df.rename(columns={old_name: new_name})

    def convert_dtype(self, df: pd.DataFrame, column: str, dtype: str) -> pd.DataFrame:
        """转换列数据类型"""
        if dtype == 'date':
            df[column] = pd.to_datetime(df[column])
        elif dtype == 'number':
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif dtype == 'string':
            df[column] = df[column].astype(str)
        return df

    def clean_data(self,
                   df: pd.DataFrame,
                   strip_strings: bool = True,
                   fill_na: Optional[any] = None,
                   drop_duplicates: bool = False) -> pd.DataFrame:
        """清洗数据"""
        if strip_strings:
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip()

        if fill_na is not None:
            df.fillna(fill_na, inplace=True)

        if drop_duplicates:
            df.drop_duplicates(inplace=True)

        return df

    def export_excel(self,
                     df: pd.DataFrame,
                     output_path: str,
                     sheet_name: str = 'Sheet1',
                     freeze_header: bool = True) -> str:
        """导出Excel文件"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # 格式化
                worksheet = writer.sheets[sheet_name]

                # 冻结首行
                if freeze_header:
                    worksheet.freeze_panes = 'A2'

                # 自动调整列宽
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            return output_path
        except Exception as e:
            raise ValueError(f"导出文件失败: {str(e)}")

    def _normalize_key(self, series: pd.Series) -> pd.Series:
        """标准化匹配键"""
        series = series.astype(str).str.strip().str.upper()
        return series


def process_from_config(config_path: str) -> str:
    """根据配置文件处理Excel"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    merger = ExcelMerger()

    # 读取所有源文件
    for file_info in config.get('source_files', []):
        merger.read_excel(file_info['path'], file_info.get('sheet', 0))

    # 执行合并
    result_df = None
    for merge_rule in config.get('merge_rules', []):
        if result_df is None:
            result_df = merger.merge_files(
                merge_rule['left'],
                merge_rule['right'],
                merge_rule['left_key'],
                merge_rule['right_key'],
                merge_rule.get('how', 'inner')
            )
        else:
            # 将结果与下一个文件合并
            next_df = merger.merge_files(
                '__result__',
                merge_rule['right'],
                config.get('result_key', 'id'),
                merge_rule['right_key'],
                merge_rule.get('how', 'inner')
            )
            result_df = next_df

    # 应用转换
    if 'transformations' in config:
        for transform in config['transformations']:
            if transform['type'] == 'rename':
                result_df = merger.rename_column(
                    result_df, transform['old'], transform['new']
                )
            elif transform['type'] == 'filter':
                result_df = merger.filter_rows(result_df, transform['condition'])
            elif transform['type'] == 'compute':
                result_df = merger.transform_column(
                    result_df, transform['column'], transform['expression']
                )

    # 清洗数据
    result_df = merger.clean_data(
        result_df,
        strip_strings=True,
        fill_na=config.get('fill_na'),
        drop_duplicates=config.get('drop_duplicates', False)
    )

    # 导出结果
    output_path = config['output']
    merger.export_excel(result_df, output_path)

    return output_path


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        output = process_from_config(config_path)
        print(f"处理完成，输出文件: {output}")
    else:
        print("用法: python excel_processor.py <config.json>")
