#!/usr/bin/env python3
"""
文件审查技能 - 模板验证脚本

验证模板配置文件是否符合规范。
"""

import json
import sys
from pathlib import Path


def validate_template(template_path: str) -> tuple[bool, list[str]]:
    """
    验证模板配置文件。

    Args:
        template_path: 模板文件路径

    Returns:
        (是否有效, 错误列表)
    """
    errors = []

    # 检查文件是否存在
    path = Path(template_path)
    if not path.exists():
        return False, [f"模板文件不存在: {template_path}"]

    # 尝试解析 JSON
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON 解析错误: {e}"]

    # 验证必填字段
    required_fields = ['template_name', 'file_type']
    for field in required_fields:
        if field not in template:
            errors.append(f"缺少必填字段: {field}")

    # 验证 file_type
    valid_file_types = ['excel', 'csv', 'json']
    if 'file_type' in template and template['file_type'] not in valid_file_types:
        errors.append(f"不支持的文件类型: {template['file_type']}，支持: {valid_file_types}")

    # 验证数据类型定义
    valid_data_types = ['string', 'number', 'date', 'datetime', 'boolean']
    if 'data_types' in template:
        for col, dtype in template['data_types'].items():
            if dtype not in valid_data_types:
                errors.append(f"不支持的数据类型 '{dtype}' for column '{col}'")

    # 验证跨文件规则
    if 'cross_file_rules' in template:
        for i, rule in enumerate(template['cross_file_rules']):
            if 'rule_name' not in rule:
                errors.append(f"规则 {i+1}: 缺少 rule_name")
            if 'validation_type' not in rule:
                errors.append(f"规则 '{rule.get('rule_name', i+1)}': 缺少 validation_type")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_template.py <模板文件路径>")
        sys.exit(1)

    template_path = sys.argv[1]
    is_valid, errors = validate_template(template_path)

    if is_valid:
        print("✓ 模板验证通过")
        sys.exit(0)
    else:
        print("✗ 模板验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
