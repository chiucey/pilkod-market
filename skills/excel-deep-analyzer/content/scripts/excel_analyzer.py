#!/usr/bin/env python3
"""
Excel Deep Analyzer - 核心分析模块
用于深度分析Excel表格，发现问题并进行根因分析
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


@dataclass
class DataQualityIssue:
    """数据质量问题"""
    issue_id: str
    issue_type: str
    field: str
    description: str
    record_count: int
    percentage: float
    severity: str  # critical, high, medium, low
    sample_records: List[Dict] = field(default_factory=list)
    suggestion: str = ""


@dataclass
class AnomalyRecord:
    """异常记录"""
    record_index: int
    field: str
    value: Any
    expected_range: Tuple[Any, Any]
    anomaly_type: str
    z_score: float = 0.0
    iqr_factor: float = 0.0


@dataclass
class RootCauseFinding:
    """根因发现"""
    problem: str
    possible_causes: List[str]
    evidence: Dict[str, Any]
    primary_cause: str
    confidence: str  # high, medium, low
    recommendation: str


class ExcelDeepAnalyzer:
    """Excel深度分析器"""

    def __init__(self, file_path: str, sheet_name: Optional[str] = None):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.quality_issues: List[DataQualityIssue] = []
        self.anomalies: List[AnomalyRecord] = []
        self.root_causes: List[RootCauseFinding] = []

        self._load_data()

    def _load_data(self):
        """加载Excel数据"""
        try:
            if self.file_path.suffix.lower() == '.csv':
                self.df = pd.read_csv(self.file_path, encoding='utf-8-sig')
            else:
                self.df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)

            self.metadata = {
                'file_name': self.file_path.name,
                'file_size': self.file_path.stat().st_size,
                'row_count': len(self.df),
                'column_count': len(self.df.columns),
                'sheet_name': self.sheet_name or 'default'
            }
            print(f"成功加载数据: {self.metadata['row_count']}行 x {self.metadata['column_count']}列")

        except Exception as e:
            raise Exception(f"数据加载失败: {str(e)}")

    def full_analysis(self) -> str:
        """执行完整分析流程"""
        print("\n" + "="*60)
        print("开始Excel深度分析")
        print("="*60)

        # 1. 数据结构分析
        print("\n[1/6] 分析数据结构...")
        structure_report = self._analyze_structure()

        # 2. 数据质量检查
        print("[2/6] 检查数据质量...")
        self._check_data_quality()

        # 3. 统计分析
        print("[3/6] 执行统计分析...")
        stats_report = self._statistical_analysis()

        # 4. 异常检测
        print("[4/6] 检测异常值...")
        self._detect_anomalies()

        # 5. 问题诊断
        print("[5/6] 诊断问题...")
        self._diagnose_problems()

        # 6. 根因分析
        print("[6/6] 分析根因...")
        self._root_cause_analysis()

        # 生成报告
        report = self._generate_report(structure_report, stats_report)

        print("\n分析完成!")
        return report

    def _analyze_structure(self) -> Dict[str, Any]:
        """分析数据结构"""
        report = {
            'columns': [],
            'dtypes': {},
            'memory_usage': 0
        }

        for col in self.df.columns:
            col_info = {
                'name': str(col),
                'dtype': str(self.df[col].dtype),
                'unique_count': self.df[col].nunique(),
                'null_count': self.df[col].isnull().sum(),
                'sample_values': self.df[col].dropna().head(3).tolist()
            }
            report['columns'].append(col_info)
            report['dtypes'][str(col)] = str(self.df[col].dtype)

        report['memory_usage'] = self.df.memory_usage(deep=True).sum()

        return report

    def _check_data_quality(self):
        """检查数据质量"""
        issue_counter = 1

        # 检查缺失值
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_rate = missing_count / len(self.df) * 100

            if missing_rate > 0:
                severity = 'critical' if missing_rate > 50 else 'high' if missing_rate > 20 else 'medium' if missing_rate > 5 else 'low'

                samples = self.df[self.df[col].isnull()].head(3).to_dict('records')
                samples = [{'row': i+1, 'value': None} for i in self.df[self.df[col].isnull()].head(3).index.tolist()]

                self.quality_issues.append(DataQualityIssue(
                    issue_id=f"Q{issue_counter:03d}",
                    issue_type="缺失值",
                    field=str(col),
                    description=f"该字段存在 {missing_count} 个缺失值，缺失率为 {missing_rate:.2f}%",
                    record_count=missing_count,
                    percentage=missing_rate,
                    severity=severity,
                    sample_records=samples,
                    suggestion=f"建议: 填充缺失值/标记为'未知'/删除该字段(如果非关键)"
                ))
                issue_counter += 1

        # 检查重复行
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_rate = duplicate_count / len(self.df) * 100
            self.quality_issues.append(DataQualityIssue(
                issue_id=f"Q{issue_counter:03d}",
                issue_type="重复行",
                field="全表",
                description=f"发现 {duplicate_count} 条重复记录，重复率为 {duplicate_rate:.2f}%",
                record_count=duplicate_count,
                percentage=duplicate_rate,
                severity='medium' if duplicate_rate < 5 else 'high',
                suggestion="建议: 检查是否为数据导入错误，删除重复记录"
            ))
            issue_counter += 1

        # 检查格式异常
        for col in self.df.columns:
            # 日期格式检查
            if 'date' in col.lower() or '日期' in str(col):
                date_errors = 0
                for idx, val in self.df[col].items():
                    if pd.notna(val):
                        try:
                            pd.to_datetime(val)
                        except:
                            date_errors += 1

                if date_errors > 0:
                    self.quality_issues.append(DataQualityIssue(
                        issue_id=f"Q{issue_counter:03d}",
                        issue_type="日期格式异常",
                        field=str(col),
                        description=f"该日期字段存在 {date_errors} 个格式异常值",
                        record_count=date_errors,
                        percentage=date_errors / len(self.df) * 100,
                        severity='high',
                        suggestion="建议: 统一日期格式，处理异常日期"
                    ))
                    issue_counter += 1

            # 数值字段负值检查
            if pd.api.types.is_numeric_dtype(self.df[col]):
                negative_count = (self.df[col] < 0).sum()
                if negative_count > 0:
                    # 数值字段默认不应有负值
                    self.quality_issues.append(DataQualityIssue(
                        issue_id=f"Q{issue_counter:03d}",
                        issue_type="负值异常",
                        field=str(col),
                        description=f"该数值字段存在 {negative_count} 个负值",
                        record_count=negative_count,
                        percentage=negative_count / len(self.df) * 100,
                        severity='medium',
                        suggestion="建议: 检查是否为数据录入错误或业务逻辑允许"
                    ))
                    issue_counter += 1

        # 检查数据类型不一致
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                mixed_types = self._check_mixed_types(self.df[col])
                if mixed_types:
                    self.quality_issues.append(DataQualityIssue(
                        issue_id=f"Q{issue_counter:03d}",
                        issue_type="数据类型混合",
                        field=str(col),
                        description=f"该文本字段包含多种数据类型: {', '.join(mixed_types)}",
                        record_count=len(mixed_types),
                        percentage=len(mixed_types) / len(self.df) * 100,
                        severity='low',
                        suggestion="建议: 统一数据格式，确保类型一致"
                    ))
                    issue_counter += 1

    def _check_mixed_types(self, series: pd.Series) -> List[str]:
        """检查混合数据类型"""
        types_found = set()
        for val in series.dropna().head(100):
            try:
                float(val)
                types_found.add('numeric')
            except:
                try:
                    pd.to_datetime(val)
                    types_found.add('date')
                except:
                    types_found.add('text')

        return list(types_found) if len(types_found) > 1 else []

    def _statistical_analysis(self) -> Dict[str, Any]:
        """统计分析"""
        report = {
            'numerical_summary': {},
            'categorical_summary': {},
            'correlation_matrix': None
        }

        # 数值型字段统计
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            data = self.df[col].dropna()
            if len(data) > 0:
                report['numerical_summary'][str(col)] = {
                    'count': len(data),
                    'mean': round(data.mean(), 4),
                    'median': round(data.median(), 4),
                    'std': round(data.std(), 4),
                    'min': data.min(),
                    'max': data.max(),
                    'Q1': data.quantile(0.25),
                    'Q3': data.quantile(0.75),
                    'skewness': round(data.skew(), 4) if len(data) > 2 else 0,
                    'missing_rate': self.df[col].isnull().sum() / len(self.df) * 100
                }

        # 分类型字段统计
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            data = self.df[col].dropna()
            if len(data) > 0:
                value_counts = data.value_counts().head(10)
                report['categorical_summary'][str(col)] = {
                    'unique_count': data.nunique(),
                    'top_values': {str(k): int(v) for k, v in value_counts.items()},
                    'missing_count': self.df[col].isnull().sum()
                }

        # 相关性分析
        if len(numerical_cols) > 1:
            corr = self.df[numerical_cols].corr()
            report['correlation_matrix'] = corr.to_dict()

        return report

    def _detect_anomalies(self):
        """异常检测"""
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numerical_cols:
            data = self.df[col].dropna()
            if len(data) < 3:
                continue

            # Z-Score方法
            z_scores = np.abs((data - data.mean()) / data.std())
            z_anomalies = z_scores > 3

            # IQR方法
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            iqr_anomalies = (data < lower_bound) | (data > upper_bound)

            # 记录异常
            for idx in data[z_anomalies | iqr_anomalies].index:
                val = self.df.loc[idx, col]
                z = z_scores[idx] if idx in z_scores.index else 0
                iqr_factor = 0
                if val < lower_bound:
                    iqr_factor = (lower_bound - val) / IQR if IQR > 0 else 0
                elif val > upper_bound:
                    iqr_factor = (val - upper_bound) / IQR if IQR > 0 else 0

                anomaly_type = '极端值' if z > 3 else '边界外值'
                severity = 'high' if z > 4 or iqr_factor > 2 else 'medium'

                self.anomalies.append(AnomalyRecord(
                    record_index=int(idx),
                    field=str(col),
                    value=float(val),
                    expected_range=(float(lower_bound), float(upper_bound)),
                    anomaly_type=anomaly_type,
                    z_score=float(z),
                    iqr_factor=float(iqr_factor)
                ))

    def _diagnose_problems(self):
        """问题诊断"""
        # 基于检测到的异常进行分组诊断
        if not self.anomalies:
            return

        anomaly_df = pd.DataFrame([
            {
                'field': a.field,
                'type': a.anomaly_type,
                'severity': 'high' if a.z_score > 4 else 'medium'
            }
            for a in self.anomalies
        ])

        # 按字段分组
        field_analysis = anomaly_df.groupby('field').agg({
            'type': 'count',
            'severity': lambda x: 'high' if (x == 'high').any() else 'medium'
        }).rename(columns={'type': 'anomaly_count'})

        # 识别高风险字段
        high_risk_fields = field_analysis[field_analysis['severity'] == 'high'].index.tolist()

        for field in high_risk_fields:
            field_anomalies = [a for a in self.anomalies if a.field == field]
            count = len(field_anomalies)
            pct = count / len(self.df) * 100

            if count > 0:
                issue = DataQualityIssue(
                    issue_id=f"ANM{count:03d}",
                    issue_type="异常值",
                    field=field,
                    description=f"该字段存在 {count} 个统计异常值 ({pct:.2f}%)",
                    record_count=count,
                    percentage=pct,
                    severity='high',
                    sample_records=[
                        {'row': a.record_index + 1, 'value': a.value, 'z_score': round(a.z_score, 2)}
                        for a in field_anomalies[:3]
                    ],
                    suggestion="建议: 检查数据录入/采集过程，分析异常原因"
                )
                # 避免重复添加
                if not any(q.field == field and q.issue_type == '异常值' for q in self.quality_issues):
                    self.quality_issues.append(issue)

    def _root_cause_analysis(self):
        """根因分析"""
        # 问题优先级排序
        critical_issues = [q for q in self.quality_issues if q.severity == 'critical']
        high_issues = [q for q in self.quality_issues if q.severity == 'high']

        # 分析缺失值根因
        missing_issues = [q for q in self.quality_issues if q.issue_type == '缺失值']
        if missing_issues:
            self._analyze_missing_root_cause(missing_issues)

        # 分析异常值根因
        anomaly_issues = [q for q in self.quality_issues if q.issue_type == '异常值']
        if anomaly_issues:
            self._analyze_anomaly_root_cause(anomaly_issues)

    def _analyze_missing_root_cause(self, issues: List[DataQualityIssue]):
        """分析缺失值根因"""
        for issue in issues:
            # 检查是否与其他字段相关
            correlated_missing = []
            for other_col in self.df.columns:
                if other_col == issue.field:
                    continue
                # 计算缺失相关性
                mask1 = self.df[issue.field].isnull()
                mask2 = self.df[other_col].isnull()
                if mask1.sum() > 0 and mask2.sum() > 0:
                    correlation = (mask1 & mask2).sum() / mask1.sum()
                    if correlation > 0.5:
                        correlated_missing.append((other_col, correlation))

            possible_causes = [
                "数据源采集时未记录该字段",
                "数据导入过程中的字段映射错误",
                "历史数据迁移时的字段丢失"
            ]

            if correlated_missing:
                possible_causes.append(f"该字段缺失与 {correlated_missing[0][0]} 高度相关，可能是同一批次数据采集问题")

            evidence = {
                '缺失数量': issue.record_count,
                '缺失占比': f"{issue.percentage:.2f}%",
                '关联缺失字段': correlated_missing[:3] if correlated_missing else '无明显关联'
            }

            self.root_causes.append(RootCauseFinding(
                problem=f"{issue.field}字段存在大量缺失值",
                possible_causes=possible_causes,
                evidence=evidence,
                primary_cause="数据采集/导入环节问题",
                confidence="medium",
                recommendation=f"1. 检查数据源采集流程\n2. 验证数据导入脚本\n3. 补充缺失数据或标记为'未知'"
            ))

    def _analyze_anomaly_root_cause(self, issues: List[DataQualityIssue]):
        """分析异常值根因"""
        for issue in issues:
            anomalies_in_field = [a for a in self.anomalies if a.field == issue.field]

            if not anomalies_in_field:
                continue

            # 分析异常值特征
            values = [a.value for a in anomalies_in_field]
            z_scores = [a.z_score for a in anomalies_in_field]

            # 判断异常类型
            is_extreme = any(z > 5 for z in z_scores)
            is_consistent = len(set(int(v) for v in values)) < len(values) * 0.3

            possible_causes = []
            if is_extreme:
                possible_causes.append("数据录入错误（如单位错误）")
                possible_causes.append("数据合并时错误匹配")
            else:
                possible_causes.append("测量/采集误差")
                possible_causes.append("真实的极端业务情况")

            possible_causes.append("系统计算错误")

            evidence = {
                '异常值数量': issue.record_count,
                '异常值示例': values[:5],
                '最大Z分数': round(max(z_scores), 2) if z_scores else 0,
                '值分布特征': '一致' if is_consistent else '分散'
            }

            self.root_causes.append(RootCauseFinding(
                problem=f"{issue.field}字段存在异常值",
                possible_causes=possible_causes,
                evidence=evidence,
                primary_cause="数据录入错误" if is_extreme else "业务异常或测量误差",
                confidence="medium",
                recommendation=f"1. 检查异常记录原始凭证\n2. 核实数据录入标准\n3. 必要时进行数据修正"
            ))

    def _calculate_quality_score(self) -> float:
        """计算数据质量总分"""
        if not self.quality_issues:
            return 100.0

        weights = {'critical': 20, 'high': 10, 'medium': 5, 'low': 2}
        total_penalty = 0

        for issue in self.quality_issues:
            penalty = weights.get(issue.severity, 5) * issue.percentage / 100
            total_penalty += min(penalty, weights.get(issue.severity, 5))

        score = max(0, 100 - total_penalty)
        return round(score, 2)

    def _generate_report(self, structure_report: Dict, stats_report: Dict) -> str:
        """生成分析报告"""
        quality_score = self._calculate_quality_score()

        report = f"""
