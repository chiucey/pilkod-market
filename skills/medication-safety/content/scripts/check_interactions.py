#!/usr/bin/env python3
"""
药物相互作用检查脚本
用于检查药物之间的相互作用、禁忌食物和禁忌行为
"""

import json
import os
from typing import Dict, List, Any, Optional

class MedicationSafetyChecker:
    """用药安全检查器"""

    def __init__(self, database_path: str = None):
        """初始化检查器

        Args:
            database_path: 药物相互作用数据库路径
        """
        if database_path is None:
            # 默认路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            database_path = os.path.join(current_dir, '..', 'references', 'drug_interactions.json')

        self.database_path = database_path
        self.db = self._load_database()
        self.drug_data = self.db.get('drugs', {})

    def _load_database(self) -> Dict:
        """加载药物相互作用数据库"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"数据库文件未找到: {self.database_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"数据库文件格式错误: {e}")

    def _normalize_drug_name(self, drug_name: str) -> Optional[str]:
        """标准化药物名称

        Args:
            drug_name: 用户输入的药物名称

        Returns:
            标准化的药物名称，如果未找到返回None
        """
        drug_name = drug_name.strip().lower()

        # 首先检查是否直接匹配
        for standard_name in self.drug_data.keys():
            if standard_name.lower() == drug_name:
                return standard_name

            # 检查别名
            aliases = self.drug_data[standard_name].get('aliases', [])
            for alias in aliases:
                if alias.lower().strip() == drug_name or alias.lower().strip().replace(' ', '') == drug_name:
                    return standard_name

        return None

    def check_interactions(self, drugs: List[str]) -> Dict[str, Any]:
        """检查药物相互作用

        Args:
            drugs: 药物名称列表

        Returns:
            包含分析结果的字典
        """
        # 标准化药物名称
        normalized_drugs = []
        unknown_drugs = []

        for drug in drugs:
            normalized = self._normalize_drug_name(drug)
            if normalized:
                if normalized not in normalized_drugs:
                    normalized_drugs.append(normalized)
            else:
                if drug not in unknown_drugs:
                    unknown_drugs.append(drug)

        # 构建结果
        result = {
            'recognized_drugs': normalized_drugs,
            'unrecognized_drugs': unknown_drugs,
            'interactions': [],
            'forbidden_drugs': set(),
            'forbidden_foods': {},
            'forbidden_behaviors': {},
            'safety_level': 'safe',
            'warnings': []
        }

        # 检查药物对之间的相互作用
        for i, drug1 in enumerate(normalized_drugs):
            for drug2 in normalized_drugs[i+1:]:
                interaction = self._check_drug_pair(drug1, drug2)
                if interaction:
                    result['interactions'].append(interaction)
                    result['forbidden_drugs'].add(drug2)

        # 收集每种药物的禁忌食物和行为
        for drug in normalized_drugs:
            drug_info = self.drug_data[drug]

            # 禁忌食物
            forbidden_foods = drug_info.get('forbidden_foods', {})
            for category, info in forbidden_foods.items():
                if category not in result['forbidden_foods']:
                    result['forbidden_foods'][category] = {
                        'examples': info.get('examples', []),
                        'reason': info.get('reason', ''),
                        'note': info.get('note', '')
                    }

            # 禁忌行为
            forbidden_behaviors = drug_info.get('forbidden_behaviors', {})
            for behavior, info in forbidden_behaviors.items():
                if behavior not in result['forbidden_behaviors']:
                    result['forbidden_behaviors'][behavior] = {
                        'reason': info.get('reason', ''),
                        'recommendation': info.get('recommendation', '')
                    }

        # 确定安全级别
        result['forbidden_drugs'] = list(result['forbidden_drugs'])
        self._calculate_safety_level(result)

        return result

    def _check_drug_pair(self, drug1: str, drug2: str) -> Optional[Dict]:
        """检查两种药物之间的相互作用

        Args:
            drug1: 第一种药物
            drug2: 第二种药物

        Returns:
            相互作用信息，如果无相互作用返回None
        """
        drug1_info = self.drug_data.get(drug1, {}).get('interactions', {})
        drug2_info = self.drug_data.get(drug2, {}).get('interactions', {})

        # 检查drug1对drug2的反应
        for other_drug, interaction in drug1_info.items():
            if other_drug.lower() == drug2.lower():
                return {
                    'drugs': [drug1, drug2],
                    'risk_level': interaction.get('risk_level', '未知'),
                    'description': interaction.get('description', ''),
                    'recommendation': interaction.get('recommendation', '')
                }

        # 检查drug2对drug1的反应
        for other_drug, interaction in drug2_info.items():
            if other_drug.lower() == drug1.lower():
                return {
                    'drugs': [drug1, drug2],
                    'risk_level': interaction.get('risk_level', '未知'),
                    'description': interaction.get('description', ''),
                    'recommendation': interaction.get('recommendation', '')
                }

        return None

    def _calculate_safety_level(self, result: Dict) -> None:
        """计算整体安全级别

        Args:
            result: 检查结果字典
        """
        risk_levels = [i['risk_level'] for i in result['interactions']]

        if '严重' in risk_levels:
            result['safety_level'] = 'dangerous'
            result['warnings'].append('存在严重药物相互作用，必须立即咨询医生！')
        elif '高危' in risk_levels:
            result['safety_level'] = 'high_risk'
            result['warnings'].append('存在高危药物相互作用，请谨慎使用！')
        elif '中危' in risk_levels:
            result['safety_level'] = 'moderate'
            result['warnings'].append('存在中等风险相互作用，请密切监测！')
        elif result['interactions']:
            result['safety_level'] = 'low_risk'
            result['warnings'].append('存在低风险相互作用，注意观察！')
        else:
            result['safety_level'] = 'safe'

    def generate_report(self, drugs: List[str]) -> str:
        """生成用药安全分析报告

        Args:
            drugs: 药物名称列表

        Returns:
            格式化的报告文本
        """
        result = self.check_interactions(drugs)

        lines = []
        lines.append("=" * 60)
        lines.append("                    用药安全分析报告")
        lines.append("=" * 60)
        lines.append("")

        # 识别的药物
        lines.append("【已识别药物】")
        if result['recognized_drugs']:
            for drug in result['recognized_drugs']:
                lines.append(f"  - {drug}")
        else:
            lines.append("  未识别到有效药物")
        lines.append("")

        # 未识别的药物
        if result['unrecognized_drugs']:
            lines.append("【未识别药物】")
            lines.append("  以下药物不在数据库中，建议咨询医生或药师：")
            for drug in result['unrecognized_drugs']:
                lines.append(f"  - {drug}")
            lines.append("")

        # 药物相互作用
        lines.append("【药物相互作用检查】")
        if result['interactions']:
            for interaction in result['interactions']:
                risk_emoji = {
                    '严重': '🚨',
                    '高危': '⚠️',
                    '中危': '⚡',
                    '低危': 'ℹ️'
                }.get(interaction['risk_level'], '❓')

                lines.append(f"\n  {risk_emoji} {interaction['drugs'][0]} + {interaction['drugs'][1]}")
                lines.append(f"     风险等级: {interaction['risk_level']}")
                lines.append(f"     说明: {interaction['description']}")
                lines.append(f"     建议: {interaction['recommendation']}")
        else:
            lines.append("  ✓ 未发现药物相互作用")
        lines.append("")

        # 禁忌药物
        lines.append("【禁忌药物清单】")
        forbidden_drugs = [d for d in result['recognized_drugs'] if d not in [i['drugs'][1] for i in result['interactions']] + [i['drugs'][0] for i in result['interactions']]]

        # 从数据库中获取每种药物的禁忌药物
        all_forbidden = []
        for drug in result['recognized_drugs']:
            drug_interactions = self.drug_data.get(drug, {}).get('interactions', {})
            for other_drug, info in drug_interactions.items():
                if info.get('risk_level') in ['严重', '高危']:
                    if other_drug not in all_forbidden and other_drug not in result['recognized_drugs']:
                        all_forbidden.append(f"{drug} + {other_drug}: {info.get('description', '')[:50]}...")

        if all_forbidden:
            lines.append("  以下药物禁止与您当前服用的药物同时服用：")
            for item in all_forbidden:
                lines.append(f"  - {item}")
        else:
            lines.append("  未发现绝对禁忌药物")
        lines.append("")

        # 禁忌食物
        lines.append("【禁忌食物清单】")
        if result['forbidden_foods']:
            lines.append("  用药期间应避免以下食物：")
            for category, info in result['forbidden_foods'].items():
                examples = '、'.join(info['examples'][:5]) if info['examples'] else ''
                lines.append(f"\n  • {category}")
                if examples:
                    lines.append(f"    食物: {examples}")
                lines.append(f"    原因: {info['reason']}")
                if info.get('note'):
                    lines.append(f"    注意: {info['note']}")
        else:
            lines.append("  未发现特殊禁忌食物")
        lines.append("")

        # 禁忌行为
        lines.append("【禁忌行为清单】")
        if result['forbidden_behaviors']:
            lines.append("  用药期间应避免以下行为：")
            for behavior, info in result['forbidden_behaviors'].items():
                lines.append(f"\n  • {behavior}")
                lines.append(f"    原因: {info['reason']}")
                if info.get('recommendation'):
                    lines.append(f"    建议: {info['recommendation']}")
        else:
            lines.append("  未发现特殊禁忌行为")
        lines.append("")

        # 安全建议
        lines.append("【安全建议】")
        if result['safety_level'] in ['dangerous', 'high_risk']:
            lines.append("  ⚠️ 警告: 请立即咨询医生或药师后再用药！")
            lines.append("  在获得专业指导之前，不建议同时服用这些药物。")
        elif result['safety_level'] == 'moderate':
            lines.append("  ℹ️ 注意: 用药期间请密切观察身体反应。")
            lines.append("  如有不适，请立即就医。")
        else:
            lines.append("  ✓ 当前药物组合相对安全。")
            lines.append("  但仍请遵循正确的服药方式和注意事项。")

        lines.append("")
        lines.append("-" * 60)
        lines.append("  ⚕️ 免责声明")
        lines.append("  本报告仅供参考，不能替代医生的诊断和建议。")
        lines.append("  如有疑问，请咨询医生或药师。")
        lines.append("=" * 60)

        return '\n'.join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='药物相互作用检查工具')
    parser.add_argument('--drugs', nargs='+', help='要检查的药物名称')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    args = parser.parse_args()

    checker = MedicationSafetyChecker()

    if args.interactive:
        print("用药安全检查工具 - 交互模式")
        print("输入药物名称（用空格分隔），输入'退出'结束：")
        while True:
            user_input = input("\n请输入药物名称: ").strip()
            if user_input in ['退出', 'exit', 'q']:
                print("再见！")
                break
            if not user_input:
                continue
            drugs = user_input.split()
            print("\n" + checker.generate_report(drugs))
    elif args.drugs:
        print(checker.generate_report(args.drugs))
    else:
        # 默认测试
        print("用药安全检查工具 - 测试模式")
        test_drugs = ["华法林", "阿司匹林"]
        print(f"\n测试药物组合: {', '.join(test_drugs)}")
        print("\n" + checker.generate_report(test_drugs))


if __name__ == '__main__':
    main()
