#!/usr/bin/env python3
"""
龙头股票识别脚本
用于识别强势板块中的龙头股票，包括龙头股、容量中军和情绪标的
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class SectorInfo:
    """板块信息"""
    name: str           # 板块名称
    change_pct: float   # 板块涨幅(%)
    turnover: float     # 板块成交额(亿)
    limit_up_count: int # 涨停家数
    market_cap: float    # 板块总市值(亿)


@dataclass
class MarketContext:
    """大盘上下文信息"""
    index_change: float      # 大盘指数涨跌幅(%)
    index_turnover: float   # 大盘成交额(亿)
    timestamp: str           # 时间戳


@dataclass
class StockInfo:
    """股票基本信息"""
    code: str           # 股票代码
    name: str           # 股票名称
    sector: str         # 所属板块
    price: float        # 当前价格
    change_pct: float   # 涨跌幅(%)
    turnover: float     # 成交额(亿)
    market_cap: float   # 总市值(亿)
    limit_up_count: int # 连续涨停天数
    limit_up_time: str  # 涨停时间(HH:MM)
    is_limit_up: bool   # 是否涨停
    wave_count: int     # 炸板次数
    seal_order: float   # 封单量(手)
    consecutive_limit_days: int = 0  # 连续一字板天数
    # 新增：与大盘联动指标
    correlation_with_market: float = 1.0  # 与大盘相关性 (0-1)
    leads_market: bool = False           # 是否领先大盘


@dataclass
class LeadStockAnalysis:
    """龙头分析结果"""
    lead_stock: Optional[StockInfo] = None          # 龙头股
    capacity_leaders: List[StockInfo] = None       # 容量中军列表
    sentiment_barometers: List[StockInfo] = None   # 情绪标的列表
    validation_warning: Optional[str] = None        # 大盘联动验证警告
    sector_strength: float = 0.0                    # 板块强度 (涨幅/大盘涨幅)

    def __post_init__(self):
        if self.capacity_leaders is None:
            self.capacity_leaders = []
        if self.sentiment_barometers is None:
            self.sentiment_barometers = []

    def to_dict(self) -> Dict:
        result = {"analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        if self.lead_stock:
            result["lead_stock"] = {
                "name": self.lead_stock.name,
                "code": self.lead_stock.code,
                "consecutive_limit_days": self.lead_stock.limit_up_count,
                "limit_up_time": self.lead_stock.limit_up_time,
                "seal_order": self.lead_stock.seal_order,
                "turnover": self.lead_stock.turnover,
                "description": "情绪定海神针，决定板块炒作高度"
            }

        result["capacity_leaders"] = [
            {
                "name": s.name,
                "code": s.code,
                "turnover": s.turnover,
                "market_cap": s.market_cap,
                "change_pct": s.change_pct,
                "description": "成交量/市值最大，提供流动性支撑"
            }
            for s in self.capacity_leaders
        ]

        result["sentiment_barometers"] = [
            {
                "name": s.name,
                "code": s.code,
                "limit_up_time": s.limit_up_time,
                "consecutive_limit_days": s.consecutive_limit_days,
                "description": "最快封板，连续一字板"
            }
            for s in self.sentiment_barometers
        ]

        return result


class LeadStockIdentifier:
    """龙头股票识别器"""

    # 权重配置
    WEIGHTS = {
        "consecutive_limit": 0.30,   # 连板高度权重
        "seal_stability": 0.25,      # 封单稳定性权重
        "sentiment_lead": 0.25,      # 情绪带动性权重
        "trend_stability": 0.20      # 分时稳健度权重
    }

    # 阈值配置
    THRESHOLDS = {
        "min_turnover": 10,          # 容量中军最小成交额(亿)
        "min_market_cap": 100,       # 容量中军最小市值(亿)
        "min_change_pct": 5,         # 容量中军最小涨幅(%)
        "sector_min_limit_up": 3,    # 板块最小涨停数
        "sector_min_change": 3,      # 板块最小涨幅(%)
        "early_limit_time": "09:45", # 情绪标的封板时间上限
        # 大盘联动阈值
        "sector_strength_min": 1.5,  # 板块强度最小值 (板块涨幅/大盘涨幅)
        "min_market_turnover_pct": 0.05,  # 板块成交额占大盘最小比例
    }

    def __init__(self):
        self.stocks: List[StockInfo] = []
        self.sector_name: str = ""
        self.sector_info: Optional[SectorInfo] = None
        self.market_context: Optional[MarketContext] = None
        self.sector_validation_passed: bool = False

    def load_data(self, stocks_data: List[Dict], sector_name: str,
                  sector_info: Optional[Dict] = None,
                  market_context: Optional[Dict] = None):
        """加载股票数据（含大盘联动信息）

        Args:
            stocks_data: 股票数据列表
            sector_name: 板块名称
            sector_info: 板块信息 dict，包含 name, change_pct, turnover, limit_up_count, market_cap
            market_context: 大盘信息 dict，包含 index_change, index_turnover, timestamp
        """
        self.sector_name = sector_name
        self.stocks = []

        # 加载板块信息
        if sector_info:
            self.sector_info = SectorInfo(
                name=sector_info.get("name", sector_name),
                change_pct=sector_info.get("change_pct", 0.0),
                turnover=sector_info.get("turnover", 0.0),
                limit_up_count=sector_info.get("limit_up_count", 0),
                market_cap=sector_info.get("market_cap", 0.0)
            )
        else:
            # 从股票数据聚合板块信息
            self.sector_info = self._aggregate_sector_info(stocks_data)

        # 加载大盘信息
        if market_context:
            self.market_context = MarketContext(
                index_change=market_context.get("index_change", 0.0),
                index_turnover=market_context.get("index_turnover", 0.0),
                timestamp=market_context.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

        # 验证板块与大盘联动
        self.sector_validation_passed = self._validate_sector_market_link()

        # 加载股票数据
        for data in stocks_data:
            stock = StockInfo(
                code=data.get("code", ""),
                name=data.get("name", ""),
                sector=data.get("sector", sector_name),
                price=data.get("price", 0.0),
                change_pct=data.get("change_pct", 0.0),
                turnover=data.get("turnover", 0.0),
                market_cap=data.get("market_cap", 0.0),
                limit_up_count=data.get("limit_up_count", 0),
                limit_up_time=data.get("limit_up_time", ""),
                is_limit_up=data.get("is_limit_up", False),
                wave_count=data.get("wave_count", 0),
                seal_order=data.get("seal_order", 0.0),
                consecutive_limit_days=data.get("consecutive_limit_days", 0),
                correlation_with_market=data.get("correlation_with_market", 1.0),
                leads_market=data.get("leads_market", False)
            )
            self.stocks.append(stock)

    def _aggregate_sector_info(self, stocks_data: List[Dict]) -> SectorInfo:
        """从股票数据聚合板块信息"""
        if not stocks_data:
            return SectorInfo(name=self.sector_name, change_pct=0.0, turnover=0.0,
                            limit_up_count=0, market_cap=0.0)

        total_turnover = sum(s.get("turnover", 0) for s in stocks_data)
        max_change = max((s.get("change_pct", 0) for s in stocks_data), default=0)
        limit_up_count = sum(1 for s in stocks_data if s.get("is_limit_up", False))

        return SectorInfo(
            name=self.sector_name,
            change_pct=max_change,
            turnover=total_turnover,
            limit_up_count=limit_up_count,
            market_cap=sum(s.get("market_cap", 0) for s in stocks_data)
        )

    def _validate_sector_market_link(self) -> bool:
        """验证板块与大盘联动（核心前提条件）

        必须满足以下条件才算有效的龙头板块：
        1. 板块涨幅 > 大盘涨幅
        2. 板块强度 >= 1.5 (板块涨幅/大盘涨幅)
        3. 板块涨停数 >= 3
        """
        if not self.sector_info:
            return False

        if not self.market_context:
            # 没有大盘数据时，假设大盘涨幅为0，仅检查板块自身条件
            return self.sector_info.change_pct > 2 and self.sector_info.limit_up_count >= 3

        sector_change = self.sector_info.change_pct
        market_change = self.market_context.index_change

        # 条件1：板块涨幅 > 大盘涨幅
        if sector_change <= market_change:
            return False

        # 条件2：板块强度 >= 阈值
        sector_strength = sector_change / max(abs(market_change), 0.01)
        if sector_strength < self.THRESHOLDS["sector_strength_min"]:
            return False

        # 条件3：板块涨停数 >= 3
        if self.sector_info.limit_up_count < self.THRESHOLDS["sector_min_limit_up"]:
            return False

        return True

    def analyze(self) -> LeadStockAnalysis:
        """执行龙头股票分析"""
        if not self.stocks:
            return LeadStockAnalysis()

        analysis = LeadStockAnalysis()

        # 计算板块强度
        if self.sector_info and self.market_context:
            market_change = abs(self.market_context.index_change)
            if market_change > 0.01:
                analysis.sector_strength = self.sector_info.change_pct / market_change
            elif self.sector_info.change_pct > 0:
                analysis.sector_strength = 999  # 大盘持平，板块上涨

        # 如果板块验证未通过（不是带动大盘的强势板块），返回警告
        if not self.sector_validation_passed:
            analysis.validation_warning = "板块未通过大盘联动验证，不符合龙头股票识别条件"
            return analysis

        # 筛选涨停股票
        limit_up_stocks = [s for s in self.stocks if s.is_limit_up]

        if not limit_up_stocks:
            return analysis

        # 1. 识别龙头股
        analysis.lead_stock = self._identify_lead_stock(limit_up_stocks)

        # 2. 识别容量中军
        analysis.capacity_leaders = self._identify_capacity_leaders()

        # 3. 识别情绪标的
        analysis.sentiment_barometers = self._identify_sentiment_barometers()

        return analysis

    def _identify_lead_stock(self, limit_up_stocks: List[StockInfo]) -> Optional[StockInfo]:
        """识别龙头股"""
        if not limit_up_stocks:
            return None

        scored_stocks = []

        for stock in limit_up_stocks:
            # 计算各项得分
            consecutive_score = min(stock.limit_up_count * 10, 100)  # 连板得分

            # 封单稳定性得分 (炸板越少分数越高)
            seal_stability = max(100 - stock.wave_count * 20, 0)

            # 情绪带动性 (用封单量衡量，封单大说明带动性强)
            sentiment_score = min(stock.seal_order / 10000, 100) if stock.seal_order else 0

            # 稳健度得分 (用一字板天数衡量)
            stability_score = min(stock.consecutive_limit_days * 30, 100)

            # 总得分
            total_score = (
                consecutive_score * self.WEIGHTS["consecutive_limit"] +
                seal_stability * self.WEIGHTS["seal_stability"] +
                sentiment_score * self.WEIGHTS["sentiment_lead"] +
                stability_score * self.WEIGHTS["trend_stability"]
            )

            scored_stocks.append((stock, total_score))

        # 返回得分最高的股票
        scored_stocks.sort(key=lambda x: x[1], reverse=True)
        return scored_stocks[0][0] if scored_stocks else None

    def _identify_capacity_leaders(self) -> List[StockInfo]:
        """识别容量中军"""
        candidates = []

        for stock in self.stocks:
            # 基础筛选条件
            if stock.turnover < self.THRESHOLDS["min_turnover"]:
                continue
            if stock.market_cap < self.THRESHOLDS["min_market_cap"]:
                continue
            if stock.change_pct < self.THRESHOLDS["min_change_pct"]:
                continue

            candidates.append(stock)

        # 按成交额排序，取前3
        candidates.sort(key=lambda x: x.turnover, reverse=True)
        return candidates[:3]

    def _identify_sentiment_barometers(self) -> List[StockInfo]:
        """识别情绪标的"""
        limit_up_stocks = [s for s in self.stocks if s.is_limit_up]

        if not limit_up_stocks:
            return []

        candidates = []
        early_limit_time = self.THRESHOLDS["early_limit_time"]

        for stock in limit_up_stocks:
            # 筛选条件：封板时间早 + 连续一字板>=2天
            if stock.limit_up_time > early_limit_time:
                continue
            if stock.consecutive_limit_days < 2:
                continue

            candidates.append(stock)

        # 按封板时间排序，然后按一字板天数排序
        candidates.sort(key=lambda x: (x.limit_up_time, -x.consecutive_limit_days))
        return candidates[:3]

    def generate_report(self, analysis: LeadStockAnalysis) -> str:
        """生成分析报告"""
        report = f"""# 【{self.sector_name}】龙头股票分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 一、大盘联动验证（核心前提）