# Excel数据分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据文件**: {self.metadata['file_name']}

---

## 1. 执行摘要

| 指标 | 数值 |
|------|------|
| 数据规模 | {self.metadata['row_count']:,} 行 × {self.metadata['column_count']} 列 |
| 数据质量评分 | **{quality_score}分** ({'优秀' if quality_score >= 90 else '良好' if quality_score >= 70 else '一般' if quality_score >= 50 else '较差'}) |
| 发现问题数 | {len(self.quality_issues)} 个 |
| 异常记录数 | {len(self.anomalies)} 个 |
| 根因分析结果 | {len(self.root_causes)} 项 |

### 关键发现

"""

        # 添加关键发现
        if self.quality_issues:
            critical = [q for q in self.quality_issues if q.severity == 'critical']
            high = [q for q in self.quality_issues if q.severity == 'high']

            if critical:
                report += f"- **严重问题**: 发现 {len(critical)} 个严重问题，需要立即处理\n"
            if high:
                report += f"- **高风险问题**: 发现 {len(high)} 个高风险问题，建议尽快处理\n"
            if self.anomalies:
                report += f"- **数据异常**: 检测到 {len(self.anomalies)} 条异常记录\n"

        if quality_score >= 90:
            report += "- 数据整体质量良好\n"
        elif quality_score >= 70:
            report += "- 数据存在一定质量问题，需要关注\n"
        else:
            report += "- **数据质量问题严重，建议优先处理**\n"

        report += """

