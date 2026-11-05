#!/usr/bin/env python3
"""
Oracle存储过程到Groovy转换器 - PL/SQL语法验证器
Checkpoint: CP1 - 存储过程语法完整性检查
"""

import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class ValidationResult:
    """验证结果数据类"""
    checkpoint: str
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    tables_found: List[str] = field(default_factory=list)
    parameters: List[Dict] = field(default_factory=list)
    sql_statements: List[Dict] = field(default_factory=list)


class PLSQLValidator:
    """PL/SQL语法验证器"""

    # 正则表达式定义
    PROCEDURE_PATTERN = re.compile(
        r'CREATE\s+(OR\s+REPLACE\s+)?(PROCEDURE|FUNCTION|PACKAGE)',
        re.IGNORECASE | re.MULTILINE
    )

    PARAM_PATTERN = re.compile(
        r'(IN|OUT|IN\s*OUT)\s+([\w]+)\s*(\([^)]+\))?\s*(?:DEFAULT|:=)?\s*(.+?)?(?=,|\))',
        re.IGNORECASE
    )

    VARIABLE_PATTERN = re.compile(
        r'(v_\w+|p_\w+|g_\w+)\s+([\w]+(?:\(\d+(?:,\d+)?\))?)',
        re.IGNORECASE
    )

    TABLE_PATTERN = re.compile(
        r'\b(FROM|INSERT\s+INTO|UPDATE|JOIN|INTO)\s+([\w]+(?:\s+\w+)?)',
        re.IGNORECASE | re.MULTILINE
    )

    SQL_PATTERN = re.compile(
        r'(SELECT|INSERT|UPDATE|DELETE|MERGE)\s+',
        re.IGNORECASE
    )

    DYNAMIC_SQL_PATTERN = re.compile(
        r'EXECUTE\s+IMMEDIATE\s+[\'"]([^\'"]+)',
        re.IGNORECASE
    )

    def __init__(self, sql_content: str):
        self.content = sql_content
        self.lines = sql_content.split('\n')

    def validate_syntax(self) -> ValidationResult:
        """执行语法验证"""
        result = ValidationResult(checkpoint="CP1", passed=True)

        # 检查1: 是否包含存储过程/函数定义
        if not self.PROCEDURE_PATTERN.search(self.content):
            result.warnings.append("未找到CREATE PROCEDURE/FUNCTION语句")

        # 检查2: 是否包含BEGIN-END块
        if not re.search(r'\bBEGIN\b', self.content, re.IGNORECASE):
            result.errors.append("缺少BEGIN关键字")
            result.passed = False

        if not re.search(r'\bEND\s*(?:;|/)?\s*$', self.content, re.MULTILINE):
            result.errors.append("缺少END关键字或未正确结束")
            result.passed = False

        # 检查3: 括号匹配
        open_parens = self.content.count('(')
        close_parens = self.content.count(')')
        if open_parens != close_parens:
            result.errors.append(f"括号不匹配: ({open_parens} vs ){close_parens}")
            result.passed = False

        # 检查4: 引号匹配
        single_quote_count = self.content.count("'")
        if single_quote_count % 2 != 0:
            result.errors.append("单引号未正确闭合")
            result.passed = False

        return result

    def extract_parameters(self) -> List[Dict]:
        """提取参数列表"""
        params = []

        # 提取参数定义区域
        param_section = re.search(
            r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:PROCEDURE|FUNCTION)\s+\w+\s*\((.*?)\)',
            self.content,
            re.IGNORECASE | re.DOTALL
        )

        if param_section:
            param_text = param_section.group(1)
            for match in self.PARAM_PATTERN.finditer(param_text):
                params.append({
                    'mode': match.group(1).strip().replace(' ', '_'),
                    'name': match.group(2).strip(),
                    'type': match.group(3).strip() if match.group(3) else 'VARCHAR2',
                    'default': match.group(4).strip() if match.group(4) else None
                })

        return params

    def extract_tables(self) -> List[str]:
        """提取表对象列表"""
        tables = set()

        # 扫描FROM子句
        from_pattern = re.compile(
            r'\bFROM\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?',
            re.IGNORECASE
        )
        for match in from_pattern.finditer(self.content):
            table = match.group(1).strip()
            if table and table.upper() not in ('DUAL', 'SYS.DUAL'):
                tables.add(table)

        # 扫描UPDATE子句
        update_pattern = re.compile(
            r'\bUPDATE\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?',
            re.IGNORECASE
        )
        for match in update_pattern.finditer(self.content):
            tables.add(match.group(1).strip())

        # 扫描INSERT INTO子句
        insert_pattern = re.compile(
            r'\bINSERT\s+INTO\s+([\w.]+)',
            re.IGNORECASE
        )
        for match in insert_pattern.finditer(self.content):
            tables.add(match.group(1).strip())

        # 扫描JOIN子句
        join_pattern = re.compile(
            r'\bJOIN\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?',
            re.IGNORECASE
        )
        for match in join_pattern.finditer(self.content):
            tables.add(match.group(1).strip())

        return sorted(list(tables))

    def extract_sql_statements(self) -> List[Dict]:
        """提取SQL语句列表"""
        statements = []

        # 提取SELECT语句
        select_pattern = re.compile(
            r'(SELECT\s+(?:(?!WHERE|FROM|ORDER|GROUP).)*)',
            re.IGNORECASE | re.DOTALL
        )

        # 提取完整的SELECT语句
        full_select_pattern = re.compile(
            r'(SELECT\b.*?;?)',
            re.IGNORECASE | re.DOTALL
        )

        for match in full_select_pattern.finditer(self.content):
            sql_type = 'SELECT'
            if match.group(0).strip().startswith('SELECT'):
                statements.append({
                    'type': sql_type,
                    'operation': 'read',
                    'sql': match.group(0).strip()[:200]
                })

        # 提取INSERT语句
        insert_pattern = re.compile(
            r'(INSERT\s+INTO\b.*?;?)',
            re.IGNORECASE | re.DOTALL
        )
        for match in insert_pattern.finditer(self.content):
            statements.append({
                'type': 'INSERT',
                'operation': 'write',
                'sql': match.group(0).strip()[:200]
            })

        # 提取UPDATE语句
        update_pattern = re.compile(
            r'(UPDATE\b.*?;?)',
            re.IGNORECASE | re.DOTALL
        )
        for match in update_pattern.finditer(self.content):
            statements.append({
                'type': 'UPDATE',
                'operation': 'write',
                'sql': match.group(0).strip()[:200]
            })

        # 提取DELETE语句
        delete_pattern = re.compile(
            r'(DELETE\s+FROM\b.*?;?)',
            re.IGNORECASE | re.DOTALL
        )
        for match in delete_pattern.finditer(self.content):
            statements.append({
                'type': 'DELETE',
                'operation': 'write',
                'sql': match.group(0).strip()[:200]
            })

        # 提取EXECUTE IMMEDIATE（动态SQL）
        dynamic_pattern = re.compile(
            r'(EXECUTE\s+IMMEDIATE\s+[\'"][^\'"]+[\'"])',
            re.IGNORECASE
        )
        for match in dynamic_pattern.finditer(self.content):
            statements.append({
                'type': 'DYNAMIC_SQL',
                'operation': 'dynamic',
                'sql': match.group(0).strip()[:200]
            })

        return statements

    def run_full_validation(self) -> ValidationResult:
        """运行完整验证流程"""
        result = self.validate_syntax()
        result.parameters = self.extract_parameters()
        result.tables_found = self.extract_tables()
        result.sql_statements = self.extract_sql_statements()

        return result


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='PL/SQL语法验证器')
    parser.add_argument('--input', required=True, help='存储过程文件路径')
    parser.add_argument('--output', help='输出JSON文件路径')
    parser.add_argument('--checkpoint', default='CP1', help='检查点名称')

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

    # 执行验证
    validator = PLSQLValidator(content)
    result = validator.run_full_validation()
    result.checkpoint = args.checkpoint

    # 输出结果
    output = asdict(result)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"验证结果已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    # 返回状态
    if not result.passed:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()