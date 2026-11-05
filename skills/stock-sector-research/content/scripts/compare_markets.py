#!/usr/bin/env python3
"""
Cross-Market Comparator
Compare sectors across A-share, HK, and US markets
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class CrossMarketComparator:
    """Compare stock sectors across different markets"""

    def __init__(self):
        self.markets = ["A", "HK", "US"]
        self.sector_mappings = self._load_sector_mappings()

    def _load_sector_mappings(self) -> Dict:
        """
        Load cross-market sector mappings
        Maps equivalent sectors across markets
        """
        return {
            "Technology": {
                "A": "电子元件|计算机应用|通信设备",
                "HK": "资讯科技业",
                "US": "XLK"
            },
            "HealthCare": {
                "A": "医疗器械|化学制药|生物制品",
                "HK": "医疗保健业",
                "US": "XLV"
            },
            "Financials": {
                "A": "银行|证券|保险",
                "HK": "金融业",
                "US": "XLF"
            },
            "ConsumerDiscretionary": {
                "A": "汽车|家电|旅游",
                "HK": "非必需消费",
                "US": "XLY"
            },
            "ConsumerStaples": {
                "A": "食品饮料|农林牧渔",
                "HK": "必需消费",
                "US": "XLP"
            },
            "Energy": {
                "A": "石油开采|煤炭开采",
                "HK": "能源业",
                "US": "XLE"
            },
            "Industrials": {
                "A": "机械设备|电气设备|军工",
                "HK": "工业",
                "US": "XLI"
            },
            "Materials": {
                "A": "化工|钢铁|有色金属",
                "HK": "原材料业",
                "US": "XLB"
            },
            "Utilities": {
                "A": "电力|燃气|水务",
                "HK": "公用事业",
                "US": "XLU"
            },
            "RealEstate": {
                "A": "房地产开发|物业管理",
                "HK": "地产建筑业",
                "US": "XLRE"
            },
            "CommunicationServices": {
                "A": "通信服务|传媒",
                "HK": "电讯业",
                "US": "XLC"
            }
        }

    def fetch_cross_market_data(self, sector_name: str) -> Dict:
        """
        Fetch sector data across all markets
        """
        data = {
            "sector": sector_name,
            "timestamp": datetime.now().isoformat(),
            "markets": {}
        }

        if sector_name not in self.sector_mappings:
            return data

        mapping = self.sector_mappings[sector_name]

        for market in self.markets:
            if market in mapping:
                data["markets"][market] = {
                    "sector_codes": mapping[market],
                    "pe_ttm": 0.0,
                    "pe_percentile": 0,
                    "pb": 0.0,
                    "roe": 0.0,
                    "dividend_yield": 0.0,
                    "market_cap_total": 0.0,
                    "currency": "CNY" if market == "A" else ("HKD" if market == "HK" else "USD")
                }

        return data

    def compare_valuations(self, sector_name: str) -> Dict:
        """
        Compare valuations across markets
        """
        data = self.fetch_cross_market_data(sector_name)

        comparison = {
            "sector": sector_name,
            "comparison_date": datetime.now().strftime("%Y-%m-%d"),
            "markets": {},
            "analysis": {
                "pe_analysis": "",
                "pb_analysis": "",
                "recommendation": ""
            }
        }

        # Extract valuation data
        valuations = {}
        for market, market_data in data["markets"].items():
            valuations[market] = {
                "pe": market_data["pe_ttm"],
                "pe_percentile": market_data["pe_percentile"],
                "pb": market_data["pb"]
            }

        comparison["markets"] = valuations

        # Analyze valuation differences
        pe_values = [v["pe"] for v in valuations.values() if v["pe"] > 0]
        if pe_values:
            avg_pe = sum(pe_values) / len(pe_values)
            min_pe_market = min(valuations.items(), key=lambda x: x[1]["pe"] if x[1]["pe"] > 0 else float('inf'))
            max_pe_market = max(valuations.items(), key=lambda x: x[1]["pe"] if x[1]["pe"] > 0 else 0)

            comparison["analysis"]["pe_analysis"] = (
                f"估值最低: {min_pe_market[0]}市场 (PE: {min_pe_market[1]['pe']:.1f}x), "
                f"估值最高: {max_pe_market[0]}市场 (PE: {max_pe_market[1]['pe']:.1f}x)"
            )

            # Generate recommendation
            comparison["analysis"]["recommendation"] = f"估值套利机会: 关注{min_pe_market[0]}市场低估值标的"

        return comparison

    def analyze_correlation(self, sector_name: str, period: int = 30) -> Dict:
        """
        Analyze correlation between markets for a sector
        """
        analysis = {
            "sector": sector_name,
            "period_days": period,
            "correlations": {
                "A_HK": 0.0,
                "A_US": 0.0,
                "HK_US": 0.0
            },
            "interpretation": ""
        }

        # Placeholder for actual correlation calculation
        # In production, fetch price data and calculate returns correlation

        # Generate interpretation
        avg_corr = sum(analysis["correlations"].values()) / len(analysis["correlations"])
        if avg_corr > 0.7:
            analysis["interpretation"] = "跨市场高度联动，可参考外围市场走势"
        elif avg_corr > 0.4:
            analysis["interpretation"] = "跨市场联动性中等，走势分化时可关注套利机会"
        else:
            analysis["interpretation"] = "跨市场联动性较弱，各自独立运行"

        return analysis

    def generate_comparison_report(self, sector_name: str) -> Dict:
        """
        Generate comprehensive cross-market comparison report
        """
        report = {
            "sector": sector_name,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "valuation_comparison": self.compare_valuations(sector_name),
            "correlation_analysis": self.analyze_correlation(sector_name),
            "recommendations": []
        }

        # Generate actionable recommendations
        valuation = report["valuation_comparison"]["analysis"]
        correlation = report["correlation_analysis"]["interpretation"]

        report["recommendations"] = [
            valuation.get("recommendation", ""),
            correlation
        ]

        return report


def main():
    comparator = CrossMarketComparator()

    # Example: Compare Technology sector
    report = comparator.generate_comparison_report("Technology")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