---

## 2. 数据概况

### 2.1 基本信息

| 属性 | 值 |
|------|---|
| 文件大小 | {:.2f} KB |
| 工作表 | {} |
| 字段数量 | {} |
| 记录数量 | {:,} |
| 内存占用 | {:.2f} MB |

### 2.2 字段清单

| 序号 | 字段名 | 数据类型 | 唯一值数 | 缺失数 | 缺失率 |
|------|--------|----------|----------|--------|--------|
""".format(
            self.metadata['file_size'] / 1024,
            self.metadata['sheet_name'],
            self.metadata['column_count'],
            self.metadata['row_count'],
            structure_report['memory_usage'] / 1024 / 1024
        )

        for i, col in enumerate(structure_report['columns'], 1):
            missing_rate = col['null_count'] / self.metadata['row_count'] * 100
            report += f"| {i} | {col['name']} | {col['dtype']} | {col['unique_count']:,} | {col['null_count']:,} | {missing_rate:.2f}% |\n"

        # 统计分析
        report += """

---

## 3. 统计分析结果

### 3.1 数值型字段统计

| 字段 | 计数 | 均值 | 中位数 | 标准差 | 最小值 | 最大值 | 偏度 |
|------|------|------|--------|--------|--------|--------|------|
"""

        for field, stats in stats_report.get('numerical_summary', {}).items():
            report += f"| {field} | {stats['count']:,} | {stats['mean']:,.2f} | {stats['median']:,.2f} | {stats['std']:,.2f} | {stats['min']:,.2f} | {stats['max']:,.2f} | {stats['skewness']:+.2f} |\n"

        # 分类型统计
        if stats_report.get('categorical_summary'):
            report += """