"""

        # 大盘联动验证结果
        if not self.sector_validation_passed:
            report += """### ⚠️ 验证未通过

**该板块未通过大盘联动验证，不符合龙头股票识别条件。**

原因可能包括：
- 板块涨幅未明显领先大盘
- 板块涨停家数不足
- 板块与大盘走势背离

**有效龙头板块必须满足**：
1. 板块涨幅 > 大盘涨幅
2. 板块强度（涨幅/大盘涨幅）>= 1.5
3. 板块涨停家数 >= 3

---

"""
        else:
            sector_strength = analysis.sector_strength
            report += f"""### ✅ 验证通过

| 验证项 | 数值 | 状态 |
|--------|------|------|
| 板块涨幅 | {self.sector_info.change_pct if self.sector_info else 0:.2f}% | ✓ |
| 大盘涨幅 | {self.market_context.index_change if self.market_context else 0:.2f}% | - |
| 板块强度 | {sector_strength:.2f} | ✓ (>=1.5) |
| 板块涨停数 | {self.sector_info.limit_up_count if self.sector_info else 0}只 | ✓ (>=3) |

**说明**: 该板块是带动大盘同步上涨的强势板块，符合龙头股票识别条件。

---

"""

        report += f"""## 二、板块概况

- 板块内股票总数: {len(self.stocks)}只
- 涨停股票数: {sum(1 for s in self.stocks if s.is_limit_up)}只
- 最大成交额: {max(s.turnover for s in self.stocks):.2f}亿
- 最大市值: {max(s.market_cap for s in self.stocks):.2f}亿

