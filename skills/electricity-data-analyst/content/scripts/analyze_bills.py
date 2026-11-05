#!/usr/bin/env python3
"""
电力客户账单数据分析脚本
功能：读取客户账单文件，提取分时段用电量及电费数据，按月汇总生成统计报表
"""

import os
import re
import glob
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BillingRecord:
    """账单记录数据类"""
    # 基本信息
    month: str = ""  # 月份，从文件名提取
    customer_id: str = ""  # 户号
    customer_name: str = ""  # 户名
    group_name: str = ""  # 集团户名
    usage_category: str = ""  # 用电类别
    market_attribute: str = ""  # 市场化属性

    # 总计
    total_power_kwh: float = 0.0  # 本期电量(千瓦时)
    total_cost_yuan: float = 0.0  # 本期电费(元)
    avg_price: float = 0.0  # 平均电价(元/千瓦时)

    # 尖段
    peak_kwh: float = 0.0  # 尖段计费电量
    peak_rate: float = 0.0  # 尖段计费标准
    peak_cost: float = 0.0  # 尖段电费

    # 峰段
    shoulder_kwh: float = 0.0  # 峰段计费电量
    shoulder_rate: float = 0.0  # 峰段计费标准
    shoulder_cost: float = 0.0  # 峰段电费

    # 平段
    flat_kwh: float = 0.0  # 平段计费电量
    flat_rate: float = 0.0  # 平段计费标准
    flat_cost: float = 0.0  # 平段电费

    # 谷段
    valley_kwh: float = 0.0  # 谷段计费电量
    valley_rate: float = 0.0  # 谷段计费标准
    valley_cost: float = 0.0  # 谷段电费

    # 其他费用
    capacity_cost: float = 0.0  # 输配容需量电费
    power_factor_cost: float = 0.0  # 功率因数调整电费