### 3.2 分类型字段统计

"""
            for field, stats in stats_report['categorical_summary'].items():
                report += f"""
#### {field}
- 唯一值数量: {stats['unique_count']}
- 缺失数量: {stats['missing_count']}
- 高频值分布:
"""
                for value, count in list(stats['top_values'].items())[:5]:
                    pct = count / sum(stats['top_values'].values()) * 100
                    report += f"  - `{value}`: {count} ({pct:.1f}%)\n"

        # 相关性分析
        if stats_report.get('correlation_matrix'):
            report += """

### 3.3 相关性分析

"""
            corr_dict = stats_report['correlation_matrix']
            strong_corrs = []

            for col1 in corr_dict:
                for col2 in corr_dict[col1]:
                    if col1 != col2:
                        corr_val = corr_dict[col1][col2]
                        if abs(corr_val) >= 0.7:
                            strong_corrs.append((col1, col2, corr_val))

            if strong_corrs:
                report += "| 字段A | 字段B | 相关系数 | 关系强度 |\n"
                report += "|-------|-------|----------|----------|\n"
                for col1, col2, corr in sorted(strong_corrs, key=lambda x: -abs(x[2])):
                    strength = '强正相关' if corr > 0.7 else '强负相关'
                    report += f"| {col1} | {col2} | {corr:+.3f} | {strength} |\n"
            else:
                report += "未发现强相关关系(|r| >= 0.7)\n"

        # 数据质量问题报告
        report += """