---

## 三、龙头股分析 (Lead Stock)

"""

        if analysis.lead_stock:
            ls = analysis.lead_stock
            report += f"""### 龙头股: {ls.name}({ls.code})

| 指标 | 数值 |
|------|------|
| 连板高度 | {ls.limit_up_count}连板 |
| 涨停时间 | {ls.limit_up_time} |
| 封单量 | {ls.seal_order:.0f}手 |
| 成交额 | {ls.turnover:.2f}亿 |
| 炸板次数 | {ls.wave_count}次 |
| 一字板天数 | {ls.consecutive_limit_days}天 |

**特征**: 情绪定海神针，决定板块炒作高度和情绪方向。分时走势稳健，不轻易炸板。

"""
        else:
            report += "> 暂无明显龙头股，需观察次日走势\n\n"

        report += """## 三、容量中军分析 (Market Cap Leader)

> 容量中军是成交量或市值最大的股票，不一定马上封板，但会稳步往上走，成交量放大。

"""

        if analysis.capacity_leaders:
            for i, cl in enumerate(analysis.capacity_leaders, 1):
                report += f"""### {i}. {cl.name}({cl.code})

| 指标 | 数值 |
|------|------|
| 成交额 | {cl.turnover:.2f}亿 |
| 市值 | {cl.market_cap:.2f}亿 |
| 涨幅 | {cl.change_pct:.2f}% |
| 涨停时间 | {cl.limit_up_time} |

