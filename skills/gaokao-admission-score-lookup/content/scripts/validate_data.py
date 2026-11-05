#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考录取分数线数据验证脚本

本脚本用于验证高考录取分数线数据的完整性、准确性和一致性。
确保数据符合官方标准，保障考生和家长的权益。

使用方法：
    python validate_data.py --input <数据文件路径> [--verbose]
    python validate_data.py --check-sources <数据目录路径>
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 尝试导入必要的库
try:
    import yaml
except ImportError:
    yaml = None


class DataValidationError(Exception):
    """数据验证异常类"""
    pass


class AdmissionScoreValidator:
    """高考录取分数线数据验证器"""

    # 有效年份范围
    VALID_YEARS = [2021, 2022, 2023, 2024, 2025]

    # 有效科类
    VALID_SUBJECT_TYPES = [
        '文科', '理科', '物理类', '历史类',
        '物理', '历史', '综合',
        '文理分科文科', '文理分科理科'
    ]

    # 各省满分标准（默认750分，部分省份可能有差异）
    FULL_SCORE_STANDARDS = {
        '750': ['全国卷', '新课标卷', '自主命题大部分省份'],
        '810': ['浙江'],  # 浙江高考改革后满分810
    }

    def __init__(self, verbose: bool = False):
        """初始化验证器

        Args:
            verbose: 是否输出详细验证信息
        """
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def log(self, message: str, level: str = 'info'):
        """输出日志信息

        Args:
            message: 日志消息
            level: 日志级别 (info/warning/error)
        """
        if level == 'error':
            self.errors.append(message)
            if self.verbose:
                print(f"[错误] {message}")
        elif level == 'warning':
            self.warnings.append(message)
            if self.verbose:
                print(f"[警告] {message}")
        else:
            if self.verbose:
                print(f"[信息] {message}")

    def validate_year(self, year: Any) -> Tuple[bool, str]:
        """验证年份字段

        Args:
            year: 年份数据

        Returns:
            (是否有效, 错误消息)
        """
        if year is None:
            return False, "年份不能为空"

        try:
            year_int = int(year)
            if year_int not in self.VALID_YEARS:
                return False, f"年份 {year_int} 不在有效范围 2021-2025 内"
            return True, ""
        except (ValueError, TypeError):
            return False, f"年份格式无效: {year}"

    def validate_score(self, score: Any, field_name: str,
                      max_possible: int = 750) -> Tuple[bool, str]:
        """验证分数字段

        Args:
            score: 分数数据
            field_name: 字段名称
            max_possible: 该省最高可能分数

        Returns:
            (是否有效, 错误消息)
        """
        if score is None:
            return False, f"{field_name} 不能为空"

        try:
            score_int = int(score)
            if score_int < 0:
                return False, f"{field_name} 不能为负数"
            if score_int > max_possible:
                return False, f"{field_name} ({score_int}) 超过该省最高分 {max_possible}"
            return True, ""
        except (ValueError, TypeError):
            return False, f"{field_name} 格式无效: {score}"

    def validate_subject_type(self, subject_type: Any) -> Tuple[bool, str]:
        """验证科类字段

        Args:
            subject_type: 科类数据

        Returns:
            (是否有效, 错误消息)
        """
        if not subject_type:
            return False, "科类不能为空"

        subject_str = str(subject_type).strip()
        if subject_str not in self.VALID_SUBJECT_TYPES:
            return False, f"科类 '{subject_str}' 不在有效范围内"

        return True, ""

    def validate_province(self, province: Any) -> Tuple[bool, str]:
        """验证省份字段

        Args:
            province: 省份数据

        Returns:
            (是否有效, 错误消息)
        """
        if not province:
            return False, "省份不能为空"

        # 简化验证：确保省份名称非空且去除空白
        province_str = str(province).strip()
        if len(province_str) < 2:
            return False, f"省份名称过短: {province_str}"

        return True, ""

    def validate_score_logical(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证分数逻辑一致性

        Args:
            data: 包含分数数据的字典

        Returns:
            (是否有效, 错误消息)
        """
        try:
            highest = int(data.get('highest_score', 0))
            lowest = int(data.get('lowest_score', 0))
            cutoff = int(data.get('provincial_cutoff', 0))

            # 最高分应大于等于最低分
            if highest < lowest:
                return False, f"最高分 ({highest}) 小于最低分 ({lowest})"

            # 最低分应大于等于省控线
            if lowest < cutoff:
                return False, f"最低分 ({lowest}) 低于省控线 ({cutoff})"

            # 最高分应大于省控线
            if highest < cutoff:
                return False, f"最高分 ({highest}) 低于省控线 ({cutoff})"

            return True, ""
        except (ValueError, TypeError) as e:
            return False, f"分数逻辑验证失败: {str(e)}"

    def validate_data_completeness(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证数据完整性

        Args:
            data: 待验证的数据字典

        Returns:
            (是否完整, 缺失字段列表)
        """
        required_fields = [
            'year', 'province', 'subject_type',
            'highest_score', 'lowest_score', 'provincial_cutoff'
        ]

        # 兼容中文字段名
        field_mappings = {
            '年份': 'year', '省份': 'province', '科类': 'subject_type',
            '最高分': 'highest_score', '最低分': 'lowest_score',
            '省控线': 'provincial_cutoff', '专业名称': 'major_name'
        }

        missing_fields = []

        for field in required_fields:
            # 检查英文字段名
            if field not in data or data[field] is None:
                # 检查可能的中文字段名
                chinese_field = [k for k, v in field_mappings.items()
                               if v == field and k in data]
                if not chinese_field or data.get(chinese_field[0]) is None:
                    missing_fields.append(field)

        return len(missing_fields) == 0, missing_fields

    def validate_single_record(self, record: Dict[str, Any],
                              record_index: int = 0) -> bool:
        """验证单条录取记录

        Args:
            record: 单条记录数据
            record_index: 记录索引（用于错误定位）

        Returns:
            是否通过验证
        """
        is_valid = True

        # 验证年份
        year_valid, year_msg = self.validate_year(record.get('year'))
        if not year_valid:
            self.log(f"记录 {record_index}: {year_msg}", 'error')
            is_valid = False

        # 验证省份
        province_valid, province_msg = self.validate_province(record.get('province'))
        if not province_valid:
            self.log(f"记录 {record_index}: {province_msg}", 'error')
            is_valid = False

        # 验证科类
        subject_valid, subject_msg = self.validate_subject_type(
            record.get('subject_type'))
        if not subject_valid:
            self.log(f"记录 {record_index}: {subject_msg}", 'error')
            is_valid = False

        # 验证最高分
        highest_valid, highest_msg = self.validate_score(
            record.get('highest_score'), '最高分')
        if not highest_valid:
            self.log(f"记录 {record_index}: {highest_msg}", 'error')
            is_valid = False

        # 验证最低分
        lowest_valid, lowest_msg = self.validate_score(
            record.get('lowest_score'), '最低分')
        if not lowest_valid:
            self.log(f"记录 {record_index}: {lowest_msg}", 'error')
            is_valid = False

        # 验证省控线
        cutoff_valid, cutoff_msg = self.validate_score(
            record.get('provincial_cutoff'), '省控线')
        if not cutoff_valid:
            self.log(f"记录 {record_index}: {cutoff_msg}", 'error')
            is_valid = False

        # 验证分数逻辑一致性
        if all([highest_valid, lowest_valid, cutoff_valid]):
            logic_valid, logic_msg = self.validate_score_logical(record)
            if not logic_valid:
                self.log(f"记录 {record_index}: {logic_msg}", 'error')
                is_valid = False

        return is_valid

    def validate_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证整个数据集

        Args:
            data: 数据集列表

        Returns:
            验证结果摘要
        """
        total_records = len(data)
        valid_records = 0
        invalid_records = 0
        incomplete_records = 0

        self.log(f"开始验证 {total_records} 条记录...")
        self.log("=" * 50)

        for idx, record in enumerate(data):
            # 检查完整性
            is_complete, missing = self.validate_data_completeness(record)
            if not is_complete:
                incomplete_records += 1
                self.log(
                    f"记录 {idx}: 数据不完整，缺失字段: {', '.join(missing)}",
                    'warning'
                )

            # 验证单条记录
            if self.validate_single_record(record, idx):
                valid_records += 1
            else:
                invalid_records += 1

        # 生成验证报告
        report = {
            'validation_time': self.validation_time,
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'incomplete_records': incomplete_records,
            'validation_passed': invalid_records == 0 and incomplete_records == 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy()
        }

        self.log("=" * 50)
        self.log("验证完成！")
        self.log(f"总计记录: {total_records}")
        self.log(f"有效记录: {valid_records}")
        self.log(f"无效记录: {invalid_records}")
        self.log(f"不完整记录: {incomplete_records}")

        if report['validation_passed']:
            self.log("验证结果: 通过 ✓", 'info')
        else:
            self.log("验证结果: 未通过 ✗", 'error')

        return report

    def generate_validation_report(self, report: Dict[str, Any],
                                   output_path: Optional[str] = None) -> str:
        """生成验证报告

        Args:
            report: 验证结果报告
            output_path: 输出文件路径（可选）

        Returns:
            报告内容字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append("高考录取分数线数据验证报告")
        lines.append("=" * 60)
        lines.append(f"验证时间: {report['validation_time']}")
        lines.append("")

        lines.append("【验证统计】")
        lines.append(f"  总记录数: {report['total_records']}")
        lines.append(f"  有效记录: {report['valid_records']}")
        lines.append(f"  无效记录: {report['invalid_records']}")
        lines.append(f"  不完整记录: {report['incomplete_records']}")
        lines.append("")

        lines.append(f"【验证结果】: {'通过 ✓' if report['validation_passed'] else '未通过 ✗'}")
        lines.append("")

        if report['errors']:
            lines.append("【错误详情】")
            for idx, error in enumerate(report['errors'], 1):
                lines.append(f"  {idx}. {error}")
            lines.append("")

        if report['warnings']:
            lines.append("【警告详情】")
            for idx, warning in enumerate(report['warnings'], 1):
                lines.append(f"  {idx}. {warning}")
            lines.append("")

        lines.append("=" * 60)

        report_content = "\n".join(lines)

        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.log(f"验证报告已保存至: {output_path}")
            except Exception as e:
                self.log(f"保存验证报告失败: {str(e)}", 'error')

        return report_content


def load_data(file_path: str) -> List[Dict[str, Any]]:
    """加载数据文件

    Args:
        file_path: 数据文件路径

    Returns:
        数据列表

    Raises:
        DataValidationError: 数据加载失败
    """
    if not os.path.exists(file_path):
        raise DataValidationError(f"文件不存在: {file_path}")

    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_ext in ['.json', '.jsonl']:
                return json.load(f)
            elif file_ext in ['.yaml', '.yml'] and yaml:
                return yaml.safe_load(f)
            elif file_ext in ['.csv']:
                # CSV 加载需要额外处理
                import csv
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    return list(reader)
            else:
                # 尝试作为 JSON 解析
                return json.load(f)
    except Exception as e:
        raise DataValidationError(f"加载数据失败: {str(e)}")


def check_sources_directory(directory_path: str) -> Dict[str, Any]:
    """检查数据源目录结构

    Args:
        directory_path: 数据目录路径

    Returns:
        检查结果
    """
    required_files = ['SKILL.md', '_meta.json']
    required_dirs = ['references', 'scripts']

    results = {
        'directory': directory_path,
        'files_found': [],
        'files_missing': [],
        'directories_found': [],
        'directories_missing': [],
        'overall_status': 'pass'
    }

    if not os.path.exists(directory_path):
        results['overall_status'] = 'fail'
        results['error'] = f"目录不存在: {directory_path}"
        return results

    # 检查必需文件
    for filename in required_files:
        filepath = os.path.join(directory_path, filename)
        if os.path.exists(filepath):
            results['files_found'].append(filename)
        else:
            results['files_missing'].append(filename)
            results['overall_status'] = 'fail'

    # 检查必需目录
    for dirname in required_dirs:
        dirpath = os.path.join(directory_path, dirname)
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            results['directories_found'].append(dirname)
        else:
            results['directories_missing'].append(dirname)
            results['overall_status'] = 'warning'

    return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='高考录取分数线数据验证工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python validate_data.py --input data/admission_scores.json --verbose
  python validate_data.py --check-sources ../gaokao-admission-score-lookup
        """
    )

    parser.add_argument(
        '--input', '-i',
        help='输入数据文件路径 (JSON/YAML/CSV)'
    )

    parser.add_argument(
        '--output', '-o',
        help='验证报告输出路径'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='输出详细验证信息'
    )

    parser.add_argument(
        '--check-sources', '-c',
        help='检查技能目录结构是否完整'
    )

    args = parser.parse_args()

    validator = AdmissionScoreValidator(verbose=args.verbose)

    # 检查技能目录结构
    if args.check_sources:
        print(f"检查技能目录: {args.check_sources}")
        print("=" * 50)
        results = check_sources_directory(args.check_sources)

        print(f"目录: {results['directory']}")
        print(f"状态: {results['overall_status']}")
        print("")

        if results['files_found']:
            print(f"已找到文件: {', '.join(results['files_found'])}")
        if results['files_missing']:
            print(f"缺失文件: {', '.join(results['files_missing'])}")
        if results['directories_found']:
            print(f"已找到目录: {', '.join(results['directories_found'])}")
        if results['directories_missing']:
            print(f"缺失目录: {', '.join(results['directories_missing'])}")

        return 0 if results['overall_status'] in ['pass', 'warning'] else 1

    # 验证数据文件
    if not args.input:
        parser.print_help()
        return 1

    try:
        print(f"加载数据文件: {args.input}")
        data = load_data(args.input)

        # 如果是单个字典，转换为列表
        if isinstance(data, dict):
            data = [data]

        # 执行验证
        report = validator.validate_dataset(data)

        # 生成报告
        report_content = validator.generate_validation_report(
            report,
            output_path=args.output
        )

        print("")
        print(report_content)

        return 0 if report['validation_passed'] else 1

    except DataValidationError as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"未知错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