---

## 4. 数据质量评估

### 4.1 质量评分

**综合评分: {:.1f}/100** {}

### 4.2 问题清单

""".format(quality_score, '✅ 优秀' if quality_score >= 90 else '⚠️ 良好' if quality_score >= 70 else '⚠️ 一般' if quality_score >= 50 else '❌ 较差')

        if self.quality_issues:
            # 按严重程度排序
            sorted_issues = sorted(self.quality_issues,
                                   key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.severity))

            report += "| 问题ID | 问题类型 | 涉及字段 | 问题描述 | 记录数 | 占比 | 严重程度 |\n"
            report += "|--------|----------|---------|---------|--------|------|----------|\n"

            for issue in sorted_issues:
                severity_icon = '🔴' if issue.severity == 'critical' else '🟠' if issue.severity == 'high' else '🟡' if issue.severity == 'medium' else '🔵'
                report += f"| {issue.issue_id} | {issue.issue_type} | {issue.field} | {issue.description} | {issue.record_count:,} | {issue.percentage:.2f}% | {severity_icon}{issue.severity} |\n"

            # 严重问题详情
            critical_high_issues = [q for q in sorted_issues if q.severity in ['critical', 'high']]
            if critical_high_issues:
                report += """

#### 严重/高风险问题详情

"""
                for issue in critical_high_issues:
                    report += f"""
