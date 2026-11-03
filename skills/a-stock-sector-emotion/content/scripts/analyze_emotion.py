"""
A股板块情绪分析脚本
分析板块与大盘的情绪联动关系，生成复盘报告
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class MarketSentiment(Enum):
    """市场情绪状态"""
    STRONG = "强势市场"      # 上涨 + 放量
    WEAK = "弱势市场"        # 下跌 + 放量
    BULLISH = "多头市场"     # 上涨 + 缩量（谨慎乐观）
    BEARISH = "空头市场"     # 下跌 + 缩量（谨慎悲观）
    CONSOLIDATION = "震荡市"  # 成交量基本持平


class SectorCorrelation(Enum):
    """板块联动类型"""
    HIGH_SYNC = "高联动"      # β > 1.2
    NORMAL_SYNC = "同步"     # 0.8 ≤ β ≤ 1.2
    LOW_SYNC = "低联动"      # β < 0.8
    COUNTER_TREND = "逆势"    # β < 0
    LEADING = "领先大盘"     # 先于大盘启动
    LAGGING = "滞后大盘"      # 跟随大盘


@dataclass
class SectorAnalysis:
    """板块分析结果"""
    name: str
    change_percent: float
    correlation: str
    correlation_value: float
    capital_flow: float
    leading_stock: str
    leading_change: float
    limit_up_count: int = 0
    sentiment: str = ""
    interpretation: str = ""


@dataclass
class MarketAnalysis:
    """市场分析结果"""
    index_data: Dict
    sentiment: str
    sentiment_detail: Dict
    sector_analysis: List[SectorAnalysis]
    capital_flow_summary: Dict
    limit_up_analysis: Dict
    leading_sectors: List[str]
    lagging_sectors: List[str]
    independent_sectors: List[str]
    warnings: List[str]
    recommendations: List[str]


class EmotionAnalyzer:
    """A股情绪分析器"""

    # 情绪判断阈值
    UP_THRESHOLD = 0.5      # 上涨阈值（%）
    DOWN_THRESHOLD = -0.5   # 下跌阈值（%）
    VOLUME_EXPAND = 10      # 放量阈值（%）
    VOLUME_SHRINK = 15      # 缩量阈值（%）
    HIGH_BETA = 1.2         # 高联动阈值
    LOW_BETA = 0.8          # 低联动阈值
    MONEY_FLOW_POSITIVE = 50   # 资金涌入阈值（亿）
    MONEY_FLOW_NEGATIVE = -30   # 资金流出阈值（亿）

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.market_index = data.get("market_index", {})
        self.sector_ranking = data.get("sector_ranking", {})
        self.capital_flow = data.get("capital_flow", {})
        self.limit_up_down = data.get("limit_up_down", {})

    def analyze(self) -> MarketAnalysis:
        """
        执行完整的市场情绪分析
        """
        print("[情绪分析] 开始分析市场情绪...")

        # 1. 判断大盘情绪
        sentiment, sentiment_detail = self._analyze_market_sentiment()
        print(f"  - 大盘情绪: {sentiment}")

        # 2. 计算板块与大盘的相关性
        market_change = self._get_market_avg_change()
        sector_analysis = self._analyze_sector_correlation(market_change)
        print(f"  - 分析板块数: {len(sector_analysis)}")

        # 3. 资金流向分析
        capital_summary = self._analyze_capital_flow()
        print(f"  - 资金净流入: {capital_summary.get('total_net', 0):.1f}亿")

        # 4. 涨跌停分析
        limit_analysis = self._analyze_limit_up_down()
        print(f"  - 涨停数: {limit_analysis.get('total', 0)}")

        # 5. 分类板块
        leading, lagging, independent = self._classify_sectors(sector_analysis, market_change)

        # 6. 生成预警和建议
        warnings = self._generate_warnings(sector_analysis, sentiment)
        recommendations = self._generate_recommendations(sector_analysis, sentiment)

        return MarketAnalysis(
            index_data=self.market_index,
            sentiment=sentiment,
            sentiment_detail=sentiment_detail,
            sector_analysis=sector_analysis,
            capital_flow_summary=capital_summary,
            limit_up_analysis=limit_analysis,
            leading_sectors=leading,
            lagging_sectors=lagging,
            independent_sectors=independent,
            warnings=warnings,
            recommendations=recommendations
        )

    def _get_market_avg_change(self) -> float:
        """获取大盘平均涨跌幅"""
        changes = []
        for index_info in self.market_index.values():
            if isinstance(index_info, dict) and "change_percent" in index_info:
                changes.append(index_info["change_percent"])
        return sum(changes) / len(changes) if changes else 0.0

    def _analyze_market_sentiment(self) -> Tuple[str, Dict]:
        """
        分析大盘情绪状态
        基于量价结合原则
        """
        # 获取主要指数数据
        shangzheng = self.market_index.get("shangzheng", {})
        change = shangzheng.get("change_percent", 0)
        volume = shangzheng.get("volume", 0)

        # 与前一日成交量对比（简化处理：假设有前日数据）
        # 实际使用时需要加载历史数据进行对比
        volume_change = 5  # 模拟值，实际需要计算

        # 判断情绪
        if change > self.UP_THRESHOLD and volume_change > self.VOLUME_EXPAND:
            sentiment = MarketSentiment.STRONG.value
        elif change < self.DOWN_THRESHOLD and volume_change > self.VOLUME_EXPAND:
            sentiment = MarketSentiment.WEAK.value
        elif change > self.UP_THRESHOLD and volume_change < -self.VOLUME_SHRINK:
            sentiment = MarketSentiment.BULLISH.value
        elif change < self.DOWN_THRESHOLD and volume_change < -self.VOLUME_SHRINK:
            sentiment = MarketSentiment.BEARISH.value
        else:
            sentiment = MarketSentiment.CONSOLIDATION.value

        detail = {
            "change": change,
            "volume_change": volume_change,
            "volume_unit": "亿股",
            "description": self._get_sentiment_description(sentiment, change, volume_change)
        }

        return sentiment, detail

    def _get_sentiment_description(self, sentiment: str, change: float, volume_change: float) -> str:
        """获取情绪描述"""
        descriptions = {
            MarketSentiment.STRONG.value: f"指数上涨{change:.2f}%且成交量放大，场外资金积极入场",
            MarketSentiment.WEAK.value: f"指数下跌{abs(change):.2f}%且成交量放大，主力资金出逃明显",
            MarketSentiment.BULLISH.value: f"指数上涨{change:.2f}%但成交量萎缩，上涨动力可能不足",
            MarketSentiment.BEARISH.value: f"指数下跌{abs(change):.2f}%且成交量萎缩，卖压不重",
            MarketSentiment.CONSOLIDATION.value: f"指数涨跌{change:.2f}%，市场处于震荡整理"
        }
        return descriptions.get(sentiment, "市场情绪不明")

    def _analyze_sector_correlation(self, market_change: float) -> List[SectorAnalysis]:
        """
        分析板块与大盘的相关性
        """
        sectors = []

        # 合并行业和概念板块
        industry_sectors = self.sector_ranking.get("industry", [])
        concept_sectors = self.sector_ranking.get("concept", [])

        # 创建板块映射
        sector_map = {}
        for s in industry_sectors:
            sector_map[s["name"]] = s
        for s in concept_sectors:
            sector_map[s["name"]] = s

        # 创建资金流向映射
        flow_map = {}
        for flow in self.capital_flow.get("industry", []) + self.capital_flow.get("concept", []):
            flow_map[flow["name"]] = flow

        for name, sector in sector_map.items():
            change = sector.get("change_percent", 0)

            # 计算相关性（β值）
            if market_change != 0:
                beta = change / market_change
            else:
                beta = 1.0 if change > 0 else -1.0

            # 确定相关性类型
            if beta > self.HIGH_BETA:
                correlation = SectorCorrelation.HIGH_SYNC.value
            elif beta < 0:
                correlation = SectorCorrelation.COUNTER_TREND.value
            elif beta < self.LOW_BETA:
                correlation = SectorCorrelation.LOW_SYNC.value
            else:
                correlation = SectorCorrelation.NORMAL_SYNC.value

            # 获取资金流向
            flow_info = flow_map.get(name, {})
            capital_flow = flow_info.get("net_inflow", 0)

            # 判断情绪
            if change > 3 and capital_flow > 10:
                sentiment = "强势"
            elif change > 0 and capital_flow > 0:
                sentiment = "偏强"
            elif change < -2 and capital_flow < -10:
                sentiment = "弱势"
            elif change < 0 and capital_flow < 0:
                sentiment = "偏弱"
            else:
                sentiment = "中性"

            # 生成解读
            interpretation = self._interpret_sector(sector, correlation, beta, capital_flow)

            sectors.append(SectorAnalysis(
                name=name,
                change_percent=change,
                correlation=correlation,
                correlation_value=beta,
                capital_flow=capital_flow,
                leading_stock=sector.get("leading_stock", ""),
                leading_change=sector.get("leading_change", 0),
                limit_up_count=sector.get("limit_up_count", 0),
                sentiment=sentiment,
                interpretation=interpretation
            ))

        # 按涨跌幅排序
        sectors.sort(key=lambda x: x.change_percent, reverse=True)

        return sectors

    def _interpret_sector(self, sector: Dict, correlation: str, beta: float, capital_flow: float) -> str:
        """生成板块解读"""
        name = sector.get("name", "")
        change = sector.get("change_percent", 0)
        leading = sector.get("leading_stock", "")

        parts = []

        if beta > self.HIGH_BETA:
            parts.append(f"{name}今日涨幅达{change:.2f}%，波动性是大盘的{beta:.1f}倍，属于高联动板块")
        elif beta < 0:
            parts.append(f"{name}逆势上涨/下跌，与大盘走势相反")
        else:
            parts.append(f"{name}跟随大盘波动，相关性{beta:.2f}")

        if capital_flow > 30:
            parts.append(f"且获得主力资金净流入{capital_flow:.1f}亿")
        elif capital_flow < -20:
            parts.append(f"但遭到主力资金净流出{abs(capital_flow):.1f}亿")

        if sector.get("limit_up_count", 0) >= 5:
            parts.append(f"，板块内{sector['limit_up_count']}只个股涨停，情绪高涨")

        return "".join(parts)

    def _analyze_capital_flow(self) -> Dict:
        """分析资金流向"""
        industry_flow = self.capital_flow.get("industry", [])
        concept_flow = self.capital_flow.get("concept", [])

        # 找出资金流入和流出最多的板块
        all_flow = industry_flow + concept_flow
        sorted_flow = sorted(all_flow, key=lambda x: x.get("net_inflow", 0), reverse=True)

        return {
            "top_inflow": sorted_flow[:5],
            "top_outflow": sorted_flow[-5:] if len(sorted_flow) >= 5 else sorted_flow,
            "total_net": self.capital_flow.get("total_net_inflow", 0)
        }

    def _analyze_limit_up_down(self) -> Dict:
        """分析涨跌停情况"""
        limit_info = self.limit_up_down or {}

        return {
            "total": limit_info.get("total_limit_up", 0),
            "down": limit_info.get("total_limit_down", 0),
            "st_up": limit_info.get("st_limit_up", 0),
            "st_down": limit_info.get("st_limit_down", 0),
            "sector_detail": limit_info.get("sector_limit_up_count", {})
        }

    def _classify_sectors(self, sectors: List[SectorAnalysis], market_change: float) -> Tuple[List[str], List[str], List[str]]:
        """分类板块：领先、滞后、独立"""
        leading = []
        lagging = []
        independent = []

        for sector in sectors:
            change = sector.change_percent
            beta = sector.correlation_value

            # 判断独立性
            if abs(beta) < 0.3 and abs(change) > 1:
                independent.append(sector.name)
            elif change > 0 and market_change < 0 and beta < 0:
                # 逆势上涨
                leading.append(sector.name)
            elif sector.limit_up_count >= 5:
                # 涨停家数多，独立行情
                independent.append(sector.name)

        # 涨幅前5且与大盘联动
        top_rising = [s.name for s in sectors if s.change_percent > 1 and s.correlation_value >= 0.8][:5]
        bottom_rising = [s.name for s in sectors if s.change_percent < -1 and s.correlation_value >= 0.8][-5:]

        return top_rising, bottom_rising, independent[:10]

    def _generate_warnings(self, sectors: List[SectorAnalysis], sentiment: str) -> List[str]:
        """生成预警"""
        warnings = []

        # 板块异常预警
        counter_trend = [s for s in sectors if SectorCorrelation.COUNTER_TREND.value in s.correlation]
        if counter_trend:
            names = ", ".join([s.name for s in counter_trend[:3]])
            warnings.append(f"【异常】{names}出现逆势走势，需关注是否有独立逻辑")

        # 资金大幅流出预警
        heavy_outflow = [s for s in sectors if s.capital_flow < -20]
        if heavy_outflow:
            names = ", ".join([s.name for s in heavy_outflow[:3]])
            warnings.append(f"【警惕】{names}遭主力资金大幅流出，谨慎参与")

        # 市场情绪预警
        if MarketSentiment.WEAK.value in sentiment:
            warnings.append("【谨慎】市场整体偏弱，控制仓位为主")
        elif MarketSentiment.CONSOLIDATION.value in sentiment:
            warnings.append("【观望】市场震荡，等待方向明朗")

        return warnings

    def _generate_recommendations(self, sectors: List[SectorAnalysis], sentiment: str) -> List[str]:
        """生成建议"""
        recommendations = []

        # 强势板块推荐
        strong = [s for s in sectors if s.sentiment == "强势" and s.capital_flow > 20]
        if strong:
            names = ", ".join([s.name for s in strong[:3]])
            recommendations.append(f"【关注】{names}今日强势且获资金青睐，可重点关注")

        # 领先板块
        leading = [s for s in sectors if s.correlation_value > 1.5][:3]
        if leading:
            names = ", ".join([s.name for s in leading])
            recommendations.append(f"【布局】{names}领先大盘启动，可能有持续性行情")

        # 情绪建议
        if MarketSentiment.STRONG.value in sentiment:
            recommendations.append("【操作】市场强势，可适当增加仓位，顺势而为")
        elif MarketSentiment.BULLISH.value in sentiment:
            recommendations.append("【轻仓】上涨但量能不足，追高需谨慎")

        return recommendations


def generate_report(analysis: MarketAnalysis, session_type: str = "尾盘") -> str:
    """
    生成复盘报告
    session_type: "午盘" 或 "尾盘"
    """
    current_date = datetime.now().strftime("%Y年%m月%d日")
    current_time = datetime.now().strftime("%H:%M")

    report = f"""
