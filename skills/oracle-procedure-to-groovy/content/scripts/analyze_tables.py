#!/usr/bin/env python3
"""
表对象分析器 - Checkpoint CP2/CP3
分析存储过程中的表对象，并进行表归属判断
"""

import json
import sys
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set


@dataclass
class TableInfo:
    """表信息"""
    name: str
    alias: Optional[str] = None
    shard_key: Optional[str] = None
    target_db: Optional[str] = None
    shard_type: Optional[str] = None
    shard_value: Optional[str] = None
    status: str = "pending"  # pending, mapped, unknown


@dataclass
class AnalysisResult:
    """分析结果"""
    tables: List[Dict]
    shard_mapping: Dict[str, str]
    pending_tables: List[str]
    cross_db_operations: List[Dict]
    report: str


class TableAnalyzer:
    """表对象分析器"""

    def __init__(self, sql_content: str, shard_config_path: str = None):
        self.content = sql_content
        self.shard_config = {}
        self.tables: List[TableInfo] = []

        if shard_config_path and Path(shard_config_path).exists():
            self.load_shard_config(shard_config_path)

    def load_shard_config(self, config_path: str):
        """加载表分片配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = json.load(f)

        # 支持JSON和简单文本格式
        if isinstance(raw_config, dict):
            for table_name, config in raw_config.items():
                self.shard_config[table_name.upper()] = {
                    'target_db': config.get('target_db', config.get('database', 'unknown')),
                    'shard_key': config.get('shard_key', config.get('partition_key')),
                    'shard_type': config.get('shard_type', 'hash'),
                    'shard_value': config.get('shard_value', config.get('partition_value'))
                }
        elif isinstance(raw_config, list):
            # Excel导出格式: [[表名, 分片字段, 分片类型, 分片值, 目标库], ...]
            for row in raw_config:
                if len(row) >= 5:
                    table_name = row[0].upper()
                    self.shard_config[table_name] = {
                        'shard_key': row[1],
                        'shard_type': row[2],
                        'shard_value': row[3],
                        'target_db': row[4]
                    }

    def scan_tables(self) -> List[TableInfo]:
        """扫描所有表对象"""
        tables_found = set()
        table_patterns = [
            # FROM子句
            re.compile(r'\bFROM\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?', re.IGNORECASE),
            # UPDATE子句
            re.compile(r'\bUPDATE\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?', re.IGNORECASE),
            # INSERT INTO子句
            re.compile(r'\bINSERT\s+INTO\s+([\w.]+)(?:\s*\(|\s+|\(|;)', re.IGNORECASE),
            # JOIN子句
            re.compile(r'\bJOIN\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?', re.IGNORECASE),
            # INTO子句（SELECT INTO）
            re.compile(r'\bINTO\s+([\w.]+)', re.IGNORECASE)
        ]

        for pattern in table_patterns:
            for match in pattern.finditer(self.content):
                table_name = match.group(1).strip()
                # 过滤系统表和关键字
                if table_name.upper() not in ('DUAL', 'SYS.DUAL', 'SYSDATE', ''):
                    alias = match.group(2).strip() if match.group(2) else None
                    tables_found.add((table_name.upper(), alias))

        # 去重并创建TableInfo列表
        for table_name, alias in tables_found:
            table_info = TableInfo(
                name=table_name,
                alias=alias if alias else None,
                status="pending"
            )

            # 匹配分片配置
            if table_name in self.shard_config:
                config = self.shard_config[table_name]
                table_info.target_db = config['target_db']
                table_info.shard_key = config.get('shard_key')
                table_info.shard_type = config.get('shard_type')
                table_info.shard_value = config.get('shard_value')
                table_info.status = "mapped"
            else:
                table_info.status = "unknown"

            self.tables.append(table_info)

        return self.tables

    def detect_cross_db_operations(self) -> List[Dict]:
        """检测跨库操作"""
        cross_db_ops = []

        # 提取每个SQL语句涉及的表
        sql_blocks = self._split_sql_blocks()

        for block in sql_blocks:
            tables_in_block = self._extract_tables_from_block(block)
            target_dbs = set()

            for table_name in tables_in_block:
                if table_name in self.shard_config:
                    target_dbs.add(self.shard_config[table_name]['target_db'])
                else:
                    target_dbs.add("unknown")

            if len(target_dbs) > 1:
                cross_db_ops.append({
                    'sql_preview': block[:100] + ('...' if len(block) > 100 else ''),
                    'tables': list(tables_in_block),
                    'target_dbs': list(target_dbs),
                    'risk_level': 'high' if len(target_dbs) > 2 else 'medium'
                })

        return cross_db_ops

    def _split_sql_blocks(self) -> List[str]:
        """分割SQL块"""
        blocks = []
        current_block = []

        for line in self.content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('--'):
                if any(stripped.startswith(kw) for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE']):
                    if current_block:
                        blocks.append(' '.join(current_block))
                    current_block = [line]
                else:
                    current_block.append(line)

        if current_block:
            blocks.append(' '.join(current_block))

        return blocks

    def _extract_tables_from_block(self, block: str) -> Set[str]:
        """从SQL块中提取表"""
        tables = set()

        patterns = [
            re.compile(r'\bFROM\s+([\w.]+)', re.IGNORECASE),
            re.compile(r'\bJOIN\s+([\w.]+)', re.IGNORECASE),
            re.compile(r'\bUPDATE\s+([\w.]+)', re.IGNORECASE),
            re.compile(r'\bINSERT\s+INTO\s+([\w.]+)', re.IGNORECASE)
        ]

        for pattern in patterns:
            for match in pattern.finditer(block):
                table = match.group(1).upper()
                if table not in ('DUAL', 'SYS.DUAL'):
                    tables.add(table)

        return tables

    def generate_report(self) -> str:
        """生成分析报告"""
        mapped_count = sum(1 for t in self.tables if t.status == "mapped")
        unknown_count = sum(1 for t in self.tables if t.status == "unknown")

        report = f"""## 表对象分析报告

