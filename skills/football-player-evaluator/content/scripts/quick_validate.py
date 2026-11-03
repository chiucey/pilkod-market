"""
快速验证脚本 - 验证足球评测技能的数据格式和结构

此脚本用于验证用户输入的评测数据是否符合规范。
"""

import json
import sys
from typing import Dict, List, Tuple


class EvaluationValidator:
    """评测数据验证器"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_basic_info(self, data: Dict) -> bool:
        """验证基本信息"""
        required_fields = ['name', 'gender', 'age', 'grade']

        for field in required_fields:
            if field not in data:
                self.errors.append(f"缺少必填字段: {field}")
                return False

        # 验证性别
        if data.get('gender') not in ['男', '女', 'M', 'F', 'male', 'female']:
            self.warnings.append(f"性别字段值 '{data.get('gender')}' 不标准，建议使用 '男' 或 '女'")

        # 验证年龄
        age = data.get('age')
        if age is not None:
            try:
                age_int = int(age)
                if age_int < 10 or age_int > 20:
                    self.warnings.append(f"年龄 {age_int} 不在常规初中生范围内(10-20岁)")
            except (ValueError, TypeError):
                self.errors.append(f"年龄字段格式错误: {age}")
                return False

        # 验证年级
        grade = data.get('grade', '')
        if grade and grade not in ['初一', '初二', '初三', '七年级', '八年级', '九年级', '7', '8', '9']:
            self.warnings.append(f"年级字段值 '{grade}' 可能不标准")

        return True

    def validate_physical_test(self, data: Dict) -> bool:
        """验证体能测试数据"""
        physical_fields = {
            'sprint_50m': {'min': 5.0, 'max': 15.0, 'unit': '秒'},
            'run_800m_1000m': {'min': 120, 'max': 600, 'unit': '秒'},
            'standing_long_jump': {'min': 100, 'max': 350, 'unit': '厘米'},
            'sit_and_reach': {'min': -20, 'max': 40, 'unit': '厘米'},
            'dribble_around_poles': {'min': 5.0, 'max': 20.0, 'unit': '秒'}
        }

        for field, specs in physical_fields.items():
            if field in data:
                value = data[field]
                try:
                    value_float = float(value)
                    if value_float < specs['min'] or value_float > specs['max']:
                        self.warnings.append(
                            f"{field} 数值 {value_float}{specs['unit']} 超出合理范围 "
                            f"({specs['min']}-{specs['max']}{specs['unit']})"
                        )
                except (ValueError, TypeError):
                    self.errors.append(f"{field} 字段格式错误: {value}")

        return len(self.errors) == 0

    def validate_technical_test(self, data: Dict) -> bool:
        """验证技术测试数据"""
        technical_fields = {
            'toe_ball_control': {'min': 0, 'max': 100, 'unit': '次'},
            'pass_accuracy': {'min': 0, 'max': 10, 'unit': '次'},
            'shot_accuracy': {'min': 0, 'max': 5, 'unit': '次'},
            'tackle_success': {'min': 0, 'max': 5, 'unit': '次'}
        }

        for field, specs in technical_fields.items():
            if field in data:
                value = data[field]
                try:
                    value_int = int(value)
                    if value_int < specs['min'] or value_int > specs['max']:
                        self.warnings.append(
                            f"{field} 数值 {value_int}{specs['unit']} 超出合理范围 "
                            f"({specs['min']}-{specs['max']}{specs['unit']})"
                        )
                except (ValueError, TypeError):
                    self.errors.append(f"{field} 字段格式错误: {value}")

        return len(self.errors) == 0

    def validate_performance_score(self, score: float) -> bool:
        """验证比赛表现评分"""
        try:
            score_float = float(score)
            if score_float < 0 or score_float > 100:
                self.errors.append(f"比赛表现评分 {score_float} 超出范围 (0-100)")
                return False
        except (ValueError, TypeError):
            self.errors.append(f"比赛表现评分格式错误: {score}")
            return False
        return True

    def validate_athlete_data(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        验证完整运动员数据

        Args:
            data: 运动员评测数据字典

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        # 验证基本信息
        if 'basic_info' in data:
            self.validate_basic_info(data['basic_info'])
        else:
            self.errors.append("缺少 basic_info 部分")

        # 验证体能测试
        if 'physical_test' in data:
            self.validate_physical_test(data['physical_test'])

        # 验证技术测试
        if 'technical_test' in data:
            self.validate_technical_test(data['technical_test'])

        # 验证比赛表现
        if 'performance_score' in data:
            self.validate_performance_score(data['performance_score'])

        return len(self.errors) == 0, self.errors, self.warnings

    def validate_batch_data(self, data_list: List[Dict]) -> Dict:
        """
        验证批量运动员数据

        Args:
            data_list: 运动员数据列表

        Returns:
            验证结果统计
        """
        results = {
            'total': len(data_list),
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }

        for i, data in enumerate(data_list):
            passed, errors, warnings = self.validate_athlete_data(data)

            detail = {
                'index': i,
                'name': data.get('basic_info', {}).get('name', f'运动员{i+1}'),
                'passed': passed,
                'errors': errors,
                'warnings': warnings
            }

            results['details'].append(detail)

            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1

            if warnings:
                results['warnings'] += 1

        return results


def main():
    """主函数 - 命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法: python quick_validate.py <json_file>")
        print("或通过管道输入JSON数据")
        sys.exit(1)

    # 尝试从文件读取
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {sys.argv[1]}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式无效 - {e}")
        sys.exit(1)

    validator = EvaluationValidator()

    # 判断是单个还是批量数据
    if isinstance(data, list):
        results = validator.validate_batch_data(data)
        print("\n=== 批量验证结果 ===")
        print(f"总数: {results['total']}")
        print(f"通过: {results['passed']}")
        print(f"失败: {results['failed']}")
        print(f"有警告: {results['warnings']}")

        print("\n详细结果:")
        for detail in results['details']:
            status = "✓" if detail['passed'] else "✗"
            print(f"\n{status} {detail['name']}:")
            for error in detail['errors']:
                print(f"  错误: {error}")
            for warning in detail['warnings']:
                print(f"  警告: {warning}")
    else:
        passed, errors, warnings = validator.validate_athlete_data(data)
        print("\n=== 单条验证结果 ===")
        print(f"状态: {'通过 ✓' if passed else '失败 ✗'}")

        if errors:
            print("\n错误:")
            for error in errors:
                print(f"  - {error}")

        if warnings:
            print("\n警告:")
            for warning in warnings:
                print(f"  - {warning}")

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
