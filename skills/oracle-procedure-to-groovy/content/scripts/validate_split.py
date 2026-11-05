#!/usr/bin/env python3
"""
SQL拆分验证器 - Checkpoint CP4
验证跨库SQL的拆分方案合理性
"""

import json
import sys
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set


@dataclass
class SplitRecommendation:
    """拆分建议"""
    sql_type: str  # single_db, cross_db, dynamic
    tables: List[str]
    target_dbs: List[str]
    recommendation: str  # merge, split, distribute
    reason: str
    risk_level: str  # low, medium, high


@dataclass
class ValidationResult:
    """验证结果"""
    checkpoint: str
    passed: bool
    split_recommendations: List[Dict]
    transaction_boundaries: List[Dict]
    warnings: List[str]
    error: Optional[str] = None


class SQLSplitter:
    """SQL拆分验证器"""

    def __init__(self, sql_statements: List[Dict], shard_mapping: Dict[str, str]):
        self.sql_statements = sql_statements
        self.shard_mapping = shard_mapping
        self.recommendations: List[SplitRecommendation] = []
        self.transactions: List[Dict] = []

    def analyze_statement(self, stmt: Dict) -> SplitRecommendation:
        """分析单个SQL语句的拆分需求"""
        sql_text = stmt.get('sql', '')
        sql_type = stmt.get('type', 'UNKNOWN')

        # 提取表
        tables = self._extract_tables(sql_text)

        # 确定目标数据库
        target_dbs = set()
        for table in tables:
            table_upper = table.upper()
            if table_upper in self.shard_mapping:
                target_dbs.add(self.shard_mapping[table_upper])
            else:
                target_dbs.add('unknown')

        # 判断类型
        if sql_type == 'DYNAMIC_SQL':
            return SplitRecommendation(
                sql_type='dynamic',
                tables=tables,
                target_dbs=list(target_dbs),
                recommendation='analyze_runtime',
                reason='动态SQL需要运行时分析',
                risk_level='high'
            )

        # 判断单库还是跨库
        valid_dbs = set(db for db in target_dbs if db != 'unknown')
        if len(valid_dbs) <= 1:
            return SplitRecommendation(
                sql_type='single_db',
                tables=tables,
                target_dbs=list(target_dbs),
                recommendation='keep',
                reason='所有表在同一数据库',
                risk_level='low'
            )
        else:
            # 跨库场景，判断是否可以合并
            recommendation = self._determine_cross_db_strategy(sql_text, tables, valid_dbs)
            return recommendation

    def _extract_tables(self, sql_text: str) -> List[str]:
        """从SQL文本提取表"""
        tables = set()

        patterns = [
            re.compile(r'\bFROM\s+([\w.]+)', re.IGNORECASE),
            re.compile(r'\bJOIN\s+([\w.]+)', re.IGNORECASE),
            re.compile(r'\bUPDATE\s+([\w.]+)', re.IGNORECASE),
            re.compile(r'\bINSERT\s+INTO\s+([\w.]+)', re.IGNORECASE)
        ]

        for pattern in patterns:
            for match in pattern.finditer(sql_text):
                table = match.group(1).upper()
                if table not in ('DUAL', 'SYS.DUAL'):
                    tables.add(table)

        return list(tables)

    def _determine_cross_db_strategy(self, sql_text: str, tables: List[str], target_dbs: Set[str]) -> SplitRecommendation:
        """确定跨库SQL的处理策略"""

        # 检查是否有JOIN操作
        has_join = 'JOIN' in sql_text.upper()

        # 检查是否有UNION操作
        has_union = 'UNION' in sql_text.upper()

        # 检查数据量级别
        has_limit = any(keyword in sql_text.upper() for keyword in ['LIMIT', 'ROWNUM', 'FETCH FIRST'])
        has_aggregation = any(keyword in sql_text.upper() for keyword in ['GROUP BY', 'HAVING', 'SUM(', 'COUNT(', 'AVG(', 'MAX(', 'MIN('])

        # 策略判断
        if has_join:
            return SplitRecommendation(
                sql_type='cross_db',
                tables=tables,
                target_dbs=list(target_dbs),
                recommendation='split',
                reason='JOIN操作需分步执行，先查各库再内存JOIN',
                risk_level='medium'
            )
        elif has_union:
            return SplitRecommendation(
                sql_type='cross_db',
                tables=tables,
                target_dbs=list(target_dbs),
                recommendation='merge',
                reason='UNION可拆分为独立查询后合并结果集',
                risk_level='low'
            )
        elif has_aggregation:
            return SplitRecommendation(
                sql_type='cross_db',
                tables=tables,
                target_dbs=list(target_dbs),
                recommendation='distribute',
                reason='聚合操作建议在各库预处理后合并',
                risk_level='medium'
            )
        else:
            return SplitRecommendation(
                sql_type='cross_db',
                tables=tables,
                target_dbs=list(target_dbs),
                recommendation='analyze',
                reason='需要进一步分析数据依赖关系',
                risk_level='high'
            )

    def detect_transaction_boundaries(self, content: str) -> List[Dict]:
        """检测事务边界"""
        boundaries = []
        in_transaction = False
        start_line = 0

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip().upper()

            if 'BEGIN' in stripped and 'BEGIN' not in stripped.replace('BEGIN', ''):
                in_transaction = True
                start_line = line_num
                boundaries.append({
                    'type': 'start',
                    'line': line_num,
                    'label': stripped[:50]
                })
            elif 'COMMIT' in stripped:
                if in_transaction:
                    boundaries.append({
                        'type': 'commit',
                        'line': line_num,
                        'start_line': start_line
                    })
                    in_transaction = False
            elif 'ROLLBACK' in stripped:
                if in_transaction:
                    boundaries.append({
                        'type': 'rollback',
                        'line': line_num,
                        'start_line': start_line
                    })
                    in_transaction = False

        return boundaries

    def run_validation(self, content: str = None) -> ValidationResult:
        """运行完整验证"""
        warnings = []

        # 分析每个SQL语句
        for stmt in self.sql_statements:
            rec = self.analyze_statement(stmt)
            self.recommendations.append(rec)

        # 检测事务边界
        if content:
            self.transactions = self.detect_transaction_boundaries(content)

        # 生成警告
        high_risk_count = sum(1 for r in self.recommendations if r.risk_level == 'high')
        if high_risk_count > 0:
            warnings.append(f"发现 {high_risk_count} 个高风险SQL，可能需要人工审查")

        cross_db_count = sum(1 for r in self.recommendations if r.sql_type == 'cross_db')
        if cross_db_count > 3:
            warnings.append(f"跨库SQL较多({cross_db_count})，建议批量优化")

        # 检查是否通过
        has_blocker = any(r.risk_level == 'high' and r.recommendation == 'analyze' for r in self.recommendations)
        passed = not has_blocker

        return ValidationResult(
            checkpoint='CP4',
            passed=passed,
            split_recommendations=[asdict(r) for r in self.recommendations],
            transaction_boundaries=self.transactions,
            warnings=warnings,
            error=None if passed else "存在无法自动处理的跨库SQL，需人工分析"
        )


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='SQL拆分验证器')
    parser.add_argument('--sql-statements', required=True, help='SQL语句JSON文件')
    parser.add_argument('--shard-map', required=True, help='表归属映射JSON文件')
    parser.add_argument('--content', help='原始存储过程内容（用于事务边界检测）')
    parser.add_argument('--output', help='输出JSON文件路径')

    args = parser.parse_args()

    # 读取SQL语句
    try:
        with open(args.sql_statements, 'r', encoding='utf-8') as f:
            sql_statements = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件 {args.sql_statements} 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取SQL语句失败 - {e}")
        sys.exit(1)

    # 读取分片映射
    try:
        with open(args.shard_map, 'r', encoding='utf-8') as f:
            shard_mapping = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件 {args.shard_map} 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取分片映射失败 - {e}")
        sys.exit(1)

    # 读取原始内容
    content = None
    if args.content and Path(args.content).exists():
        with open(args.content, 'r', encoding='utf-8') as f:
            content = f.read()

    # 执行验证
    validator = SQLSplitter(sql_statements, shard_mapping)
    result = validator.run_validation(content)

    # 输出结果
    output = asdict(result)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"验证结果已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    # 打印摘要
    print(f"\n=== 拆分验证摘要 ===")
    print(f"验证状态: {'通过' if result.passed else '失败'}")
    print(f"单库SQL: {sum(1 for r in result.split_recommendations if r['sql_type'] == 'single_db')}")
    print(f"跨库SQL: {sum(1 for r in result.split_recommendations if r['sql_type'] == 'cross_db')}")
    print(f"动态SQL: {sum(1 for r in result.split_recommendations if r['sql_type'] == 'dynamic')}")

    if result.warnings:
        print("\n警告:")
        for warning in result.warnings:
            print(f"  - {warning}")

    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()