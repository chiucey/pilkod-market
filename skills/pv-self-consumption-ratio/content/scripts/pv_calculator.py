"""
分布式光伏发电自消纳比例计算引擎
PV Self-Consumption Ratio Calculator Engine

功能：
1. 基于企业用电负荷曲线计算光伏发电自消纳比例
2. 支持分时段、分季节的精细化测算
3. 输出详细的测算报告和经济性分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class PVProjectParams:
    """光伏项目参数"""
    installed_capacity: float  # 装机容量 (kWp)
    system_efficiency: float = 0.82  # 系统效率
    annual_equivalent_hours: float = 1200  # 年等效发电小时数
    installation_direction: str = "south"  # 安装朝向
    panel_tilt_angle: float = 25  # 组件倾角

    def __post_init__(self):
        if not 0 < self.system_efficiency <= 1:
            raise ValueError("系统效率必须在0-1之间")


@dataclass
class EnterpriseLoadParams:
    """企业用电参数"""
    annual_consumption: float  # 年用电量 (kWh)
    max_demand: float  # 最大需量 (kW)
    load_factor: float  # 负荷率
    peak_hours: List[int]  # 高峰时段 (小时)
    valley_hours: List[int]  # 低谷时段 (小时)
    flat_hours: List[int]  # 平段时段 (小时)


class PVSelfConsumptionCalculator:
    """分布式光伏自消纳比例计算器"""

    # 月度发电量分布比例（中国中部地区参考值）
    MONTHLY_GEN_RATIO = {
        1: 0.06, 2: 0.07, 3: 0.10, 4: 0.12,
        5: 0.11, 6: 0.11, 7: 0.12, 8: 0.11,
        9: 0.08, 10: 0.07, 11: 0.03, 12: 0.02
    }

    # 典型日光伏发电曲线系数（每小时的发电量占日发电量的比例）
    HOURLY_PV_CURVE = {
        0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00,
        4: 0.00, 5: 0.02, 6: 0.08, 7: 0.15,
        8: 0.22, 9: 0.28, 10: 0.32, 11: 0.33,
        12: 0.32, 13: 0.28, 14: 0.24, 15: 0.18,
        16: 0.12, 17: 0.06, 18: 0.02, 19: 0.00,
        20: 0.00, 21: 0.00, 22: 0.00, 23: 0.00
    }

    def __init__(self, pv_params: PVProjectParams, load_params: EnterpriseLoadParams):
        """
        初始化计算器

        Args:
            pv_params: 光伏项目参数
            load_params: 企业用电参数
        """
        self.pv_params = pv_params
        self.load_params = load_params

    def calculate_annual_generation(self) -> Dict[str, float]:
        """
        计算年度光伏发电量及分月分布

        Returns:
            包含年发电量和月发电量的字典
        """
        annual_gen = (
            self.pv_params.installed_capacity
            * self.pv_params.annual_equivalent_hours
            * self.pv_params.system_efficiency
        )

        monthly_gen = {
            month: annual_gen * ratio
            for month, ratio in self.MONTHLY_GEN_RATIO.items()
        }

        return {
            "annual_generation": annual_gen,
            "monthly_generation": monthly_gen,
            "daily_average": annual_gen / 365
        }

    def generate_typical_day_pv_curve(self) -> pd.DataFrame:
        """
        生成典型日光伏发电曲线

        Returns:
            24小时光伏发电曲线 DataFrame
        """
        daily_gen = (
            self.pv_params.installed_capacity
            * self.pv_params.annual_equivalent_hours
            * self.pv_params.system_efficiency
            / 365
        )

        hours = list(range(24))
        gen_values = [
            daily_gen * self.HOURLY_PV_CURVE[h]
            for h in hours
        ]

        df = pd.DataFrame({
            "hour": hours,
            "pv_generation": gen_values
        })

        df["pv_generation"] = df["pv_generation"].round(2)
        return df

    def generate_typical_enterprise_load_curve(
        self,
        workday_type: str = "workday"
    ) -> pd.DataFrame:
        """
        生成典型日企业负荷曲线

        Args:
            workday_type: 工作日类型 ('workday' 或 'weekend')

        Returns:
            24小时企业负荷曲线 DataFrame
        """
        base_load = self.load_params.annual_consumption / (365 * 24)

        if workday_type == "workday":
            # 工作日负荷曲线（制造业典型）
            hourly_ratios = {
                0: 0.50, 1: 0.48, 2: 0.50, 3: 0.52,
                4: 0.55, 5: 0.60, 6: 0.70, 7: 0.85,
                8: 0.95, 9: 1.00, 10: 1.00, 11: 0.98,
                12: 0.85, 13: 0.90, 14: 1.00, 15: 1.00,
                16: 0.98, 17: 0.90, 18: 0.75, 19: 0.60,
                20: 0.55, 21: 0.52, 22: 0.50, 23: 0.48
            }
        else:
            # 休息日负荷曲线
            hourly_ratios = {
                0: 0.40, 1: 0.38, 2: 0.40, 3: 0.42,
                4: 0.45, 5: 0.48, 6: 0.55, 7: 0.60,
                8: 0.65, 9: 0.70, 10: 0.75, 11: 0.78,
                12: 0.80, 13: 0.82, 14: 0.80, 15: 0.78,
                16: 0.75, 17: 0.70, 18: 0.65, 19: 0.55,
                20: 0.50, 21: 0.45, 22: 0.42, 23: 0.40
            }

        hours = list(range(24))
        load_values = [
            self.load_params.max_demand * hourly_ratios[h]
            for h in hours
        ]

        df = pd.DataFrame({
            "hour": hours,
            "enterprise_load": load_values
        })

        df["enterprise_load"] = df["enterprise_load"].round(2)
        return df

    def calculate_hourly_self_consumption(
        self,
        workday_type: str = "workday"
    ) -> pd.DataFrame:
        """
        计算每小时的自消纳情况

        Args:
            workday_type: 工作日类型

        Returns:
            包含各时段消纳情况的 DataFrame
        """
        pv_curve = self.generate_typical_day_pv_curve()
        load_curve = self.generate_typical_enterprise_load_curve(workday_type)

        df = pd.merge(pv_curve, load_curve, on="hour")

        # 计算自消纳和余电上网
        df["self_consumption"] = df.apply(
            lambda row: min(row["pv_generation"], row["enterprise_load"]),
            axis=1
        )
        df["surplus_to_grid"] = df.apply(
            lambda row: max(0, row["pv_generation"] - row["enterprise_load"]),
            axis=1
        )
        df["curtailment"] = 0.0  # 假设无弃光

        df["self_consumption_ratio"] = (
            df["self_consumption"] / df["pv_generation"].replace(0, np.nan)
        ).fillna(0)

        return df

    def calculate_daily_self_consumption(
        self,
        workday_type: str = "workday"
    ) -> Dict[str, float]:
        """
        计算典型日自消纳总量

        Args:
            workday_type: 工作日类型

        Returns:
            典型日发电和消纳统计
        """
        hourly_df = self.calculate_hourly_self_consumption(workday_type)

        total_pv_gen = hourly_df["pv_generation"].sum()
        total_self_consumption = hourly_df["self_consumption"].sum()
        total_surplus = hourly_df["surplus_to_grid"].sum()

        daily_self_ratio = (
            total_self_consumption / total_pv_gen if total_pv_gen > 0 else 0
        )

        return {
            "total_pv_generation": round(total_pv_gen, 2),
            "total_self_consumption": round(total_self_consumption, 2),
            "total_surplus_to_grid": round(total_surplus, 2),
            "daily_self_consumption_ratio": round(daily_self_ratio * 100, 2)
        }

    def calculate_annual_self_consumption(
        self,
        workdays_per_year: int = 250
    ) -> Dict[str, float]:
        """
        计算年度自消纳比例

        Args:
            workdays_per_year: 年工作日数，默认250天

        Returns:
            年度发电和消纳统计
        """
        weekend_days = 365 - workdays_per_year

        # 计算工作日总量
        workday_stats = self.calculate_daily_self_consumption("workday")
        weekend_stats = self.calculate_daily_self_consumption("weekend")

        annual_pv_gen = (
            workday_stats["total_pv_generation"] * workdays_per_year
            + weekend_stats["total_pv_generation"] * weekend_days
        )

        annual_self_consumption = (
            workday_stats["total_self_consumption"] * workdays_per_year
            + weekend_stats["total_self_consumption"] * weekend_days
        )

        annual_surplus = (
            workday_stats["total_surplus_to_grid"] * workdays_per_year
            + weekend_stats["total_surplus_to_grid"] * weekend_days
        )

        annual_self_ratio = (
            annual_self_consumption / annual_pv_gen if annual_pv_gen > 0 else 0
        )

        return {
            "annual_pv_generation": round(annual_pv_gen, 2),
            "annual_self_consumption": round(annual_self_consumption, 2),
            "annual_surplus_to_grid": round(annual_surplus, 2),
            "annual_self_consumption_ratio": round(annual_self_ratio * 100, 2),
            "workday_daily_ratio": workday_stats["daily_self_consumption_ratio"],
            "weekend_daily_ratio": weekend_stats["daily_self_consumption_ratio"]
        }

    def calculate_monthly_self_consumption(self) -> pd.DataFrame:
        """
        计算月度自消纳比例

        Returns:
            12个月的自消纳数据 DataFrame
        """
        results = []

        for month in range(1, 13):
            # 根据月份确定工作日数估算
            if month in [2]:
                workdays = 19
            elif month in [7, 8]:
                workdays = 21
            else:
                workdays = 22

            weekend_days = {
                1: 10, 2: 8, 3: 9, 4: 8, 5: 10,
                6: 9, 7: 8, 8: 10, 9: 9, 10: 8, 11: 9, 12: 10
            }[month]

            workday_stats = self.calculate_daily_self_consumption("workday")
            weekend_stats = self.calculate_daily_self_consumption("weekend")

            month_pv_gen = (
                workday_stats["total_pv_generation"] * workdays
                + weekend_stats["total_pv_generation"] * weekend_days
            )

            month_self_consumption = (
                workday_stats["total_self_consumption"] * workdays
                + weekend_stats["total_self_consumption"] * weekend_days
            )

            month_surplus = (
                workday_stats["total_surplus_to_grid"] * workdays
                + weekend_stats["total_surplus_to_grid"] * weekend_days
            )

            month_ratio = (
                month_self_consumption / month_pv_gen * 100
                if month_pv_gen > 0 else 0
            )

            results.append({
                "month": month,
                "pv_generation": round(month_pv_gen, 2),
                "self_consumption": round(month_self_consumption, 2),
                "surplus_to_grid": round(month_surplus, 2),
                "self_consumption_ratio": round(month_ratio, 2)
            })

        return pd.DataFrame(results)

    def calculate_economic_analysis(
        self,
        self_consumption_price: float = 0.60,
        surplus_price: float = 0.35,
        feed_in_tariff: float = 0.10,
        investment_cost: float = 4500
    ) -> Dict[str, float]:
        """
        计算项目经济性

        Args:
            self_consumption_price: 自消纳电价 (元/kWh)
            surplus_price: 余电上网电价 (元/kWh)
            feed_in_tariff: 国家补贴 (元/kWh)
            investment_cost: 单位投资成本 (元/kWp)

        Returns:
            经济性分析结果
        """
        annual_stats = self.calculate_annual_self_consumption()

        annual_revenue = (
            annual_stats["annual_self_consumption"] * self_consumption_price
            + annual_stats["annual_surplus_to_grid"] * surplus_price
            + annual_stats["annual_pv_generation"] * feed_in_tariff
        )

        total_investment = self.pv_params.installed_capacity * investment_cost

        simple_payback = total_investment / annual_revenue if annual_revenue > 0 else float('inf')

        annual_savings = annual_stats["annual_self_consumption"] * self_consumption_price

        # 计算25年总收益（考虑组件衰减）
        total_25y_revenue = 0
        for year in range(1, 26):
            degradation = (1 - 0.005) ** year  # 年衰减0.5%
            year_revenue = annual_revenue * degradation
            total_25y_revenue += year_revenue

        return {
            "total_investment": round(total_investment, 2),
            "annual_revenue": round(annual_revenue, 2),
            "annual_savings": round(annual_savings, 2),
            "simple_payback_years": round(simple_payback, 1),
            "total_25y_revenue": round(total_25y_revenue, 2),
            "irr_25y": round((total_25y_revenue / total_investment - 1) * 100, 2) if total_investment > 0 else 0
        }

    def generate_full_report(self) -> Dict:
        """
        生成完整的测算报告

        Returns:
            包含所有测算结果的字典
        """
        annual_stats = self.calculate_annual_self_consumption()
        monthly_df = self.calculate_monthly_self_consumption()
        economic = self.calculate_economic_analysis()

        report = {
            "report_info": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pv_params": {
                    "installed_capacity": self.pv_params.installed_capacity,
                    "system_efficiency": self.pv_params.system_efficiency,
                    "annual_equivalent_hours": self.pv_params.annual_equivalent_hours
                },
                "load_params": {
                    "annual_consumption": self.load_params.annual_consumption,
                    "max_demand": self.load_params.max_demand,
                    "load_factor": self.load_params.load_factor
                }
            },
            "generation_summary": self.calculate_annual_generation(),
            "annual_self_consumption": annual_stats,
            "monthly_breakdown": monthly_df.to_dict(orient="records"),
            "economic_analysis": economic,
            "recommendations": self._generate_recommendations(annual_stats, economic)
        }

        return report

    def _generate_recommendations(
        self,
        annual_stats: Dict,
        economic: Dict
    ) -> List[str]:
        """
        生成优化建议

        Args:
            annual_stats: 年度统计
            economic: 经济性分析

        Returns:
            优化建议列表
        """
        recommendations = []

        self_ratio = annual_stats["annual_self_consumption_ratio"]

        if self_ratio < 50:
            recommendations.append(
                f"自消纳比例({self_ratio}%)偏低，建议考虑储能系统以提升自消纳率"
            )

        if self_ratio > 80:
            recommendations.append(
                "自消纳比例较高，可考虑适当增加装机容量"
            )

        if economic["simple_payback_years"] > 8:
            recommendations.append(
                "投资回收期较长，建议优化项目方案或争取更优惠的电价政策"
            )
        else:
            recommendations.append(
                "项目经济性良好，建议加快推进建设"
            )

        return recommendations


def load_load_curve_from_excel(file_path: str) -> pd.DataFrame:
    """
    从Excel文件加载负荷曲线数据

    Args:
        file_path: Excel文件路径

    Returns:
        负荷曲线 DataFrame
    """
    df = pd.read_excel(file_path)
    return df


def load_bill_data(file_path: str) -> Dict:
    """
    从Excel文件加载电费核查联数据

    Args:
        file_path: Excel文件路径

    Returns:
        电费数据字典
    """
    df = pd.read_excel(file_path)
    return df.to_dict(orient="records")


if __name__ == "__main__":
    # 示例计算
    pv_params = PVProjectParams(
        installed_capacity=500,  # 500kWp
        system_efficiency=0.82,
        annual_equivalent_hours=1200
    )

    load_params = EnterpriseLoadParams(
        annual_consumption=2000000,  # 200万kWh/年
        max_demand=800,  # 800kW
        load_factor=0.70,
        peak_hours=[9, 10, 11, 14, 15, 16],
        valley_hours=[23, 0, 1, 2, 3, 4, 5, 6],
        flat_hours=[7, 8, 12, 13, 17, 18, 19, 20, 21, 22]
    )

    calculator = PVSelfConsumptionCalculator(pv_params, load_params)

    # 输出结果
    report = calculator.generate_full_report()

    print("=" * 60)
    print("分布式光伏自消纳比例测算报告")
    print("=" * 60)

    print("\n【年度发电量】")
    gen = report["generation_summary"]
    print(f"  年发电量: {gen['annual_generation']:,.0f} kWh")
    print(f"  日均发电: {gen['daily_average']:,.0f} kWh/天")

    print("\n【年度自消纳测算】")
    annual = report["annual_self_consumption"]
    print(f"  光伏发电总量: {annual['annual_pv_generation']:,.0f} kWh")
    print(f"  自我消纳电量: {annual['annual_self_consumption']:,.0f} kWh")
    print(f"  余电上网电量: {annual['annual_surplus_to_grid']:,.0f} kWh")
    print(f"  自消纳比例: {annual['annual_self_consumption_ratio']}%")

    print("\n【经济性分析】")
    eco = report["economic_analysis"]
    print(f"  总投资: {eco['total_investment']:,.0f} 元")
    print(f"  年收益: {eco['annual_revenue']:,.0f} 元")
    print(f"  投资回收期: {eco['simple_payback_years']} 年")

    print("\n【优化建议】")
    for rec in report["recommendations"]:
        print(f"  - {rec}")

    print("\n" + "=" * 60)
