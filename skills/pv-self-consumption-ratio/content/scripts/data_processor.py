"""
数据标准化处理模块
Data Processor for PV Self-Consumption Calculation

功能：
1. 处理电费核查联数据
2. 处理用电负荷曲线数据
3. 数据质量检查与清洗
4. 数据标准化输出
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import warnings

warnings.filterwarnings('ignore')


class ElectricityBillProcessor:
    """电费核查联数据处理器"""

    REQUIRED_FIELDS = [
        'settlement_period',  # 结算周期
        'peak_consumption',    # 峰时段电量
        'valley_consumption',  # 谷时段电量
        'flat_consumption',    # 平时段电量
        'max_demand',          # 最大需量
        'voltage_level',       # 电压等级
        'price'                # 电价
    ]

    def __init__(self):
        self.data = None
        self.quality_report = {}

    def load_from_dataframe(self, df: pd.DataFrame) -> bool:
        """
        从DataFrame加载数据

        Args:
            df: 电费核查联数据

        Returns:
            加载是否成功
        """
        try:
            # 检查必需字段
            missing_fields = self._check_required_fields(df.columns.tolist())
            if missing_fields:
                self.quality_report['error'] = f"缺少必需字段: {missing_fields}"
                return False

            self.data = df.copy()
            self._perform_quality_check()
            return True

        except Exception as e:
            self.quality_report['error'] = str(e)
            return False

    def load_from_dict(self, data: List[Dict]) -> bool:
        """
        从字典列表加载数据

        Args:
            data: 电费数据列表

        Returns:
            加载是否成功
        """
        try:
            df = pd.DataFrame(data)
            return self.load_from_dataframe(df)
        except Exception as e:
            self.quality_report['error'] = str(e)
            return False

    def _check_required_fields(self, columns: List[str]) -> List[str]:
        """检查必需字段"""
        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in columns:
                missing.append(field)
        return missing

    def _perform_quality_check(self):
        """执行数据质量检查"""
        self.quality_report = {
            'total_records': len(self.data),
            'missing_values': self.data.isnull().sum().to_dict(),
            'data_range': {
                'start': self.data['settlement_period'].min(),
                'end': self.data['settlement_period'].max()
            }
        }

        # 检查数据完整性
        if len(self.data) < 12:
            self.quality_report['warning'] = "数据不足12个月，结果可能不够准确"

        # 检查缺失值
        missing_pct = (self.data.isnull().sum() / len(self.data) * 100).to_dict()
        self.quality_report['missing_percentage'] = missing_pct

    def get_annual_summary(self) -> Dict[str, float]:
        """
        获取年度用电汇总

        Returns:
            年度统计字典
        """
        if self.data is None:
            return {}

        annual = {
            'total_consumption': self.data[[
                'peak_consumption', 'valley_consumption', 'flat_consumption'
            ]].sum().sum(),
            'peak_consumption': self.data['peak_consumption'].sum(),
            'valley_consumption': self.data['valley_consumption'].sum(),
            'flat_consumption': self.data['flat_consumption'].sum(),
            'avg_max_demand': self.data['max_demand'].mean(),
            'max_max_demand': self.data['max_demand'].max()
        }

        # 计算各时段占比
        total = annual['total_consumption']
        if total > 0:
            annual['peak_ratio'] = annual['peak_consumption'] / total * 100
            annual['valley_ratio'] = annual['valley_consumption'] / total * 100
            annual['flat_ratio'] = annual['flat_consumption'] / total * 100

        return annual

    def get_monthly_distribution(self) -> pd.DataFrame:
        """
        获取月度用电分布

        Returns:
            月度数据 DataFrame
        """
        if self.data is None:
            return pd.DataFrame()

        return self.data.copy()

    def export_standardized(self) -> Dict:
        """
        导出标准化格式

        Returns:
            标准化数据字典
        """
        if self.data is None:
            return {}

        return {
            'annual_summary': self.get_annual_summary(),
            'monthly_data': self.data.to_dict(orient='records'),
            'quality_report': self.quality_report,
            'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class LoadCurveProcessor:
    """用电负荷曲线数据处理器"""

    REQUIRED_FIELDS = ['timestamp', 'active_power']

    def __init__(self):
        self.data = None
        self.typical_days = {}

    def load_from_dataframe(
        self,
        df: pd.DataFrame,
        timestamp_col: str = 'timestamp',
        power_col: str = 'active_power'
    ) -> bool:
        """
        从DataFrame加载数据

        Args:
            df: 负荷曲线数据
            timestamp_col: 时间戳列名
            power_col: 功率列名

        Returns:
            加载是否成功
        """
        try:
            self.data = df.copy()

            # 重命名列
            if timestamp_col != 'timestamp':
                self.data.rename(columns={timestamp_col: 'timestamp'}, inplace=True)
            if power_col != 'active_power':
                self.data.rename(columns={power_col: 'active_power'}, inplace=True)

            # 转换时间戳
            if not pd.api.types.is_datetime64_any_dtype(self.data['timestamp']):
                self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])

            # 排序
            self.data = self.data.sort_values('timestamp').reset_index(drop=True)

            # 生成典型日曲线
            self._generate_typical_curves()

            return True

        except Exception as e:
            return False

    def load_from_excel(
        self,
        file_path: str,
        sheet_name: int = 0
    ) -> bool:
        """
        从Excel文件加载数据

        Args:
            file_path: 文件路径
            sheet_name: 工作表名称或索引

        Returns:
            加载是否成功
        """
        try:
            self.data = pd.read_excel(file_path, sheet_name=sheet_name)
            return self.load_from_dataframe(self.data)
        except Exception as e:
            return False

    def _generate_typical_curves(self):
        """生成典型日负荷曲线"""
        if self.data is None or len(self.data) == 0:
            return

        # 提取小时信息
        self.data['date'] = self.data['timestamp'].dt.date
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['day_of_week'] = self.data['timestamp'].dt.dayofweek

        # 区分工作日和休息日
        workday_data = self.data[self.data['day_of_week'] < 5]
        weekend_data = self.data[self.data['day_of_week'] >= 5]

        # 计算各小时平均负荷
        if len(workday_data) > 0:
            workday_hourly = workday_data.groupby('hour')['active_power'].mean()
            self.typical_days['workday'] = workday_hourly.to_dict()

        if len(weekend_data) > 0:
            weekend_hourly = weekend_data.groupby('hour')['active_power'].mean()
            self.typical_days['weekend'] = weekend_hourly.to_dict()

        # 计算月度典型日
        self.data['month'] = self.data['timestamp'].dt.month
        self.typical_days['monthly'] = {}

        for month in range(1, 13):
            month_data = self.data[self.data['month'] == month]
            if len(month_data) > 0:
                monthly_hourly = month_data.groupby('hour')['active_power'].mean()
                self.typical_days['monthly'][month] = monthly_hourly.to_dict()

    def get_hourly_load_curve(self, curve_type: str = 'workday') -> Dict[int, float]:
        """
        获取小时级负荷曲线

        Args:
            curve_type: 曲线类型 ('workday', 'weekend', 或月份1-12)

        Returns:
            小时到负荷的映射
        """
        if curve_type == 'workday':
            return self.typical_days.get('workday', {})
        elif curve_type == 'weekend':
            return self.typical_days.get('weekend', {})
        elif isinstance(curve_type, int) and 1 <= curve_type <= 12:
            return self.typical_days.get('monthly', {}).get(curve_type, {})
        else:
            return {}

    def get_daily_statistics(self) -> pd.DataFrame:
        """
        获取每日统计

        Returns:
            每日统计数据 DataFrame
        """
        if self.data is None:
            return pd.DataFrame()

        daily_stats = self.data.groupby('date').agg({
            'active_power': ['mean', 'max', 'min', 'std']
        }).reset_index()

        daily_stats.columns = ['date', 'avg_power', 'max_power', 'min_power', 'std_power']
        daily_stats['load_factor'] = daily_stats['avg_power'] / daily_stats['max_power']

        return daily_stats

    def get_load_characteristics(self) -> Dict[str, Any]:
        """
        获取负荷特征分析

        Returns:
            负荷特征字典
        """
        if self.data is None or len(self.data) == 0:
            return {}

        daily_stats = self.get_daily_statistics()

        return {
            'annual_consumption': self.data['active_power'].sum() / 4,  # 假设15分钟采集
            'avg_daily_consumption': daily_stats['avg_power'].mean() * 24,
            'max_daily_peak': daily_stats['max_power'].max(),
            'avg_load_factor': daily_stats['load_factor'].mean(),
            'peak_valley_ratio': daily_stats['max_power'].max() / daily_stats['min_power'].replace(0, 1).min(),
            'typical_workday': self.typical_days.get('workday', {}),
            'typical_weekend': self.typical_days.get('weekend', {})
        }

    def export_standardized(self) -> Dict:
        """
        导出标准化格式

        Returns:
            标准化数据字典
        """
        if self.data is None:
            return {}

        return {
            'load_characteristics': self.get_load_characteristics(),
            'daily_statistics': self.get_daily_statistics().to_dict(orient='records'),
            'typical_days': self.typical_days,
            'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class DataStandardizer:
    """数据标准化综合处理器"""

    def __init__(self):
        self.bill_processor = ElectricityBillProcessor()
        self.load_processor = LoadCurveProcessor()

    def process_bill_data(self, data: Any) -> Dict:
        """
        处理电费核查联数据

        Args:
            data: DataFrame或字典列表

        Returns:
            处理结果
        """
        if isinstance(data, pd.DataFrame):
            success = self.bill_processor.load_from_dataframe(data)
        else:
            success = self.bill_processor.load_from_dict(data)

        if success:
            return self.bill_processor.export_standardized()
        else:
            return {'error': self.bill_processor.quality_report.get('error', 'Unknown error')}

    def process_load_curve(self, data: Any, **kwargs) -> Dict:
        """
        处理负荷曲线数据

        Args:
            data: DataFrame或文件路径

        Returns:
            处理结果
        """
        if isinstance(data, pd.DataFrame):
            success = self.load_processor.load_from_dataframe(
                data,
                timestamp_col=kwargs.get('timestamp_col', 'timestamp'),
                power_col=kwargs.get('power_col', 'active_power')
            )
        elif isinstance(data, str):
            success = self.load_processor.load_from_excel(data)
        else:
            return {'error': 'Unsupported data format'}

        if success:
            return self.load_processor.export_standardized()
        else:
            return {'error': 'Failed to load load curve data'}

    def generate_combined_report(self) -> Dict:
        """
        生成综合数据报告

        Returns:
            综合数据报告
        """
        return {
            'electricity_bill': self.bill_processor.get_annual_summary(),
            'load_characteristics': self.load_processor.get_load_characteristics(),
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def validate_data_completeness(
    bill_data: Dict,
    load_data: Dict,
    required_months: int = 12,
    required_days: int = 7
) -> Tuple[bool, List[str]]:
    """
    验证数据完整性

    Args:
        bill_data: 电费数据
        load_data: 负荷曲线数据
        required_months: 要求的月数
        required_days: 要求的天数

    Returns:
        (是否通过, 问题列表)
    """
    issues = []

    # 检查电费数据
    if 'monthly_data' in bill_data:
        if len(bill_data['monthly_data']) < required_months:
            issues.append(
                f"电费数据仅{len(bill_data['monthly_data'])}个月，"
                f"建议至少{required_months}个月"
            )

    # 检查负荷曲线数据
    if 'daily_statistics' in load_data:
        if len(load_data['daily_statistics']) < required_days:
            issues.append(
                f"负荷曲线仅{len(load_data['daily_statistics'])}天，"
                f"建议至少{required_days}天"
            )

    return len(issues) == 0, issues


if __name__ == "__main__":
    # 示例用法
    processor = DataStandardizer()

    # 模拟电费数据
    sample_bill = [
        {'settlement_period': f'2024-{m:02d}', 'peak_consumption': 50000, 'valley_consumption': 30000, 'flat_consumption': 70000, 'max_demand': 800, 'voltage_level': 10, 'price': 0.6}
        for m in range(1, 13)
    ]

    bill_result = processor.process_bill_data(sample_bill)
    print("电费数据处理结果:")
    print(json.dumps(bill_result.get('annual_summary', {}), indent=2, ensure_ascii=False))