**{issue.issue_id}: {issue.field} - {issue.issue_type}**

- 描述: {issue.description}
- 建议: {issue.suggestion}
"""
                    if issue.sample_records:
                        report += "- 样例记录:\n"
                        for rec in issue.sample_records[:3]:
                            report += f"  - 行{rec.get('row', 'N/A')}: {rec.get('value', 'N/A')}\n"
        else:
            report += "✅ 未发现数据质量问题\n"

        # 异常检测报告
        report += """

---

## 5. 异常检测报告

"""
        if self.anomalies:
            report += f"共检测到 **{len(self.anomalies)}** 个异常记录\n\n"

            # 按字段分组统计
            anomaly_by_field = {}
            for a in self.anomalies:
                if a.field not in anomaly_by_field:
                    anomaly_by_field[a.field] = []
                anomaly_by_field[a.field].append(a)

            for field, anomalies in anomaly_by_field.items():
                report += f"""
### {field}

| 行号 | 值 | 异常类型 | Z分数 |
|------|-----|---------|-------|
"""
                for a in anomalies[:10]:
                    report += f"| {a.record_index + 1} | {a.value:,.2f} | {a.anomaly_type} | {a.z_score:.2f} |\n"

                if len(anomalies) > 10:
                    report += f"\n*...还有 {len(anomalies) - 10} 条异常记录*\n"
        else:
            report += "✅ 未检测到统计异常值\n"

        # 根因分析报告
        report += """