# 【{current_date} {session_type}复盘报告】
> 生成时间：{current_time}

---

## 一、大盘情绪总览

"""

    # 添加指数数据
    for key, index in analysis.index_data.items():
        name = index.get("name", key)
        price = index.get("price", 0)
        change = index.get("change", 0)
        change_pct = index.get("change_percent", 0)
        volume = index.get("volume", 0) / 100000000  # 转换为亿股
        amount = index.get("amount", 0) / 100000000000  # 转换为亿元

        direction = "▲" if change > 0 else "▼" if change < 0 else "—"
        report += f"| {name} | {price:.2f} | {direction}{abs(change_pct):.2f}% | {volume:.1f}亿股 | {amount:.0f}亿 |\n"

    report += f"""
**综合情绪**：{analysis.sentiment}

情绪解读：{analysis.sentiment_detail.get('description', '')}

---

## 二、板块情绪联动分析

"""

    # 强势联动板块
    rising_sectors = [s for s in analysis.sector_analysis if s.change_percent > 1][:8]
    if rising_sectors:
        report += "### ▲ 强势上涨板块\n\n"
        for i, s in enumerate(rising_sectors, 1):
            flow_icon = "↑" if s.capital_flow > 0 else "↓"
            limit_icon = f" [{s.limit_up_count}只涨停]" if s.limit_up_count > 0 else ""
            report += f"{i}. **{s.name}** +{s.change_percent:.2f}% {flow_icon}{abs(s.capital_flow):.1f}亿{limit_icon}\n"
            report += f"   - 联动性：{s.correlation}（β={s.correlation_value:.2f}）\n"
            if s.leading_stock:
                report += f"   - 龙头股：{s.leading_stock}（{'+' if s.leading_change > 0 else ''}{s.leading_change:.1f}%）\n"
        report += "\n"

    # 弱势联动板块
    falling_sectors = [s for s in analysis.sector_analysis if s.change_percent < -0.5 and s.correlation_value > 0][:5]
    if falling_sectors:
        report += "### ▼ 弱势回调板块\n\n"
        for i, s in enumerate(falling_sectors, 1):
            flow_icon = "↑" if s.capital_flow > 0 else "↓"
            report += f"{i}. **{s.name}** {s.change_percent:.2f}% {flow_icon}{abs(s.capital_flow):.1f}亿\n"
            report += f"   - 解读：{s.interpretation}\n"
        report += "\n"

    # 独立走势板块
    if analysis.independent_sectors:
        report += "### ◇ 独立走势板块\n\n"
        report += f"以下板块走出独立行情，与大盘关联度较低：\n\n"
        for s in analysis.independent_sectors[:5]:
            sector = next((x for x in analysis.sector_analysis if x.name == s), None)
            if sector:
                report += f"- {s}（{sector.change_percent:+.2f}%）- {sector.interpretation}\n"
        report += "\n"

    # 领先大盘板块
    if analysis.leading_sectors:
        report += f"### ★ 领先大盘板块\n\n"
        report += "这些板块先于大盘启动，可能具有前瞻性：\n\n"
        for s in analysis.leading_sectors[:3]:
            report += f"- {s}\n"
        report += "\n"

    # 资金流向
    report += "## 三、资金流向总结\n\n"

    if analysis.capital_flow_summary.get("top_inflow"):
        report += "**主力净流入TOP5**：\n\n"
        for i, flow in enumerate(analysis.capital_flow_summary["top_inflow"], 1):
            report += f"{i}. {flow['name']} +{flow['net_inflow']:.1f}亿\n"
        report += "\n"

    if analysis.capital_flow_summary.get("top_outflow"):
        report += "**主力净流出TOP5**：\n\n"
        for i, flow in enumerate(analysis.capital_flow_summary["top_outflow"], 1):
            report += f"{i}. {flow['name']} {flow['net_inflow']:.1f}亿\n"
        report += "\n"

    total_net = analysis.capital_flow_summary.get("total_net", 0)
    net_direction = "净流入" if total_net > 0 else "净流出"
    report += f"**市场整体**：{net_direction}{abs(total_net):.1f}亿\n\n"

    # 涨跌停统计
    if analysis.limit_up_analysis:
        report += "## 四、涨跌停统计\n\n"
        report += f"- 涨停总数：{analysis.limit_up_analysis.get('total', 0)}只\n"
        report += f"- 跌停总数：{analysis.limit_up_analysis.get('down', 0)}只\n"
        report += f"- ST涨停：{analysis.limit_up_analysis.get('st_up', 0)}只\n\n"

        sector_detail = analysis.limit_up_analysis.get("sector_detail", {})
        if sector_detail:
            report += "**板块涨停分布**：\n\n"
            sorted_sectors = sorted(sector_detail.items(), key=lambda x: x[1], reverse=True)
            for name, count in sorted_sectors[:6]:
                report += f"- {name}：{count}只涨停\n"
            report += "\n"

    # 预警和建议
    if analysis.warnings:
        report += "## 五、风险预警\n\n"
        for warning in analysis.warnings:
            report += f"- {warning}\n"
        report += "\n"

    if analysis.recommendations:
        report += "## 六、操作建议\n\n"
        for rec in analysis.recommendations:
            report += f"- {rec}\n"
        report += "\n"

    # 总结
    report += """---

