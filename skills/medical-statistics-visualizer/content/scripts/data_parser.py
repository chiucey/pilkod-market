"""
医学统计 - 数据解析器
功能：解析CSV/Excel/JSON格式数据，自动识别列类型和含义
依赖：pandas, numpy
"""

import pandas as pd
import numpy as np
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class DataParser:
    """数据解析器"""

    # 常用列名映射
    COLUMN_MAPPINGS = {
        'time': ['time', '生存时间', 'follow_up_time', 'survival_time', 'os_time', 'pfs_time', 'dfs_time', 'months', 'days'],
        'event': ['event', 'status', '生存状态', 'outcome', 'death', 'censor', 'dead', 'alive', 'relapse', 'progression'],
        'group': ['group', 'Group', '分组', 'treatment', 'arm', 'cohort', 'type', 'category'],
        'marker': ['marker', 'Marker', '标志物', 'biomarker', 'cea', 'ca19_9', 'ca19-9', 'afp', 'psa', 'value']
    }

    # 常用编码
    EVENT_CODES = {
        'positive': [1, '1', 'yes', 'Yes', 'YES', 'Dead', 'dead', 'Death', 'death', 'Event', 'event', True],
        'negative': [0, '0', 'no', 'No', 'NO', 'Alive', 'alive', 'Censor', 'censor', 'Censored', 'censored', False]
    }

    def __init__(self):
        self.data = None
        self.encoding = None

    def load(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        加载数据文件

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            数据框
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        try:
            if suffix == '.csv':
                self.data = pd.read_csv(file_path, encoding=encoding)
            elif suffix in ['.xlsx', '.xls']:
                self.data = pd.read_excel(file_path)
            elif suffix == '.json':
                with open(file_path, 'r', encoding=encoding) as f:
                    json_data = json.load(f)
                if isinstance(json_data, list):
                    self.data = pd.DataFrame(json_data)
                else:
                    self.data = pd.DataFrame([json_data])
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            self.encoding = encoding
            return self.data

        except UnicodeDecodeError:
            # 尝试其他编码
            for enc in ['gbk', 'gb2312', 'latin1', 'cp1252']:
                try:
                    if suffix == '.csv':
                        self.data = pd.read_csv(file_path, encoding=enc)
                    else:
                        continue
                    self.encoding = enc
                    return self.data
                except:
                    continue
            raise ValueError(f"无法读取文件，请检查编码格式")

    def parse_from_dict(self, data: Dict) -> pd.DataFrame:
        """从字典解析数据"""
        self.data = pd.DataFrame(data)
        return self.data

    def parse_from_string(self, text: str, format_type: str = 'csv') -> pd.DataFrame:
        """
        从文本字符串解析数据

        Args:
            text: CSV格式的文本
            format_type: 'csv' 或 'json'

        Returns:
            数据框
        """
        from io import StringIO

        if format_type == 'csv':
            self.data = pd.read_csv(StringIO(text))
        elif format_type == 'json':
            json_data = json.loads(text)
            if isinstance(json_data, list):
                self.data = pd.DataFrame(json_data)
            else:
                self.data = pd.DataFrame([json_data])
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        return self.data

    def auto_detect_columns(self) -> Dict[str, List[str]]:
        """
        自动识别关键列

        Returns:
            识别的列类型映射
        """
        if self.data is None:
            raise ValueError("请先加载数据")

        detected = {
            'time_col': None,
            'event_col': None,
            'group_col': None,
            'marker_cols': [],
            'outcome_col': None,
            'covariate_cols': []
        }

        columns = [col.lower().strip() for col in self.data.columns]

        # 识别时间列
        for col, aliases in self.COLUMN_MAPPINGS['time']:
            for alias in aliases:
                if alias.lower() in columns:
                    idx = columns.index(alias.lower())
                    detected['time_col'] = self.data.columns[idx]
                    break

        # 识别事件列
        for col, aliases in self.COLUMN_MAPPINGS['event']:
            for alias in aliases:
                if alias.lower() in columns:
                    idx = columns.index(alias.lower())
                    detected['event_col'] = self.data.columns[idx]
                    break

        # 识别分组列
        for col, aliases in self.COLUMN_MAPPINGS['group']:
            for alias in aliases:
                if alias.lower() in columns:
                    idx = columns.index(alias.lower())
                    detected['group_col'] = self.data.columns[idx]
                    break

        # 识别标志物列（数值型列，排除ID等）
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            col_lower = col.lower()
            # 排除ID类列
            if 'id' in col_lower or 'no' in col_lower or 'num' in col_lower:
                continue
            # 排除已识别的列
            if col in [detected['time_col'], detected['event_col']]:
                continue
            detected['marker_cols'].append(col)

        return detected

    def validate_survival_data(self, time_col: str, event_col: str) -> Tuple[bool, List[str]]:
        """
        验证生存数据格式

        Args:
            time_col: 时间列
            event_col: 事件列

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        if time_col not in self.data.columns:
            errors.append(f"时间列 '{time_col}' 不存在")

        if event_col not in self.data.columns:
            errors.append(f"事件列 '{event_col}' 不存在")

        if time_col in self.data.columns:
            time_data = pd.to_numeric(self.data[time_col], errors='coerce')
            if time_data.isna().any():
                n_invalid = time_data.isna().sum()
                errors.append(f"时间列有 {n_invalid} 个非数值数据")

            if (time_data <= 0).any():
                n_invalid = (time_data <= 0).sum()
                errors.append(f"时间列有 {n_invalid} 个非正值")

        if event_col in self.data.columns:
            unique_vals = self.data[event_col].unique()
            # 检查是否为二元变量
            binary_vals = set(str(v) for v in unique_vals) & set('01')
            if len(binary_vals) != 2:
                errors.append(f"事件列不是标准的0/1编码，当前值: {unique_vals}")

        return len(errors) == 0, errors

    def get_column_info(self) -> pd.DataFrame:
        """获取列详细信息"""
        if self.data is None:
            raise ValueError("请先加载数据")

        info = []
        for col in self.data.columns:
            col_info = {
                'column': col,
                'dtype': str(self.data[col].dtype),
                'n_unique': self.data[col].nunique(),
                'n_missing': self.data[col].isna().sum(),
                'missing_pct': f"{(self.data[col].isna().sum() / len(self.data) * 100):.1f}%"
            }

            if pd.api.types.is_numeric_dtype(self.data[col]):
                col_info['min'] = self.data[col].min()
                col_info['max'] = self.data[col].max()
                col_info['mean'] = f"{self.data[col].mean():.2f}"
                col_info['median'] = f"{self.data[col].median():.2f}"
            else:
                col_info['top_values'] = self.data[col].value_counts().head(3).to_dict()

            info.append(col_info)

        return pd.DataFrame(info)

    def sample_data(self, n: int = 10) -> pd.DataFrame:
        """返回样本数据"""
        if self.data is None:
            raise ValueError("请先加载数据")
        return self.data.head(n)

    def to_csv(self, output_path: str, **kwargs) -> None:
        """导出为CSV"""
        if self.data is None:
            raise ValueError("请先加载数据")
        self.data.to_csv(output_path, **kwargs)

    def to_excel(self, output_path: str, **kwargs) -> None:
        """导出为Excel"""
        if self.data is None:
            raise ValueError("请先加载数据")
        self.data.to_excel(output_path, **kwargs)

    def to_json(self, output_path: str, **kwargs) -> None:
        """导出为JSON"""
        if self.data is None:
            raise ValueError("请先加载数据")
        self.data.to_json(output_path, **kwargs)


def demo():
    """演示函数"""
    import os
    os.makedirs('/workspace/temp-skills/medical-statistics-visualizer/assets', exist_ok=True)

    # 创建示例数据
    np.random.seed(42)
    n = 100

    demo_data = pd.DataFrame({
        'patient_id': range(1, n + 1),
        'group': np.random.choice(['手术组', '化疗组'], n),
        'time': np.random.exponential(20, n) + np.random.normal(0, 2, n),
        'event': np.random.binomial(1, 0.6, n),
        'age': np.random.normal(55, 10, n),
        'stage': np.random.choice([1, 2, 3], n),
        'CEA': np.random.lognormal(2, 0.5, n),
        'CA19_9': np.random.lognormal(3, 0.6, n)
    })
    demo_data['time'] = demo_data['time'].clip(lower=0.5)

    # 保存测试数据
    test_file = '/workspace/temp-skills/medical-statistics-visualizer/assets/demo_survival.csv'
    demo_data.to_csv(test_file, index=False)

    # 解析数据
    parser = DataParser()
    data = parser.load(test_file)

    print("数据信息:")
    print(f"行数: {len(data)}, 列数: {len(data.columns)}")

    # 自动识别列
    detected = parser.auto_detect_columns()
    print("\n识别的列类型:")
    for k, v in detected.items():
        print(f"  {k}: {v}")

    # 列详细信息
    col_info = parser.get_column_info()
    print("\n列详细信息:")
    print(col_info)


if __name__ == '__main__':
    demo()
