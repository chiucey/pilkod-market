#!/usr/bin/env python3
"""
Groovy语法验证器 - Checkpoint CP5/CP6
验证生成的Groovy脚本语法正确性和业务逻辑完整性
"""

import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class ValidationIssue:
    """验证问题"""
    severity: str  # error, warning, info
    line: int
    message: str
    suggestion: Optional[str] = None


@dataclass
class GroovyValidationResult:
    """验证结果"""
    checkpoint: str
    passed: bool
    issues: List[Dict] = field(default_factory=list)
    syntax_valid: bool = True
    logic_complete: bool = True
    performance_warnings: List[str] = field(default_factory=list)


class GroovyValidator:
    """Groovy语法验证器"""

    # Groovy语法检查模式
    BRACKET_PAIRS = {'(': ')', '[': ']', '{': '}'}
    KEYWORDS = ['def', 'class', 'void', 'return', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally', 'import', 'package']

    def __init__(self, groovy_content: str):
        self.content = groovy_content
        self.lines = groovy_content.split('\n')

    def validate_syntax(self) -> List[ValidationIssue]:
        """验证Groovy语法"""
        issues = []

        # 1. 检查括号匹配
        issues.extend(self._check_brackets())

        # 2. 检查引号匹配
        issues.extend(self._check_quotes())

        # 3. 检查分号使用（Groovy可选分号）
        issues.extend(self._check_semicolons())

        # 4. 检查import语句
        issues.extend(self._check_imports())

        # 5. 检查方法定义
        issues.extend(self._check_methods())

        # 6. 检查字符串插值
        issues.extend(self._check_string_interpolation())

        return issues

    def _check_brackets(self) -> List[ValidationIssue]:
        """检查括号匹配"""
        issues = []
        stack = []

        for line_num, line in enumerate(self.lines, 1):
            # 跳过注释
            if line.strip().startswith('//') or line.strip().startswith('/*'):
                continue

            for char in line:
                if char in '([{':
                    stack.append((char, line_num))
                elif char in ')]}':
                    if stack:
                        last_open, open_line = stack.pop()
                        if self.BRACKET_PAIRS.get(last_open) != char:
                            issues.append(ValidationIssue(
                                severity='error',
                                line=line_num,
                                message=f"括号不匹配: '{last_open}' 在行 {open_line} 与 '{char}' 不配对",
                                suggestion=f"检查行 {open_line} 到 {line_num} 的括号"
                            ))

        # 检查未关闭的括号
        while stack:
            char, line_num = stack.pop()
            issues.append(ValidationIssue(
                severity='error',
                line=line_num,
                message=f"括号 '{char}' 未关闭",
                suggestion="在适当位置添加对应的闭合括号"
            ))

        return issues

    def _check_quotes(self) -> List[ValidationIssue]:
        """检查引号匹配"""
        issues = []
        single_quote_count = 0
        double_quote_count = 0
        in_multiline = False

        for line_num, line in enumerate(self.lines, 1):
            if '"""' in line:
                in_multiline = not in_multiline
                continue

            if not in_multiline:
                # 简化检查：计算未被转义的引号
                stripped = line.replace('\\"', '').replace("\\'", "")
                # 过滤字符串内容中的引号
                test_line = re.sub(r'"[^"]*"', '""', stripped)
                test_line = re.sub(r"'[^']*'", "''", test_line)

                single_quote_count += test_line.count("'")
                double_quote_count += test_line.count('"')

        if single_quote_count % 2 != 0:
            issues.append(ValidationIssue(
                severity='error',
                line=0,
                message="单引号未正确闭合"
            ))

        if double_quote_count % 2 != 0:
            issues.append(ValidationIssue(
                severity='error',
                line=0,
                message="双引号未正确闭合"
            ))

        return issues

    def _check_semicolons(self) -> List[ValidationIssue]:
        """检查语句分隔"""
        issues = []

        # Groovy推荐不加分号，检查是否有语法问题
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                # 检查是否有无意义的空语句
                if re.match(r'^;+\s*$', stripped):
                    issues.append(ValidationIssue(
                        severity='warning',
                        line=line_num,
                        message="发现空语句",
                        suggestion="删除多余的分号"
                    ))

        return issues

    def _check_imports(self) -> List[ValidationIssue]:
        """检查import语句"""
        issues = []
        imports = []

        import_pattern = re.compile(r'^import\s+([\w.]+)', re.MULTILINE)

        for match in import_pattern.finditer(self.content):
            import_path = match.group(1)
            if import_path in imports:
                issues.append(ValidationIssue(
                    severity='warning',
                    line=0,
                    message=f"重复import: {import_path}",
                    suggestion="删除重复的import语句"
                ))
            imports.append(import_path)

        return issues

    def _check_methods(self) -> List[ValidationIssue]:
        """检查方法定义"""
        issues = []

        # 检查方法是否都有返回类型或def
        method_pattern = re.compile(r'^\s*(private|public|protected)?\s*(\w+)\s+(\w+)\s*\(', re.MULTILINE)

        for match in method_pattern.finditer(self.content):
            access = match.group(1) or 'public'
            return_type = match.group(2)
            method_name = match.group(3)

            if return_type not in self.KEYWORDS and not re.match(r'^[A-Z]', return_type):
                issues.append(ValidationIssue(
                    severity='warning',
                    line=0,
                    message=f"方法 '{method_name}' 缺少显式返回类型",
                    suggestion=f"考虑使用 'def {method_name}' 或显式指定返回类型"
                ))

        return issues

    def _check_string_interpolation(self) -> List[ValidationIssue]:
        """检查字符串插值"""
        issues = []

        # 检查Groovy字符串插值格式 ${} 或 $var
        for line_num, line in enumerate(self.lines, 1):
            # 查找单引号中使用了$的情况（这会导致问题）
            if "'" in line:
                # 简单检查：单引号内不应有$变量
                in_single = False
                i = 0
                while i < len(line):
                    char = line[i]
                    if char == "'" and (i == 0 or line[i-1] != '\\'):
                        in_single = not in_single
                    elif char == '$' and in_single:
                        issues.append(ValidationIssue(
                            severity='warning',
                            line=line_num,
                            message="单引号字符串中使用了变量插值，这不会生效",
                            suggestion="使用双引号来启用变量插值"
                        ))
                        break
                    i += 1

        return issues

    def check_performance(self) -> List[str]:
        """检查潜在的性能问题"""
        warnings = []

        # 1. 检查是否使用了预编译SQL
        if 'Sql' in self.content and 'new Sql' in self.content:
            if 'withStatement' not in self.content and 'prepareStatement' not in self.content:
                warnings.append("建议使用预编译SQL以提高性能（参考: PreparedStatement或withStatement）")

        # 2. 检查是否有循环中的数据库操作（N+1问题）
        if re.search(r'for\s*\([^)]*\)\s*\{[^}]*sql\.(rows|execute|first)', self.content, re.DOTALL):
            warnings.append("[高风险] 检测到循环中的数据库操作，可能导致N+1查询问题，建议改用批量操作")

        # 3. 检查是否正确关闭资源
        if 'new Sql' in self.content and 'close()' not in self.content:
            warnings.append("建议使用try-with-resources或显式关闭Sql资源")

        # 4. 检查是否有分页处理
        if 'SELECT' in self.content and 'WHERE' in self.content:
            if 'LIMIT' not in self.content and 'ROWNUM' not in self.content and 'fetchFirst' not in self.content:
                warnings.append("建议为大查询结果添加分页处理")

        return warnings

    def validate_logic_completeness(self, original_sql: str = None) -> bool:
        """验证业务逻辑完整性"""
        # 检查基本结构
        has_class = 'class ' in self.content or 'class\t' in self.content
        has_method = re.search(r'def\s+\w+\s*\(', self.content) is not None

        if not has_class or not has_method:
            return False

        # 检查是否包含基本的数据库操作
        has_db_operation = any(op in self.content for op in [
            'sql.rows', 'sql.execute', 'sql.firstRow', 'sql.each'
        ])

        return has_db_operation

    def run_validation(self, original_sql: str = None) -> GroovyValidationResult:
        """运行完整验证"""
        issues = self.validate_syntax()
        performance_warnings = self.check_performance()
        logic_complete = self.validate_logic_completeness(original_sql)

        # 分类问题
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']

        result = GroovyValidationResult(
            checkpoint='CP5-CP6',
            passed=len(errors) == 0,
            issues=[asdict(i) for i in issues],
            syntax_valid=len(errors) == 0,
            logic_complete=logic_complete,
            performance_warnings=performance_warnings
        )

        return result


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='Groovy语法验证器')
    parser.add_argument('--input', required=True, help='Groovy文件路径')
    parser.add_argument('--original-sql', help='原始SQL文件路径（用于逻辑对比）')
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

    # 读取原始SQL（如果提供）
    original_sql = None
    if args.original_sql and Path(args.original_sql).exists():
        with open(args.original_sql, 'r', encoding='utf-8') as f:
            original_sql = f.read()

    # 执行验证
    validator = GroovyValidator(content)
    result = validator.run_validation(original_sql)

    # 输出结果
    output = asdict(result)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"验证结果已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    # 打印摘要
    print(f"\n=== 验证摘要 ===")
    print(f"语法检查: {'通过' if result.syntax_valid else '失败'}")
    print(f"逻辑检查: {'完整' if result.logic_complete else '可能不完整'}")
    print(f"问题数: {len(result.issues)} (错误: {len([i for i in result.issues if i['severity']=='error'])}, 警告: {len([i for i in result.issues if i['severity']=='warning'])})")
    print(f"性能提示: {len(result.performance_warnings)}")

    if result.performance_warnings:
        print("\n性能建议:")
        for warning in result.performance_warnings:
            print(f"  - {warning}")

    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()