"""
分布式光伏自消纳比例测算报告生成器
Report Generator for PV Self-Consumption Ratio Calculation

功能：
1. 生成可视化分析图表
2. 生成Excel格式详细报告
3. 生成HTML格式网页报告
4. 支持多场景对比分析
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from io import BytesIO


class ReportGenerator:
    """报告生成器"""

    def __init__(self, report_data: Dict):
        """
        初始化报告生成器

        Args:
            report_data: 包含所有测算数据的字典
        """
        self.data = report_data

    def generate_text_report(self) -> str:
        """
        生成纯文本报告

        Returns:
            文本格式报告
        """
        lines = []
        lines.append("=" * 70)
        lines.append("          分布式光伏发电自消纳比例测算报告")
        lines.append("=" * 70)
        lines.append(f"报告生成时间: {self.data.get('report_info', {}).get('generated_at', '')}")
        lines.append("")

        # 项目基本信息
        lines.append("一、项目基本信息")
        lines.append("-" * 70)
        pv_params = self.data.get('pv_params', {})
        load_params = self.data.get('load_params', {})

        lines.append(f"  装机容量: {pv_params.get('installed_capacity', 0):.0f} kWp")
        lines.append(f"  系统效率: {pv_params.get('system_efficiency', 0)*100:.1f}%")
        lines.append(f"  年等效发电小时数: {pv_params.get('annual_equivalent_hours', 0):.0f} h")
        lines.append("")
        lines.append(f"  年用电量: {load_params.get('annual_consumption', 0):,.0f} kWh")
        lines.append(f"  最大需量: {load_params.get('max_demand', 0):.0f} kW")
        lines.append(f"  负荷率: {load_params.get('load_factor', 0)*100:.1f}%")
        lines.append("")

        # 发电量测算
        lines.append("二、发电量测算")
        lines.append("-" * 70)
        gen = self.data.get('generation_summary', {})

        lines.append(f"  年设计发电量: {gen.get('annual_generation', 0):,.0f} kWh")
        lines.append(f"  日均发电量: {gen.get('daily_average', 0):,.0f} kWh/天")
        lines.append("")

        # 月度发电分布
        lines.append("  月度发电量分布:")
        monthly = self.data.get('monthly_breakdown', [])
        if monthly:
            for m in monthly:
                lines.append(
                    f"    {m['month']:2d}月: {m['pv_generation']:>10,.0f} kWh "
                    f"(占比 {m.get('pv_ratio', 0)*100:.1f}%)"
                )
        lines.append("")

        # 自消纳测算结果
        lines.append("三、自消纳比例测算结果")
        lines.append("-" * 70)
        annual = self.data.get('annual_self_consumption', {})

        lines.append(f"  年光伏发电总量: {annual.get('annual_pv_generation', 0):,.0f} kWh")
        lines.append(f"  年自我消纳电量: {annual.get('annual_self_consumption', 0):,.0f} kWh")
        lines.append(f"  年余电上网电量: {annual.get('annual_surplus_to_grid', 0):,.0f} kWh")
        lines.append(f"  综合自消纳比例: {annual.get('annual_self_consumption_ratio', 0):.1f}%")
        lines.append("")
        lines.append(f"  工作日自消纳比例: {annual.get('workday_daily_ratio', 0):.1f}%")
        lines.append(f"  休息日自消纳比例: {annual.get('weekend_daily_ratio', 0):.1f}%")
        lines.append("")

        # 月度自消纳比例
        lines.append("  月度自消纳比例:")
        if monthly:
            for m in monthly:
                lines.append(
                    f"    {m['month']:2d}月: {m['self_consumption_ratio']:5.1f}% "
                    f"(消纳: {m['self_consumption']:>10,.0f} kWh, "
                    f"上网: {m['surplus_to_grid']:>10,.0f} kWh)"
                )
        lines.append("")

        # 经济性分析
        lines.append("四、经济性测算")
        lines.append("-" * 70)
        eco = self.data.get('economic_analysis', {})

        lines.append(f"  总投资: {eco.get('total_investment', 0):,.0f} 元")
        lines.append(f"  年综合收益: {eco.get('annual_revenue', 0):,.0f} 元/年")
        lines.append(f"  年电费节省: {eco.get('annual_savings', 0):,.0f} 元/年")
        lines.append(f"  静态投资回收期: {eco.get('simple_payback_years', 0):.1f} 年")
        lines.append(f"  25年总收益: {eco.get('total_25y_revenue', 0):,.0f} 元")
        lines.append(f"  25年IRR: {eco.get('irr_25y', 0):.1f}%")
        lines.append("")

        # 优化建议
        lines.append("五、优化建议")
        lines.append("-" * 70)
        recommendations = self.data.get('recommendations', [])

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
        else:
            lines.append("  暂无优化建议")
        lines.append("")

        lines.append("=" * 70)
        lines.append("                         报告结束")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_excel_report(self, output_path: str) -> bool:
        """
        生成Excel格式报告

        Args:
            output_path: 输出文件路径

        Returns:
            是否生成成功
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 汇总表
                summary_data = {
                    '指标': ['装机容量(kWp)', '系统效率', '年等效发电小时数',
                            '年设计发电量(kWh)', '年自我消纳电量(kWh)',
                            '年余电上网电量(kWh)', '综合自消纳比例(%)',
                            '总投资(元)', '年收益(元)', '投资回收期(年)'],
                    '数值': [
                        self.data.get('pv_params', {}).get('installed_capacity', 0),
                        f"{self.data.get('pv_params', {}).get('system_efficiency', 0)*100:.1f}%",
                        self.data.get('pv_params', {}).get('annual_equivalent_hours', 0),
                        self.data.get('generation_summary', {}).get('annual_generation', 0),
                        self.data.get('annual_self_consumption', {}).get('annual_self_consumption', 0),
                        self.data.get('annual_self_consumption', {}).get('annual_surplus_to_grid', 0),
                        self.data.get('annual_self_consumption', {}).get('annual_self_consumption_ratio', 0),
                        self.data.get('economic_analysis', {}).get('total_investment', 0),
                        self.data.get('economic_analysis', {}).get('annual_revenue', 0),
                        self.data.get('economic_analysis', {}).get('simple_payback_years', 0)
                    ]
                }
                pd.DataFrame(summary_data).to_excel(
                    writer, sheet_name='汇总', index=False, startrow=2
                )

                # 月度测算表
                monthly_df = pd.DataFrame(self.data.get('monthly_breakdown', []))
                if not monthly_df.empty:
                    monthly_df.to_excel(writer, sheet_name='月度测算', index=False)

                # 建议表
                recommendations = self.data.get('recommendations', [])
                if recommendations:
                    rec_df = pd.DataFrame({
                        '序号': range(1, len(recommendations) + 1),
                        '优化建议': recommendations
                    })
                    rec_df.to_excel(writer, sheet_name='优化建议', index=False)

            return True

        except Exception as e:
            print(f"生成Excel报告失败: {e}")
            return False

    def generate_json_report(self) -> str:
        """
        生成JSON格式报告

        Returns:
            JSON格式报告字符串
        """
        return json.dumps(self.data, indent=2, ensure_ascii=False)