"""
        else:
            report += "> 暂无符合条件容量中军\n\n"

        report += """## 四、情绪标的分析 (Sentiment Barometer)

> 情绪标的是最快封板且后续至少有两天及以上一字板的股票。

"""

        if analysis.sentiment_barometers:
            for i, sb in enumerate(analysis.sentiment_barometers, 1):
                report += f"""### {i}. {sb.name}({sb.code})

| 指标 | 数值 |
|------|------|
| 封板时间 | {sb.limit_up_time} |
| 一字板天数 | {sb.consecutive_limit_days}天 |
| 封单量 | {sb.seal_order:.0f}手 |
| 成交额 | {sb.turnover:.2f}亿 |

"""
        else:
            report += "> 暂无符合条件情绪标的\n\n"

        report += """## 五、三类股票关系

```
        龙头股 ←→ 情绪标的
           ↓           ↓
        (相互强化，带动板块情绪)
           ↓
        容量中军
    (提供流动性支撑，确保板块活力)
```

---

## 六、实战建议

### 选股优先级建议

| 投资者类型 | 优先级顺序 | 说明 |
|------------|------------|------|
| 激进型 | 情绪标的 > 龙头股 > 容量中军 | 追求最大化收益 |
| 稳健型 | 容量中军 > 龙头股 > 情绪标的 | 追求稳定收益 |
| 均衡型 | 龙头股 > 情绪标的 > 容量中军 | 平衡风险收益 |

