#!/usr/bin/env python3
"""
Data Validator - 数据质量校验模块

检测并报告：
- 缺失值
- 异常值
- 重复行
- 格式问题
- 数据类型不一致
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import Counter

import pandas as pd
import numpy as np


class IssueSeverity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"  # 严重，影响分析
    WARNING = "warning"   # 警告，可能影响
    INFO = "info"         # 提示，供参考


@dataclass
class DataIssue:
    """数据问题"""
    severity: IssueSeverity
    issue_type: str        # missing_values, outliers, duplicates, etc.
    column: str            # 受影响的列名，"整表"表示整表问题
    description: str       # 问题描述
    affected_rows: int     # 受影响的行数
    affected_percent: float  # 占比
    details: Dict = field(default_factory=dict)  # 额外详情
    cleaning_action: Dict = field(default_factory=dict)  # 清洗建议


@dataclass
class ValidationReport:
    """数据质量报告"""
    overall_score: float     # 质量评分 0-100
    total_rows: int
    total_columns: int
    issues: List[DataIssue]
    cleaning_summary: Dict

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'overall_score': self.overall_score,
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'issues': [
                {
                    'severity': i.severity.value,
                    'issue_type': i.issue_type,
                    'column': i.column,
                    'description': i.description,
                    'affected_rows': i.affected_rows,
                    'affected_percent': i.affected_percent,
                    'details': i.details,
                    'cleaning_action': i.cleaning_action
                }
                for i in self.issues
            ],
            'cleaning_summary': self.cleaning_summary
        }

    def get_cleaning_summary(self) -> Dict:
        """获取清洗摘要"""
        return self.cleaning_summary

    def generate_cleaning_report(self) -> str:
        """生成清洗报告"""
        lines = [
            "=" * 60,
            "数据清洗建议报告",
            "=" * 60,
            f"\n整体质量评分: {self.overall_score:.1f}/100",
            f"数据规模: {self.total_rows:,} 行 × {self.total_columns} 列",
            f"发现问题: {len(self.issues)} 个",
            ""
        ]

        if not self.issues:
            lines.append("✅ 未检测到明显的数据质量问题")
            return "\n".join(lines)

        # 按严重程度分组
        critical = [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
        warnings = [i for i in self.issues if i.severity == IssueSeverity.WARNING]

        if critical:
            lines.append(f"\n🔴 严重问题 ({len(critical)} 个):")
            for i in critical:
                lines.append(f"  - [{i.column}] {i.description}")
                lines.append(f"    影响: {i.affected_rows:,} 行 ({i.affected_percent:.1f}%)")
                if i.cleaning_action:
                    lines.append(f"    处理: {i.cleaning_action.get('description', '需人工审核')}")
                lines.append("")

        if warnings:
            lines.append(f"\n🟡 警告问题 ({len(warnings)} 个):")
            for i in warnings:
                lines.append(f"  - [{i.column}] {i.description}")
                lines.append(f"    影响: {i.affected_rows:,} 行 ({i.affected_percent:.1f}%)")
                lines.append("")

        lines.append("\n" + "=" * 60)
        lines.append("清洗操作摘要")
        lines.append("=" * 60)
        for action, count in self.cleaning_summary.items():
            if count > 0:
                lines.append(f"  - {action}: {count}")

        return "\n".join(lines)


class DataValidator:
    """数据质量校验器"""

    # 异常值检测的 Z-score 阈值
    ZSCORE_THRESHOLD = 3.0

    # 缺失率警告阈值
    MISSING_RATE_WARNING = 0.05  # 5%
    MISSING_RATE_CRITICAL = 0.20  # 20%

    def __init__(self):
        self.last_report: Optional[ValidationReport] = None

    def execute(self, df: pd.DataFrame) -> ValidationReport:
        """
        执行数据质量校验

        Args:
            df: 要校验的 DataFrame

        Returns:
            ValidationReport: 校验报告
        """
        issues = []

        # 1. 检查缺失值
        issues.extend(self._check_missing_values(df))

        # 2. 检查重复行
        issues.extend(self._check_duplicates(df))

        # 3. 检查异常值
        issues.extend(self._check_outliers(df))

        # 4. 检查数据类型
        issues.extend(self._check_data_types(df))

        # 5. 检查字符串格式
        issues.extend(self._check_string_format(df))

        # 6. 计算整体评分
        overall_score = self._calculate_score(len(df), issues)

        # 7. 生成清洗摘要
        cleaning_summary = self._generate_cleaning_summary(df, issues)

        report = ValidationReport(
            overall_score=overall_score,
            total_rows=len(df),
            total_columns=len(df.columns),
            issues=issues,
            cleaning_summary=cleaning_summary
        )

        self.last_report = report
        return report

    def _check_missing_values(self, df: pd.DataFrame) -> List[DataIssue]:
        """检查缺失值"""
        issues = []

        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_rate = null_count / len(df)

            if null_rate >= self.MISSING_RATE_CRITICAL:
                severity = IssueSeverity.CRITICAL
                action_desc = "建议删除此列或使用特殊值填充"
            elif null_rate >= self.MISSING_RATE_WARNING:
                severity = IssueSeverity.WARNING
                action_desc = "建议填充缺失值"
            else:
                severity = IssueSeverity.INFO
                action_desc = "可选填充或保留"

            if null_count > 0:
                issues.append(DataIssue(
                    severity=severity,
                    issue_type="missing_values",
                    column=col,
                    description=f"存在 {null_count:,} 个缺失值",
                    affected_rows=null_count,
                    affected_percent=null_rate * 100,
                    details={
                        'null_count': int(null_count),
                        'null_rate': float(null_rate)
                    },
                    cleaning_action={
                        'description': action_desc,
                        'recommended_method': 'fillna' if null_rate < 0.3 else 'drop_or_review'
                    }
                ))

        return issues

    def _check_duplicates(self, df: pd.DataFrame) -> List[DataIssue]:
        """检查重复行"""
        issues = []

        dup_count = df.duplicated().sum()
        dup_rate = dup_count / len(df)

        if dup_count > 0:
            severity = IssueSeverity.WARNING if dup_rate < 0.1 else IssueSeverity.CRITICAL

            issues.append(DataIssue(
                severity=severity,
                issue_type="duplicates",
                column="整表",
                description=f"存在 {dup_count:,} 个重复行",
                affected_rows=dup_count,
                affected_percent=dup_rate * 100,
                details={
                    'duplicate_count': int(dup_count),
                    'duplicate_rate': float(dup_rate)
                },
                cleaning_action={
                    'description': '建议删除重复行' if dup_count > 0 else '无需处理',
                    'recommended_method': 'drop_duplicates'
                }
            ))

        return issues

    def _check_outliers(self, df: pd.DataFrame) -> List[DataIssue]:
        """检查异常值"""
        issues = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            data = df[col].dropna()

            if len(data) < 3:
                continue

            # Z-score 方法
            mean = data.mean()
            std = data.std()

            if std > 0:
                z_scores = np.abs((data - mean) / std)
                outliers = (z_scores > self.ZSCORE_THRESHOLD).sum()
                outlier_rate = outliers / len(data)

                if outlier_rate > 0.05:  # 超过5%为异常
                    severity = IssueSeverity.WARNING
                    if outlier_rate > 0.15:
                        severity = IssueSeverity.CRITICAL

                    # 计算异常值范围
                    lower_bound = mean - self.ZSCORE_THRESHOLD * std
                    upper_bound = mean + self.ZSCORE_THRESHOLD * std

                    issues.append(DataIssue(
                        severity=severity,
                        issue_type="outliers",
                        column=col,
                        description=f"存在 {outliers:,} 个异常值 ({outlier_rate*100:.1f}%)",
                        affected_rows=outliers,
                        affected_percent=outlier_rate * 100,
                        details={
                            'outlier_count': int(outliers),
                            'outlier_rate': float(outlier_rate),
                            'lower_bound': float(lower_bound),
                            'upper_bound': float(upper_bound),
                            'mean': float(mean),
                            'std': float(std)
                        },
                        cleaning_action={
                            'description': '建议审核异常值来源',
                            'recommended_method': 'investigate_or_clip'
                        }
                    ))

        return issues

    def _check_data_types(self, df: pd.DataFrame) -> List[DataIssue]:
        """检查数据类型问题"""
        issues = []

        # 检查 ID 列是否被误识别为数值
        id_patterns = ['id', 'no', 'code', 'num', 'key']

        for col in df.columns:
            if df[col].dtype == 'int64' or df[col].dtype == 'float64':
                col_lower = col.lower()

                # 可能是 ID 但被识别为数值
                if any(p in col_lower for p in id_patterns):
                    unique_ratio = df[col].nunique() / len(df)
                    if unique_ratio > 0.9:  # 高基数
                        issues.append(DataIssue(
                            severity=IssueSeverity.INFO,
                            issue_type="data_type",
                            column=col,
                            description=f"ID列可能被误识别为数值类型",
                            affected_rows=0,
                            affected_percent=0,
                            details={
                                'current_dtype': str(df[col].dtype),
                                'unique_ratio': float(unique_ratio)
                            },
                            cleaning_action={
                                'description': '建议转换为字符串类型',
                                'recommended_method': 'astype(str)'
                            }
                        ))

        return issues

    def _check_string_format(self, df: pd.DataFrame) -> List[DataIssue]:
        """检查字符串格式问题"""
        issues = []

        # 检查可能的日期格式
        date_patterns = ['date', 'time', 'timestamp', 'created', 'updated']
        object_cols = df.select_dtypes(include=['object']).columns

        for col in object_cols:
            col_lower = col.lower()

            if any(p in col_lower for p in date_patterns):
                # 尝试解析日期
                try:
                    parsed = pd.to_datetime(df[col].dropna(), errors='coerce')
                    parsed_rate = parsed.notna().sum() / df[col].notna().sum()

                    if 0.5 < parsed_rate < 1.0:  # 部分能解析
                        issues.append(DataIssue(
                            severity=IssueSeverity.WARNING,
                            issue_type="format",
                            column=col,
                            description=f"存在 {int((1-parsed_rate)*df[col].notna().sum())} 个无效日期格式",
                            affected_rows=int((1-parsed_rate)*df[col].notna().sum()),
                            affected_percent=(1-parsed_rate) * 100,
                            cleaning_action={
                                'description': '建议统一日期格式',
                                'recommended_method': 'pd.to_datetime'
                            }
                        ))
                except:
                    pass

            # 检查前后空格
            if df[col].dtype == 'object':
                try:
                    has_leading_space = df[col].astype(str).str.startswith(' ').sum()
                    has_trailing_space = df[col].astype(str).str.endswith(' ').sum()

                    if has_leading_space > 0 or has_trailing_space > 0:
                        total_space_issues = has_leading_space + has_trailing_space
                        issues.append(DataIssue(
                            severity=IssueSeverity.INFO,
                            issue_type="format",
                            column=col,
                            description=f"存在 {total_space_issues:,} 个前后空格",
                            affected_rows=total_space_issues,
                            affected_percent=total_space_issues / len(df) * 100,
                            cleaning_action={
                                'description': '建议去除前后空格',
                                'recommended_method': 'str.strip'
                            }
                        ))
                except:
                    pass

        return issues

    def _calculate_score(self, total_rows: int, issues: List[DataIssue]) -> float:
        """计算质量评分"""
        if total_rows == 0:
            return 0.0

        # 基础分
        score = 100.0

        # 扣除各项问题
        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                # 每个严重问题扣 10-30 分
                score -= min(30, issue.affected_percent * 0.5)
            elif issue.severity == IssueSeverity.WARNING:
                # 每个警告扣 2-10 分
                score -= min(10, issue.affected_percent * 0.2)
            else:
                # 每个提示扣 0.5-2 分
                score -= min(2, issue.affected_percent * 0.05)

        return max(0.0, min(100.0, score))

    def _generate_cleaning_summary(self, df: pd.DataFrame, issues: List[DataIssue]) -> Dict:
        """生成清洗摘要"""
        summary = {
            'recommended_deletions': 0,
            'recommended_fills': 0,
            'recommended_reviews': 0,
            'recommended_transforms': 0
        }

        for issue in issues:
            if issue.cleaning_action.get('recommended_method') == 'drop_or_review':
                summary['recommended_reviews'] += issue.affected_rows
            elif issue.cleaning_action.get('recommended_method') == 'fillna':
                summary['recommended_fills'] += issue.affected_rows
            elif issue.cleaning_action.get('recommended_method') in ['drop_duplicates']:
                summary['recommended_deletions'] += issue.affected_rows
            elif issue.cleaning_action.get('recommended_method') in ['investigate_or_clip', 'astype(str)']:
                summary['recommended_transforms'] += issue.affected_rows

        return summary


def main():
    """测试入口"""
    import sys

    if len(sys.argv) < 2:
        # 创建测试数据
        df = pd.DataFrame({
            'id': range(1000),
            'name': ['user_' + str(i) for i in range(1000)],
            'age': [25, 30, 35, 150, 28, 29] * 166 + [25, 30, 35, 150, 28],  # 含异常值
            'salary': [5000, 6000, 7000, None, 5500, 6200] * 166 + [5000, 6000],
            'date': pd.date_range('2024-01-01', periods=1000)
        })
        # 添加重复行
        df = pd.concat([df, df.head(50)], ignore_index=True)

        print("使用测试数据")
    else:
        from data_loader import DataLoader
        loader = DataLoader()
        result = loader.execute({'file_path': sys.argv[1]})
        if not result.success:
            print(f"加载失败: {result.errors}")
            sys.exit(1)
        df = result.data

    validator = DataValidator()
    report = validator.execute(df)

    print(f"\n数据质量报告")
    print(f"=" * 50)
    print(f"评分: {report.overall_score:.1f}/100")
    print(f"规模: {report.total_rows:,} 行 × {report.total_columns} 列")
    print(f"问题: {len(report.issues)} 个")

    print(f"\n{report.generate_cleaning_report()}")


if __name__ == '__main__':
    main()
