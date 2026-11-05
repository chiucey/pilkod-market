#!/usr/bin/env python3
"""
数据验证脚本
Data Validation Module

验证数据完整性和合理性
"""

import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')


class DataValidator:
    """数据验证器"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.validation_results = {}

    def validate_population_data(self, data: Dict) -> bool:
        """验证人口数据"""
        required_fields = ['population', 'density', 'age_structure', 'income_distribution']

        for field in required_fields:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
                return False

        # 合理性检查
        if data['population'] <= 0:
            self.errors.append("Population must be positive")
            return False

        if data['density'] <= 0:
            self.errors.append("Density must be positive")
            return False

        # 年龄结构比例和
        age_total = sum(data['age_structure'].values())
        if not 0.99 <= age_total <= 1.01:
            self.warnings.append("Age structure percentages do not sum to 100%")

        return True

    def validate_competition_data(self, competitors: pd.DataFrame) -> bool:
        """验证竞品数据"""
        required_cols = ['name', 'lat', 'lon', 'rating', 'reviews']

        for col in required_cols:
            if col not in competitors.columns:
                self.errors.append(f"Missing column: {col}")
                return False

        # 评分范围检查
        if not competitors['rating'].between(0, 5).all():
            self.warnings.append("Some ratings are outside 0-5 range")

        # 评论数非负
        if (competitors['reviews'] < 0).any():
            self.errors.append("Negative review counts found")
            return False

        return True

    def validate_cost_data(self, cost_data: Dict) -> bool:
        """验证成本数据"""
        required_fields = ['rent_per_sqm', 'staff_salary', 'avg_utilities', 'marketing']

        for field in required_fields:
            if field not in cost_data:
                self.errors.append(f"Missing cost field: {field}")
                return False

        # 成本应非负
        for field in required_fields:
            if cost_data[field] < 0:
                self.errors.append(f"{field} cannot be negative")
                return False

        return True

    def validate_location_coordinates(self, lat: float, lon: float) -> bool:
        """验证坐标合理性（中国大陆范围）"""
        # 中国大陆大致范围
        CHINA_BOUNDS = {
            'lat_min': 18,
            'lat_max': 54,
            'lon_min': 73,
            'lon_max': 135
        }

        if not CHINA_BOUNDS['lat_min'] <= lat <= CHINA_BOUNDS['lat_max']:
            self.errors.append(f"Latitude {lat} out of valid range")
            return False

        if not CHINA_BOUNDS['lon_min'] <= lon <= CHINA_BOUNDS['lon_max']:
            self.errors.append(f"Longitude {lon} out of valid range")
            return False

        return True

    def validate_sales_assumptions(self, assumptions: Dict) -> bool:
        """验证销售假设"""
        required_assumptions = ['conversion_rate', 'aov', 'footfall']

        for field in required_assumptions:
            if field not in assumptions:
                self.errors.append(f"Missing assumption: {field}")
                return False

        # 转化率应在合理范围
        if not 0 < assumptions['conversion_rate'] < 1:
            self.warnings.append(f"Conversion rate {assumptions['conversion_rate']} seems unusual")

        # 客单价应正数
        if assumptions['aov'] <= 0:
            self.errors.append("AOV must be positive")
            return False

        return True

    def check_data_freshness(self, update_date: str, max_age_days: int = 365) -> bool:
        """检查数据时效性"""
        try:
            update = datetime.strptime(update_date, '%Y-%m-%d')
            age = (datetime.now() - update).days

            if age > max_age_days:
                self.warnings.append(f"Data is {age} days old (threshold: {max_age_days})")
                return False

            return True
        except ValueError:
            self.errors.append(f"Invalid date format: {update_date}")
            return False

    def generate_validation_report(self) -> Dict:
        """生成验证报告"""
        return {
            'is_valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_time': datetime.now().isoformat()
        }


def detect_outliers_iqr(data: pd.Series, multiplier: float = 1.5) -> Tuple[np.ndarray, Dict]:
    """
    使用IQR方法检测异常值

    Returns:
        Tuple: (outlier_mask, stats_dict)
    """
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    outlier_mask = (data < lower_bound) | (data > upper_bound)

    stats = {
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'outlier_count': outlier_mask.sum(),
        'outlier_percentage': outlier_mask.mean() * 100
    }

    return outlier_mask, stats


def handle_missing_values(df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
    """
    处理缺失值

    Strategies:
        - 'mean': 数值列用均值填充
        - 'median': 数值列用中位数填充
        - 'mode': 分类列用众数填充
        - 'drop': 删除缺失行
        - 'auto': 根据数据类型自动选择
    """
    df_clean = df.copy()

    for col in df_clean.columns:
        missing_pct = df_clean[col].isna().mean()

        if missing_pct == 0:
            continue

        if df_clean[col].dtype in ['int64', 'float64']:
            if strategy == 'auto':
                fill_value = df_clean[col].median() if missing_pct > 0.1 else df_clean[col].mean()
            elif strategy == 'mean':
                fill_value = df_clean[col].mean()
            elif strategy == 'median':
                fill_value = df_clean[col].median()
            elif strategy == 'drop':
                df_clean = df_clean.dropna(subset=[col])
                continue
            else:
                fill_value = 0

            df_clean[col] = df_clean[col].fillna(fill_value)

        else:
            if strategy in ['auto', 'drop']:
                if missing_pct > 0.5:
                    df_clean[col] = df_clean[col].fillna('Unknown')
                else:
                    df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown')

    return df_clean


def standardize_data(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    标准化数据（Z-score）

    (x - mean) / std
    """
    df_std = df.copy()

    for col in columns:
        if col in df_std.columns:
            mean = df_std[col].mean()
            std = df_std[col].std()
            if std > 0:
                df_std[col] = (df_std[col] - mean) / std

    return df_std