### 统计摘要
- 总表数: {len(self.tables)}
- 已配置归属: {mapped_count}
- 待确认表: {unknown_count}

### 表归属映射
"""

        for table in self.tables:
            status_icon = "✓" if table.status == "mapped" else "⚠"
            target = table.target_db or "待确认"
            report += f"- {status_icon} {table.name} → {target}\n"

        cross_db = self.detect_cross_db_operations()
        if cross_db:
            report += f"\n### 跨库操作风险\n"
            report += f"- 跨库SQL数量: {len(cross_db)}\n"
            for i, op in enumerate(cross_db, 1):
                report += f"{i}. 涉及数据库: {', '.join(op['target_dbs'])}\n"
                report += f"   表: {', '.join(op['tables'])}\n"

        return report

    def run_analysis(self) -> AnalysisResult:
        """运行完整分析"""
        self.scan_tables()

        shard_mapping = {
            t.name: t.target_db for t in self.tables
            if t.target_db
        }

        pending = [t.name for t in self.tables if t.status != "mapped"]

        return AnalysisResult(
            tables=[asdict(t) for t in self.tables],
            shard_mapping=shard_mapping,
            pending_tables=pending,
            cross_db_operations=self.detect_cross_db_operations(),
            report=self.generate_report()
        )


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='表对象分析器')
    parser.add_argument('--input', required=True, help='存储过程文件路径')
    parser.add_argument('--shard-config', help='表分片配置文件路径(JSON/Excel)')
    parser.add_argument('--output', help='输出JSON文件路径')

    args = parser.parse_args()

    # 读取文件
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件 {args.input} 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)

    # 执行分析
    analyzer = TableAnalyzer(content, args.shard_config)
    result = analyzer.run_analysis()

    # 输出结果
    output = {
        'tables': result.tables,
        'shard_mapping': result.shard_mapping,
        'pending_tables': result.pending_tables,
        'cross_db_operations': result.cross_db_operations,
        'report': result.report
    }

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    print("\n" + result.report)


if __name__ == '__main__':
    main()