---

## 6. 问题诊断与根因分析

"""
        if self.root_causes:
            for i, rc in enumerate(self.root_causes, 1):
                confidence_icon = '🟢' if rc.confidence == 'high' else '🟡' if rc.confidence == 'medium' else '⚪'

                report += f"""
### 6.{i} {rc.problem}

**可能原因:**
"""
                for cause in rc.possible_causes:
                    report += f"- {cause}\n"

                report += f"""
**证据支持:**
"""
                for key, value in rc.evidence.items():
                    report += f"- {key}: {value}\n"

                report += f"""
**根本原因** ({confidence_icon}{rc.confidence}置信度)
> {rc.primary_cause}

**修复建议:**
{rc.recommendation}
"""
        else:
            report += "未发现需要深入根因分析的问题\n"

        # 总结与建议
        report += """

---

## 7. 总结与建议

### 7.1 数据质量总评

"""

        if quality_score >= 90:
            report += "**优秀**: 数据质量良好，可以直接用于分析和决策。"
        elif quality_score >= 70:
            report += "**良好**: 数据整体可用，但存在一些需要关注的问题。"
        elif quality_score >= 50:
            report += "**一般**: 数据质量一般，建议处理主要问题后再使用。"
        else:
            report += "**较差**: 数据质量问题严重，建议优先进行数据治理后再分析。"

        report += """

### 7.2 优先处理建议

"""

        # 按严重程度和影响范围排序
        priority_issues = sorted(self.quality_issues,
                                key=lambda x: (
                                    ['critical', 'high', 'medium', 'low'].index(x.severity),
                                    -x.record_count
                                ))[:5]

        if priority_issues:
            report += "| 优先级 | 问题 | 涉及字段 | 处理建议 |\n"
            report += "|--------|------|---------|---------|\n"
            for i, issue in enumerate(priority_issues, 1):
                report += f"| {i} | {issue.issue_type} | {issue.field} | {issue.suggestion.split('建议:')[1].strip() if '建议:' in issue.suggestion else issue.suggestion} |\n"
        else:
            report += "无优先处理项\n"

        report += """

### 7.3 长期改进建议

1. **数据采集环节**: 规范数据录入标准，增加必填字段校验
2. **数据导入环节**: 增强导入脚本的数据校验能力
3. **数据存储环节**: 建立数据质量监控机制
4. **数据使用环节**: 定期进行数据质量评估和清理

---

*报告由Excel深度分析技能自动生成*
"""

        return report

    def save_report(self, output_path: str = None):
        """保存分析报告"""
        if output_path is None:
            output_path = self.file_path.stem + '_analysis_report.md'

        report = self._generate_report(self._analyze_structure(), self._statistical_analysis())

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return output_path


def analyze_excel(file_path: str, sheet_name: str = None, output_path: str = None) -> str:
    """
    分析Excel文件的便捷函数

    参数:
        file_path: Excel文件路径
        sheet_name: 工作表名称（可选）
        output_path: 报告输出路径（可选）

    返回:
        分析报告内容
    """
    analyzer = ExcelDeepAnalyzer(file_path, sheet_name)
    report = analyzer.full_analysis()

    if output_path:
        analyzer.save_report(output_path)
        print(f"报告已保存至: {output_path}")

    return report


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python excel_analyzer.py <excel_file_path> [output_report_path]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        report = analyze_excel(file_path, output_path=output_path)
        print("\n" + "="*60)
        print("分析完成!")
        print("="*60)
    except Exception as e:
        print(f"分析失败: {str(e)}")
        sys.exit(1)