def normalize_data(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    归一化数据（Min-Max）

    (x - min) / (max - min)
    """
    df_norm = df.copy()

    for col in columns:
        if col in df_norm.columns:
            min_val = df_norm[col].min()
            max_val = df_norm[col].max()
            if max_val > min_val:
                df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)

    return df_norm


class AssumptionImpactAnalyzer:
    """假设影响分析器"""

    @staticmethod
    def calculate_impact_level(assumption_value: float,
                              true_value: float,
                              sensitivity: float = 0.2) -> str:
        """
        计算假设对结果的影响程度

        Parameters:
            assumption_value: 假设值
            true_value: 实际值
            sensitivity: 敏感度阈值

        Returns:
            'high', 'medium', 'low'
        """
        if true_value == 0:
            return 'high' if assumption_value != 0 else 'low'

        deviation = abs(assumption_value - true_value) / abs(true_value)

        if deviation > sensitivity * 2:
            return 'high'
        elif deviation > sensitivity:
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def generate_assumption_report(assumptions: Dict,
                                   actuals: Dict,
                                   model_output: Any) -> Dict:
        """生成假设影响报告"""
        impacts = []

        for key, assumption_value in assumptions.items():
            actual_value = actuals.get(key, assumption_value)
            impact = AssumptionImpactAnalyzer.calculate_impact_level(
                assumption_value, actual_value
            )

            impacts.append({
                'assumption': key,
                'assumed_value': assumption_value,
                'actual_value': actual_value,
                'impact_level': impact,
                'deviation_pct': abs(assumption_value - actual_value) / actual_value * 100
                           if actual_value != 0 else 0
            })

        return {
            'impacts': impacts,
            'high_impact_count': sum(1 for i in impacts if i['impact_level'] == 'high'),
            'overall_reliability': 'Low' if sum(1 for i in impacts if i['impact_level'] == 'high') > 3 else 'Medium'
                                  if sum(1 for i in impacts if i['impact_level'] == 'high') > 1 else 'High'
        }


# =============================================================================
# 使用示例
# =============================================================================

if __name__ == '__main__':
    # 示例使用
    validator = DataValidator()

    # 验证人口数据
    pop_data = {
        'population': 500000,
        'density': 15000,
        'age_structure': {'0-14': 0.18, '15-64': 0.72, '65+': 0.10},
        'income_distribution': {}
    }

    validator.validate_population_data(pop_data)
    print(validator.generate_validation_report())

    # 检测异常值
    sample_data = pd.Series([100, 105, 110, 200, 95, 102, 500, 98, 103])
    outliers, stats = detect_outliers_iqr(sample_data)
    print(f"Outlier indices: {outliers[outliers].index.tolist()}")
    print(f"Stats: {stats}")
