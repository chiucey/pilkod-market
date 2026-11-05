#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金收益分析模块
基于持仓数据和净值数据计算各类收益指标
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class HoldingAnalysis:
    """单只基金持仓分析结果"""
    code: str
    name: str
    shares: float
    cost: float
    current_nav: float
    previous_nav: float

    # 市值相关
    market_value: float  # 当前市值
    cost_basis: float    # 成本金额

    # 收益相关
    daily_return: float      # 当日收益金额
    daily_return_pct: float   # 当日收益率
    total_return: float       # 累计收益金额
    total_return_pct: float   # 累计收益率

    # 配置相关
    allocation_pct: float     # 持仓占比


class ReturnsAnalyzer:
    """收益分析器"""

    def __init__(self, holdings: List[Dict]):
        """
        初始化分析器

        Args:
            holdings: 持仓数据列表
        """
        self.holdings = holdings
        self.analyses: List[HoldingAnalysis] = []
        self.total_analysis: Optional[Dict] = None

    def analyze(self, fund_data: Dict[str, Dict]) -> List[HoldingAnalysis]:
        """
        分析所有持仓基金的收益情况

        Args:
            fund_data: {基金代码: 净值数据} 字典

        Returns:
            分析结果列表
        """
        self.analyses = []
        total_market_value = 0
        total_cost_basis = 0

        for holding in self.holdings:
            code = holding.get("code", "")
            fund_info = fund_data.get(code, {})

            # 基本信息
            shares = holding.get("shares", 0)
            cost = holding.get("cost", 0)

            # 净值数据
            current_nav = fund_info.get("nav", 0)
            previous_nav = fund_info.get("previous_nav", 0)

            # 计算市值和成本
            market_value = current_nav * shares
            cost_basis = cost * shares

            # 计算收益
            daily_return = (current_nav - previous_nav) * shares
            daily_return_pct = ((current_nav / previous_nav) - 1) * 100 if previous_nav > 0 else 0

            total_return = market_value - cost_basis
            total_return_pct = ((market_value / cost_basis) - 1) * 100 if cost_basis > 0 else 0

            analysis = HoldingAnalysis(
                code=code,
                name=holding.get("name", fund_info.get("name", code)),
                shares=shares,
                cost=cost,
                current_nav=current_nav,
                previous_nav=previous_nav,
                market_value=market_value,
                cost_basis=cost_basis,
                daily_return=daily_return,
                daily_return_pct=daily_return_pct,
                total_return=total_return,
                total_return_pct=total_return_pct,
                allocation_pct=0  # 稍后计算
            )

            self.analyses.append(analysis)
            total_market_value += market_value
            total_cost_basis += cost_basis

        # 计算持仓占比
        for analysis in self.analyses:
            if total_market_value > 0:
                analysis.allocation_pct = (analysis.market_value / total_market_value) * 100

        # 计算汇总
        self.total_analysis = {
            "total_market_value": total_market_value,
            "total_cost_basis": total_cost_basis,
            "total_daily_return": sum(a.daily_return for a in self.analyses),
            "total_daily_return_pct": 0,
            "total_return": total_market_value - total_cost_basis,
            "total_return_pct": 0,
            "holding_count": len(self.analyses)
        }

        if total_cost_basis > 0:
            self.total_analysis["total_daily_return_pct"] = (
                self.total_analysis["total_daily_return"] /
                (total_market_value - self.total_analysis["total_daily_return"])
            ) * 100
            self.total_analysis["total_return_pct"] = (
                (total_market_value / total_cost_basis) - 1
            ) * 100

        return self.analyses

    def get_top_performers(self, n: int = 3) -> List[HoldingAnalysis]:
        """获取收益最高的N只基金"""
        return sorted(self.analyses, key=lambda x: x.total_return_pct, reverse=True)[:n]

    def get_bottom_performers(self, n: int = 3) -> List[HoldingAnalysis]:
        """获取收益最低的N只基金"""
        return sorted(self.analyses, key=lambda x: x.total_return_pct)[:n]

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": self.total_analysis,
            "holdings": [asdict(a) for a in self.analyses],
            "top_performers": [asdict(a) for a in self.get_top_performers()],
            "bottom_performers": [asdict(a) for a in self.get_bottom_performers()]
        }

    def format_summary(self) -> str:
        """生成文本摘要"""
        if not self.total_analysis:
            return "暂无分析数据"

        total = self.total_analysis
        date_str = datetime.now().strftime("%Y年%m月%d日")

        # 格式化数字
        def fmt_currency(x):
            return f"¥{x:,.2f}"

        def fmt_pct(x):
            sign = "+" if x >= 0 else ""
            return f"{sign}{x:.2f}%"

        lines = [
            f"📊 每日基金收益报表",
            f"📅 {date_str}",
            "",
            f"💰 总资产：{fmt_currency(total['total_market_value'])}",
            f"📈 今日收益：{fmt_currency(total['total_daily_return'])} ({fmt_pct(total['total_daily_return_pct'])})",
            f"💵 累计收益：{fmt_currency(total['total_return'])} ({fmt_pct(total['total_return_pct'])})",
            "",
            "【持仓明细】",
            "-" * 40
        ]

        for i, a in enumerate(sorted(self.analyses, key=lambda x: x.market_value, reverse=True), 1):
            lines.append(f"{i}. {a.name} ({a.code})")
            lines.append(f"   持有份额：{a.shares:.2f}份")
            lines.append(f"   今日收益：{fmt_currency(a.daily_return)} ({fmt_pct(a.daily_return_pct)})")
            lines.append(f"   累计收益：{fmt_currency(a.total_return)} ({fmt_pct(a.total_return_pct)})")
            lines.append(f"   持仓占比：{a.allocation_pct:.1f}%")
            lines.append("")

        return "\n".join(lines)


def load_portfolio(file_path: str) -> List[Dict]:
    """加载持仓配置"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("holdings", [])


def analyze_cli():
    """命令行入口"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python analyze_returns.py <持仓文件> <基金数据JSON>")
        sys.exit(1)

    portfolio_file = sys.argv[1]
    fund_data_file = sys.argv[2]

    # 加载数据
    holdings = load_portfolio(portfolio_file)
    with open(fund_data_file, 'r', encoding='utf-8') as f:
        fund_data = json.load(f)

    # 分析
    analyzer = ReturnsAnalyzer(holdings)
    analyzer.analyze(fund_data)

    # 输出
    print(analyzer.format_summary())

    # 保存分析结果
    output_file = f"data/analysis_{datetime.now().strftime('%Y%m%d')}.json"
    import os
    os.makedirs("data", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analyzer.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\n分析结果已保存到: {output_file}")


if __name__ == "__main__":
    analyze_cli()
