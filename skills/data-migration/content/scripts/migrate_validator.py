#!/usr/bin/env python3
"""
数据迁移验证器
用于验证源端和目标端数据一致性
"""

import pandas as pd
import sys
from typing import Dict, List, Any


class MigrationValidator:
    def __init__(self, source_data, target_data, key_fields: List[str] = None):
        self.source = source_data
        self.target = target_data
        self.key_fields = key_fields or []

    def validate_count(self) -> Dict[str, Any]:
        """验证数据总量"""
        source_count = len(self.source)
        target_count = len(self.target)

        return {
            "type": "count",
            "source_count": source_count,
            "target_count": target_count,
            "match": source_count == target_count,
            "difference": abs(source_count - target_count)
        }

    def validate_columns(self) -> Dict[str, Any]:
        """验证字段完整性"""
        source_cols = set(self.source.columns)
        target_cols = set(self.target.columns)

        return {
            "type": "columns",
            "source_columns": list(source_cols),
            "target_columns": list(target_cols),
            "missing_in_target": list(source_cols - target_cols),
            "extra_in_target": list(target_cols - source_cols),
            "match": source_cols == target_cols
        }

    def validate_sample(self, sample_size: int = 10) -> Dict[str, Any]:
        """抽样验证数据内容"""
        source_sample = self.source.head(sample_size)
        target_sample = self.target.head(sample_size)

        mismatches = []
        for idx in range(min(len(source_sample), len(target_sample))):
            s_row = source_sample.iloc[idx].to_dict()
            t_row = target_sample.iloc[idx].to_dict()

            row_diff = {}
            for key in s_row:
                if key in t_row and s_row[key] != t_row[key]:
                    row_diff[key] = {"source": s_row[key], "target": t_row[key]}

            if row_diff:
                mismatches.append({"row": idx, "differences": row_diff})

        return {
            "type": "sample",
            "sample_size": sample_size,
            "mismatches": mismatches,
            "match_rate": 1 - len(mismatches) / sample_size if sample_size > 0 else 1
        }

    def validate_nulls(self) -> Dict[str, Any]:
        """验证空值情况"""
        source_nulls = self.source.isnull().sum().to_dict()
        target_nulls = self.target.isnull().sum().to_dict()

        return {
            "type": "nulls",
            "source_nulls": source_nulls,
            "target_nulls": target_nulls,
            "match": source_nulls == target_nulls
        }

    def generate_report(self) -> str:
        """生成完整验证报告"""
        results = []
        results.append("=" * 60)
        results.append("数据迁移验证报告")
        results.append("=" * 60)

        # 数量验证
        count_result = self.validate_count()
        results.append(f"\n1. 数据总量验证:")
        results.append(f"   源端数据: {count_result['source_count']}")
        results.append(f"   目标端数据: {count_result['target_count']}")
        results.append(f"   状态: {'✓ 通过' if count_result['match'] else '✗ 失败'}")

        # 字段验证
        col_result = self.validate_columns()
        results.append(f"\n2. 字段完整性验证:")
        results.append(f"   源端字段: {len(col_result['source_columns'])}")
        results.append(f"   目标端字段: {len(col_result['target_columns'])}")
        if col_result['missing_in_target']:
            results.append(f"   缺失字段: {col_result['missing_in_target']}")
        results.append(f"   状态: {'✓ 通过' if col_result['match'] else '✗ 失败'}")

        # 抽样验证
        sample_result = self.validate_sample()
        results.append(f"\n3. 数据内容抽样验证:")
        results.append(f"   抽样数量: {sample_result['sample_size']}")
        results.append(f"   不匹配数: {len(sample_result['mismatches'])}")
        results.append(f"   匹配率: {sample_result['match_rate']:.2%}")

        # 空值验证
        null_result = self.validate_nulls()
        results.append(f"\n4. 空值验证:")
        results.append(f"   源端空值: {sum(null_result['source_nulls'].values())}")
        results.append(f"   目标端空值: {sum(null_result['target_nulls'].values())}")

        results.append("\n" + "=" * 60)

        return "\n".join(results)


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python migrate_validator.py <source.csv> <target.csv>")
        sys.exit(1)

    source_path = sys.argv[1]
    target_path = sys.argv[2]

    print("正在加载数据...")
    source = pd.read_csv(source_path)
    target = pd.read_csv(target_path)

    validator = MigrationValidator(source, target)
    print(validator.generate_report())


if __name__ == "__main__":
    main()