class BillAnalyzer:
    """账单分析器"""

    # 字段映射配置
    FIELD_MAPPINGS = {
        # 基本信息字段映射
        '户号': 'customer_id',
        '用户编号': 'customer_id',
        '客户编号': 'customer_id',
        '户名': 'customer_name',
        '客户名称': 'customer_name',
        '用户名': 'customer_name',
        '集团户名': 'group_name',
        '集团名称': 'group_name',
        '用电类别': 'usage_category',
        '用户类型': 'usage_category',
        '市场化属性': 'market_attribute',
        '属性': 'market_attribute',

        # 电量字段映射
        '本期电量': 'total_power_kwh',
        '总电量': 'total_power_kwh',
        '用电量': 'total_power_kwh',
        '尖段电量': 'peak_kwh',
        '尖峰电量': 'peak_kwh',
        '峰段电量': 'shoulder_kwh',
        '平段电量': 'flat_kwh',
        '谷段电量': 'valley_kwh',

        # 电费字段映射
        '本期电费': 'total_cost_yuan',
        '总电费': 'total_cost_yuan',
        '尖段电费': 'peak_cost',
        '尖峰电费': 'peak_cost',
        '峰段电费': 'shoulder_cost',
        '平段电费': 'flat_cost',
        '谷段电费': 'valley_cost',

        # 费率字段映射
        '尖段标准': 'peak_rate',
        '尖段单价': 'peak_rate',
        '尖峰单价': 'peak_rate',
        '峰段标准': 'shoulder_rate',
        '峰段单价': 'shoulder_rate',
        '平段标准': 'flat_rate',
        '平段单价': 'flat_rate',
        '谷段标准': 'valley_rate',
        '谷段单价': 'valley_rate',

        # 其他费用
        '输配容需量电费': 'capacity_cost',
        '容量电费': 'capacity_cost',
        '需量电费': 'capacity_cost',
        '功率因数调整电费': 'power_factor_cost',
        '力调电费': 'power_factor_cost',
    }

    def __init__(self, bills_dir: str, output_dir: str = "output"):
        """
        初始化账单分析器

        Args:
            bills_dir: 账单文件目录路径
            output_dir: 输出目录路径
        """
        self.bills_dir = Path(bills_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.statistics_dir = self.output_dir / "statistics"
        self.statistics_dir.mkdir(parents=True, exist_ok=True)

    def extract_month_from_filename(self, filename: str) -> Optional[str]:
        """
        从文件名提取月份信息

        Args:
            filename: 文件名

        Returns:
            月份字符串，格式如 "2024-01"，失败返回None
        """
        # 匹配常见格式：2024-01账单、2024年01月账单、202401账单
        patterns = [
            r'(\d{4})-(\d{1,2})',  # 2024-01
            r'(\d{4})年(\d{1,2})月',  # 2024年01月
            r'(\d{4})(\d{2})',  # 202401
        ]

        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                if len(match.groups()) == 2:
                    year, month = match.groups()
                    return f"{year}-{month.zfill(2)}"
        return None

    def read_bill_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        读取账单文件

        Args:
            filepath: 文件路径

        Returns:
            账单记录列表
        """
        suffix = filepath.suffix.lower()

        try:
            if suffix in ['.xlsx', '.xls']:
                return self._read_excel(filepath)
            elif suffix == '.csv':
                return self._read_csv(filepath)
            elif suffix == '.pdf':
                return self._read_pdf(filepath)
            else:
                logger.warning(f"不支持的文件格式: {suffix}")
                return []
        except Exception as e:
            logger.error(f"读取文件失败 {filepath}: {e}")
            return []

    def _read_excel(self, filepath: Path) -> List[Dict[str, Any]]:
        """读取Excel文件"""
        records = []
        month = self.extract_month_from_filename(filepath.name)

        # 读取所有sheet
        excel_file = pd.ExcelFile(filepath)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            records.extend(self._process_dataframe(df, month, sheet_name))

        return records

    def _read_csv(self, filepath: Path) -> List[Dict[str, Any]]:
        """读取CSV文件"""
        month = self.extract_month_from_filename(filepath.name)
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        return self._process_dataframe(df, month, filepath.stem)

    def _read_pdf(self, filepath: Path) -> List[Dict[str, Any]]:
        """读取PDF文件 - 简化实现"""
        logger.warning("PDF解析支持有限，建议使用Excel或CSV格式")
        return []

    def _process_dataframe(self, df: pd.DataFrame, month: str, source: str) -> List[Dict[str, Any]]:
        """
        处理DataFrame，提取账单数据

        Args:
            df: 数据框
            month: 月份
            source: 数据来源

        Returns:
            记录列表
        """
        records = []

        # 标准化列名
        df.columns = df.columns.str.strip()

        # 尝试识别数据区域
        for idx, row in df.iterrows():
            # 检查是否是有效数据行
            if self._is_valid_data_row(row):
                record = self._extract_record(row.to_dict(), month)
                if record:
                    records.append(record)

        # 如果没有找到标准格式，尝试整表解析
        if not records:
            records = self._parse_whole_table(df, month, source)

        return records

    def _is_valid_data_row(self, row: pd.Series) -> bool:
        """检查是否是有效数据行"""
        # 检查是否有非空数值
        for val in row.values:
            if pd.notna(val):
                try:
                    float(val)
                    return True
                except (ValueError, TypeError):
                    pass
        return False

    def _extract_record(self, row_data: Dict[str, Any], month: str) -> Optional[Dict[str, Any]]:
        """从行数据中提取记录"""
        record = {'month': month}

        for col_name, value in row_data.items():
            if pd.isna(value):
                continue

            # 尝试匹配字段
            col_str = str(col_name).strip()
            if col_str in self.FIELD_MAPPINGS:
                field = self.FIELD_MAPPINGS[col_str]
                try:
                    record[field] = float(value)
                except (ValueError, TypeError):
                    record[field] = str(value)

        # 只有当有电量或电费数据时才返回
        if 'total_power_kwh' in record or 'total_cost_yuan' in record:
            return record
        return None

    def _parse_whole_table(self, df: pd.DataFrame, month: str, source: str) -> List[Dict[str, Any]]:
        """整表解析 - 尝试从整个表格提取数据"""
        records = []
        record = {'month': month}

        # 遍历所有列
        for col in df.columns:
            col_str = str(col).strip()

            # 查找字段映射
            for key, field in self.FIELD_MAPPINGS.items():
                if key in col_str:
                    # 尝试获取该列的值
                    values = df[col].dropna()
                    if len(values) > 0:
                        try:
                            record[field] = float(values.iloc[0])
                        except:
                            record[field] = str(values.iloc[0])

        if len(record) > 1:
            records.append(record)

        return records

    def aggregate_records(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        汇总记录，按月合并

        Args:
            records: 原始记录列表

        Returns:
            汇总后的DataFrame
        """
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # 按月份分组汇总
        numeric_cols = [
            'total_power_kwh', 'total_cost_yuan',
            'peak_kwh', 'peak_rate', 'peak_cost',
            'shoulder_kwh', 'shoulder_rate', 'shoulder_cost',
            'flat_kwh', 'flat_rate', 'flat_cost',
            'valley_kwh', 'valley_rate', 'valley_cost',
            'capacity_cost', 'power_factor_cost'
        ]

        # 保留文本字段的第一个值
        text_cols = ['customer_id', 'customer_name', 'group_name',
                     'usage_category', 'market_attribute']

        # 分组聚合
        grouped = df.groupby('month').agg({
            **{col: 'sum' for col in numeric_cols if col in df.columns},
            **{col: 'first' for col in text_cols if col in df.columns}
        }).reset_index()

        # 计算平均电价
        if 'total_power_kwh' in grouped.columns and 'total_cost_yuan' in grouped.columns:
            grouped['avg_price'] = grouped.apply(
                lambda row: row['total_cost_yuan'] / row['total_power_kwh']
                if row['total_power_kwh'] > 0 else 0, axis=1
            )

        # 按月份排序
        grouped = grouped.sort_values('month')

        return grouped

    def format_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        格式化输出列

        Args:
            df: DataFrame

        Returns:
            格式化后的DataFrame
        """
        if df.empty:
            return df

        # 定义列顺序
        column_order = [
            'month',
            'customer_id', 'customer_name', 'group_name',
            'usage_category', 'market_attribute',
            'total_power_kwh', 'total_cost_yuan', 'avg_price',
            'peak_kwh', 'peak_rate', 'peak_cost',
            'shoulder_kwh', 'shoulder_rate', 'shoulder_cost',
            'flat_kwh', 'flat_rate', 'flat_cost',
            'valley_kwh', 'valley_rate', 'valley_cost',
            'capacity_cost', 'power_factor_cost'
        ]

        # 中文列名映射
        chinese_names = {
            'month': '月份',
            'customer_id': '户号',
            'customer_name': '户名',
            'group_name': '集团户名',
            'usage_category': '用电类别',
            'market_attribute': '市场化属性',
            'total_power_kwh': '本期电量',
            'total_cost_yuan': '本期电费',
            'avg_price': '平均电价',
            'peak_kwh': '尖段_计费电量',
            'peak_rate': '尖段_计费标准',
            'peak_cost': '尖段_电费',
            'shoulder_kwh': '峰段_计费电量',
            'shoulder_rate': '峰段_计费标准',
            'shoulder_cost': '峰段_电费',
            'flat_kwh': '平段_计费电量',
            'flat_rate': '平段_计费标准',
            'flat_cost': '平段_电费',
            'valley_kwh': '谷段_计费电量',
            'valley_rate': '谷段_计费标准',
            'valley_cost': '谷段_电费',
            'capacity_cost': '输配容需量电费',
            'power_factor_cost': '功率因数调整电费'
        }

        # 选择存在的列
        existing_cols = [col for col in column_order if col in df.columns]
        df = df[existing_cols]

        # 重命名为中文
        df = df.rename(columns=chinese_names)

        return df

    def analyze(self) -> pd.DataFrame:
        """
        执行分析

        Returns:
            统计结果DataFrame
        """
        logger.info(f"开始分析账单目录: {self.bills_dir}")

        # 收集所有记录
        all_records = []

        # 支持的文件模式
        patterns = ['*.xlsx', '*.xls', '*.csv', '*.pdf']

        for pattern in patterns:
            for filepath in self.bills_dir.rglob(pattern):
                logger.info(f"处理文件: {filepath}")
                records = self.read_bill_file(filepath)
                all_records.extend(records)

        logger.info(f"共提取 {len(all_records)} 条记录")

        # 汇总
        if all_records:
            df = self.aggregate_records(all_records)
            df = self.format_output_columns(df)

            # 保存结果
            output_path = self.statistics_dir / "monthly_summary.csv"
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"统计结果已保存至: {output_path}")

            return df
        else:
            logger.warning("未提取到任何记录")
            return pd.DataFrame()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='电力客户账单数据分析')
    parser.add_argument('bills_dir', help='账单文件目录路径')
    parser.add_argument('-o', '--output', default='output', help='输出目录路径')

    args = parser.parse_args()

    analyzer = BillAnalyzer(args.bills_dir, args.output)
    result = analyzer.analyze()

    if not result.empty:
        print("\n统计结果预览:")
        print(result.to_string())
        print(f"\n结果已保存至: {args.output}/statistics/monthly_summary.csv")
    else:
        print("未找到有效的账单数据")


if __name__ == '__main__':
    main()