class ScenarioComparator:
    """多场景对比分析器"""

    def __init__(self):
        self.scenarios = {}

    def add_scenario(self, name: str, report_data: Dict):
        """
        添加场景数据

        Args:
            name: 场景名称
            report_data: 场景数据
        """
        self.scenarios[name] = report_data

    def compare_scenarios(self) -> pd.DataFrame:
        """
        对比各场景

        Returns:
            对比结果 DataFrame
        """
        comparison = []

        for name, data in self.scenarios.items():
            annual = data.get('annual_self_consumption', {})
            eco = data.get('economic_analysis', {})

            comparison.append({
                '场景': name,
                '装机容量(kWp)': data.get('pv_params', {}).get('installed_capacity', 0),
                '年发电量(kWh)': annual.get('annual_pv_generation', 0),
                '自消纳电量(kWh)': annual.get('annual_self_consumption', 0),
                '自消纳比例(%)': annual.get('annual_self_consumption_ratio', 0),
                '余电上网(kWh)': annual.get('annual_surplus_to_grid', 0),
                '总投资(元)': eco.get('total_investment', 0),
                '年收益(元)': eco.get('annual_revenue', 0),
                '回收期(年)': eco.get('simple_payback_years', 0)
            })

        return pd.DataFrame(comparison)

    def generate_comparison_report(self) -> str:
        """
        生成对比分析报告

        Returns:
            对比报告文本
        """
        lines = []
        lines.append("=" * 70)
        lines.append("            多场景对比分析报告")
        lines.append("=" * 70)
        lines.append("")

        comparison_df = self.compare_scenarios()

        # 表格输出
        lines.append(comparison_df.to_string(index=False))
        lines.append("")

        # 最佳场景推荐
        if len(self.scenarios) > 0:
            best_payback = min(
                self.scenarios.items(),
                key=lambda x: x[1].get('economic_analysis', {}).get('simple_payback_years', float('inf'))
            )
            lines.append(f"推荐场景: {best_payback[0]}")
            lines.append(
                f"  - 投资回收期: {best_payback[1].get('economic_analysis', {}).get('simple_payback_years', 0):.1f} 年"
            )
            lines.append(
                f"  - 自消纳比例: {best_payback[1].get('annual_self_consumption', {}).get('annual_self_consumption_ratio', 0):.1f}%"
            )

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)


def export_report_summary(report_data: Dict, output_file: str, format: str = 'txt') -> bool:
    """
    导出报告摘要

    Args:
        report_data: 报告数据
        output_file: 输出文件路径
        format: 输出格式 ('txt', 'excel', 'json')

    Returns:
        是否成功
    """
    generator = ReportGenerator(report_data)

    if format == 'txt':
        content = generator.generate_text_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    elif format == 'excel':
        return generator.generate_excel_report(output_file)

    elif format == 'json':
        content = generator.generate_json_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


if __name__ == "__main__":
    # 示例数据
    sample_report = {
        "report_info": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pv_params": {
                "installed_capacity": 500,
                "system_efficiency": 0.82,
                "annual_equivalent_hours": 1200
            },
            "load_params": {
                "annual_consumption": 2000000,
                "max_demand": 800,
                "load_factor": 0.70
            }
        },
        "generation_summary": {
            "annual_generation": 492000,
            "daily_average": 1348
        },
        "annual_self_consumption": {
            "annual_pv_generation": 492000,
            "annual_self_consumption": 393600,
            "annual_surplus_to_grid": 98400,
            "annual_self_consumption_ratio": 80.0,
            "workday_daily_ratio": 85.0,
            "weekend_daily_ratio": 65.0
        },
        "monthly_breakdown": [
            {"month": m, "pv_generation": 41000, "self_consumption": 32800,
             "surplus_to_grid": 8200, "self_consumption_ratio": 80.0}
            for m in range(1, 13)
        ],
        "economic_analysis": {
            "total_investment": 2250000,
            "annual_revenue": 295200,
            "annual_savings": 236160,
            "simple_payback_years": 7.6,
            "total_25y_revenue": 7380000,
            "irr_25y": 12.5
        },
        "recommendations": [
            "自消纳比例较高，项目经济性良好",
            "建议优先推进建设"
        ]
    }

    generator = ReportGenerator(sample_report)
    print(generator.generate_text_report())