### 操作建议

- **龙头股**: 回调至5日线附近介入，分时低点买入
- **容量中军**: 上涨途中、成交放大时介入
- **情绪标的**: 炸板回封时、集合竞价确认一字后介入

### 风险提示

1. ⚠️ 情绪标的一字板开板后可能直接跌停
2. ⚠️ 龙头股高位炸板可能引发板块退潮
3. ⚠️ 容量中军调整往往滞后于龙头股

---
*本报告由龙头股票识别技能自动生成*
"""

        return report


def quick_identify(stocks_data: List[Dict], sector_name: str) -> Dict:
    """快速识别龙头股票（单函数接口）"""
    identifier = LeadStockIdentifier()
    identifier.load_data(stocks_data, sector_name)
    analysis = identifier.analyze()
    return identifier.generate_report(analysis), analysis.to_dict()


if __name__ == "__main__":
    # 测试用例
    test_data = [
        {"code": "001", "name": "测试龙头", "change_pct": 10.0, "turnover": 25.0,
         "market_cap": 200, "limit_up_count": 5, "limit_up_time": "09:35",
         "is_limit_up": True, "wave_count": 0, "seal_order": 50000, "consecutive_limit_days": 4},
        {"code": "002", "name": "测试中军", "change_pct": 7.5, "turnover": 50.0,
         "market_cap": 500, "limit_up_count": 1, "limit_up_time": "10:15",
         "is_limit_up": True, "wave_count": 1, "seal_order": 20000, "consecutive_limit_days": 0},
        {"code": "003", "name": "测试情绪", "change_pct": 10.0, "turnover": 8.0,
         "market_cap": 50, "limit_up_count": 3, "limit_up_time": "09:32",
         "is_limit_up": True, "wave_count": 0, "seal_order": 80000, "consecutive_limit_days": 3},
        {"code": "004", "name": "普通股票", "change_pct": 3.0, "turnover": 5.0,
         "market_cap": 80, "limit_up_count": 0, "limit_up_time": "",
         "is_limit_up": False, "wave_count": 0, "seal_order": 0, "consecutive_limit_days": 0},
    ]

    report, result = quick_identify(test_data, "测试板块")
    print(report)
    print("\n=== JSON输出 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))