## 七、情绪小结

"""

    # 根据分析结果生成情绪小结
    strong_count = len([s for s in analysis.sector_analysis if s.sentiment in ["强势", "偏强"]])
    weak_count = len([s for s in analysis.sector_analysis if s.sentiment in ["弱势", "偏弱"]])

    if strong_count > weak_count:
        report += f"今日市场情绪偏暖，{strong_count}个板块表现强势，资金积极布局。{analysis.sentiment}背景下，可适度参与强势板块。\n"
    elif weak_count > strong_count:
        report += f"今日市场情绪偏弱，{weak_count}个板块表现疲软，主力资金有所撤退。{analysis.sentiment}背景下，建议控制仓位，谨慎操作。\n"
    else:
        report += f"今日市场情绪分化，强势与弱势板块数量相当（{strong_count} vs {weak_count}）。{analysis.sentiment}背景下，建议精选个股，避免追涨杀跌。\n"

    report += """
---

*本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
"""

    return report


async def main():
    """测试分析脚本"""
    # 导入爬取脚本
    import sys
    sys.path.append('scripts')
    from scrape_data import AStockDataScraper

    scraper = AStockDataScraper()
    data = await scraper.scrape_market_data()

    analyzer = EmotionAnalyzer(data)
    analysis = analyzer.analyze()

    report = generate_report(analysis, "午盘")
    print(report)

    # 保存报告
    with open("data/cache/emotion_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    return analysis, report


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
