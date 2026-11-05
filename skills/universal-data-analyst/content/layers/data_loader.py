#!/usr/bin/env python3
"""
Data Loader - 多格式数据加载模块

支持的文件格式：
- CSV / TSV (.csv, .tsv, .txt)
- Excel (.xlsx, .xls)
- Parquet (.parquet, .pq)
- JSON (.json)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

import pandas as pd


class DataFormat(Enum):
    """支持的数据格式"""
    CSV = "csv"
    TSV = "tsv"
    EXCEL = "excel"
    PARQUET = "parquet"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class DataLoadResult:
    """数据加载结果"""
    success: bool
    data: Optional[pd.DataFrame] = None
    file_path: str = ""
    format: DataFormat = DataFormat.UNKNOWN
    rows: int = 0
    columns: int = 0
    memory_usage_mb: float = 0.0
    encoding: str = "utf-8"
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class DataLoader:
    """多格式数据加载器"""

    # 常见编码列表，按优先级排序
    ENCODINGS = [
        'utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be',
        'gbk', 'gb2312', 'gb18030',
        'big5', 'big5hkscs',
        'latin1', 'iso-8859-1', 'cp1252',
        'ascii'
    ]

    # CSV 分隔符
    DELIMITERS = [',', '\t', ';', '|', ' ']

    def __init__(self):
        self.last_result: Optional[DataLoadResult] = None

    def detect_format(self, file_path: str) -> DataFormat:
        """检测文件格式"""
        ext = Path(file_path).suffix.lower()

        format_map = {
            '.csv': DataFormat.CSV,
            '.tsv': DataFormat.TSV,
            '.txt': DataFormat.CSV,  # 默认当作 CSV
            '.xlsx': DataFormat.EXCEL,
            '.xls': DataFormat.EXCEL,
            '.parquet': DataFormat.PARQUET,
            '.pq': DataFormat.PARQUET,
            '.json': DataFormat.JSON,
        }

        return format_map.get(ext, DataFormat.UNKNOWN)

    def execute(self, config: Dict[str, Any]) -> DataLoadResult:
        """
        执行数据加载

        Args:
            config: 配置字典，包含 file_path 等参数

        Returns:
            DataLoadResult: 加载结果
        """
        file_path = config.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return DataLoadResult(
                success=False,
                errors=[f"文件不存在: {file_path}"]
            )

        fmt = self.detect_format(file_path)

        try:
            if fmt == DataFormat.CSV:
                return self._load_csv(file_path, config)
            elif fmt == DataFormat.TSV:
                return self._load_csv(file_path, config, delimiter='\t')
            elif fmt == DataFormat.EXCEL:
                return self._load_excel(file_path, config)
            elif fmt == DataFormat.PARQUET:
                return self._load_parquet(file_path, config)
            elif fmt == DataFormat.JSON:
                return self._load_json(file_path, config)
            else:
                return DataLoadResult(
                    success=False,
                    errors=[f"不支持的文件格式: {fmt}"]
                )
        except Exception as e:
            return DataLoadResult(
                success=False,
                file_path=file_path,
                errors=[f"加载失败: {str(e)}"]
            )

    def _load_csv(self, file_path: str, config: Dict, delimiter: str = None) -> DataLoadResult:
        """加载 CSV 文件，支持多种编码和分隔符"""
        errors = []
        warnings = []
        df = None
        used_encoding = None
        used_delimiter = None

        # 自动检测分隔符
        if delimiter is None:
            delimiter = self._detect_delimiter(file_path)

        # 尝试多种编码
        for encoding in self.ENCODINGS:
            try:
                # 尝试读取
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    delimiter=delimiter,
                    engine='c',
                    on_bad_lines='warn',
                    encoding_errors='replace'
                )

                used_encoding = encoding
                used_delimiter = delimiter

                # 如果成功但有替换的字符，给出警告
                if df is not None and df.shape[0] > 0:
                    break

            except UnicodeDecodeError:
                continue
            except Exception as e:
                # 如果 C 引擎失败，尝试 Python 引擎
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        delimiter=delimiter,
                        engine='python',
                        on_bad_lines='skip'
                    )
                    used_encoding = encoding
                    used_delimiter = delimiter
                    warnings.append(f"使用 Python 引擎，跳过格式错误的行")
                    break
                except:
                    continue

        if df is None:
            return DataLoadResult(
                success=False,
                file_path=file_path,
                format=DataFormat.CSV,
                errors=[f"无法解析 CSV 文件，尝试了所有编码: {', '.join(self.ENCODINGS)}"]
            )

        if used_encoding not in ['utf-8', 'utf-8-sig']:
            warnings.append(f"使用了非标准编码: {used_encoding}")

        return self._create_result(df, file_path, DataFormat.CSV, used_encoding, warnings)

    def _detect_delimiter(self, file_path: str) -> str:
        """检测 CSV 分隔符"""
        try:
            # 读取前几行
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                first_lines = [f.readline() for _ in range(3)]

            # 统计各分隔符出现频率
            delimiter_counts = {}
            for delim in self.DELIMITERS:
                counts = [line.count(delim) for line in first_lines]
                if counts and max(counts) > 0:
                    delimiter_counts[delim] = sum(counts) / len(counts)

            if delimiter_counts:
                return max(delimiter_counts, key=delimiter_counts.get)
        except:
            pass

        return ','  # 默认逗号分隔

    def _load_excel(self, file_path: str, config: Dict) -> DataLoadResult:
        """加载 Excel 文件"""
        sheet_name = config.get('sheet_name')
        warnings = []

        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            else:
                # 默认读取第一个 sheet
                df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
        except Exception as e:
            # 回退到 xlrd 引擎（兼容旧格式）
            try:
                df = pd.read_excel(file_path, sheet_name=0, engine='xlrd')
                warnings.append("使用 xlrd 引擎读取")
            except:
                return DataLoadResult(
                    success=False,
                    file_path=file_path,
                    format=DataFormat.EXCEL,
                    errors=[f"Excel 加载失败: {str(e)}"]
                )

        return self._create_result(df, file_path, DataFormat.EXCEL, "utf-8", warnings)

    def _load_parquet(self, file_path: str, config: Dict) -> DataLoadResult:
        """加载 Parquet 文件"""
        try:
            df = pd.read_parquet(file_path)
        except Exception as e:
            return DataLoadResult(
                success=False,
                file_path=file_path,
                format=DataFormat.PARQUET,
                errors=[f"Parquet 加载失败: {str(e)}"]
            )

        return self._create_result(df, file_path, DataFormat.PARQUET, "utf-8", [])

    def _load_json(self, file_path: str, config: Dict) -> DataLoadResult:
        """加载 JSON 文件"""
        warnings = []
        orient = config.get('json_orient', None)

        # 首先尝试读取文件确定格式
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(4096)
                try:
                    sample = json.loads(content)
                    if isinstance(sample, list):
                        orient = 'records'
                    elif isinstance(sample, dict):
                        if 'data' in sample:
                            orient = 'records'
                        else:
                            orient = 'columns'
                except:
                    orient = 'records'
        except:
            pass

        try:
            df = pd.read_json(file_path, orient=orient, encoding='utf-8')
        except Exception as e:
            # 回退：不指定 orient
            try:
                df = pd.read_json(file_path, encoding='utf-8')
                warnings.append("自动检测 JSON 格式")
            except Exception as e2:
                return DataLoadResult(
                    success=False,
                    file_path=file_path,
                    format=DataFormat.JSON,
                    errors=[f"JSON 加载失败: {str(e2)}"]
                )

        return self._create_result(df, file_path, DataFormat.JSON, "utf-8", warnings)

    def _create_result(self, df: pd.DataFrame, file_path: str,
                      fmt: DataFormat, encoding: str,
                      warnings: List[str]) -> DataLoadResult:
        """创建加载结果"""
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

        result = DataLoadResult(
            success=True,
            data=df,
            file_path=file_path,
            format=fmt,
            rows=len(df),
            columns=len(df.columns),
            memory_usage_mb=memory_mb,
            encoding=encoding,
            warnings=warnings
        )

        self.last_result = result
        return result

    def get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取数据基本信息"""
        info = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes': {col: str(df[col].dtype) for col in df.columns},
            'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        info['numeric_columns'] = list(numeric_cols)

        # 缺失值统计
        null_counts = df.isnull().sum()
        info['null_summary'] = {
            'total': null_counts.sum(),
            'by_column': null_counts[null_counts > 0].to_dict()
        }

        return info


def main():
    """测试入口"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python data_loader.py <file_path>")
        sys.exit(1)

    loader = DataLoader()
    result = loader.execute({'file_path': sys.argv[1]})

    if result.success:
        print(f"✅ 加载成功:")
        print(f"   格式: {result.format.value}")
        print(f"   编码: {result.encoding}")
        print(f"   行数: {result.rows:,}")
        print(f"   列数: {result.columns}")
        print(f"   内存: {result.memory_usage_mb:.2f} MB")

        if result.warnings:
            print(f"\n⚠️ 警告:")
            for w in result.warnings:
                print(f"   - {w}")

        print(f"\n前5行预览:")
        print(result.data.head())
    else:
        print(f"❌ 加载失败:")
        for e in result.errors:
            print(f"   - {e}")


if __name__ == '__main__':
    main()
