"""
数据管理中心脚本
用于数据获取、检核、更新和虚拟数据处理
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataStatus(Enum):
    """数据状态枚举"""
    FRESH = "fresh"           # 数据新鲜
    STALE = "stale"           # 数据较旧
    UPDATING = "updating"     # 更新中
    ERROR = "error"           # 获取失败
    VIRTUAL = "virtual"       # 虚拟数据


@dataclass
class DataPoint:
    """数据点"""
    symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str = "unknown"
    is_virtual: bool = False
    virtual_reason: Optional[str] = None
    confidence: float = 1.0
    status: DataStatus = DataStatus.FRESH


@dataclass
class ValidationResult:
    """数据验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    corrected: bool = False
    corrected_values: Dict = field(default_factory=dict)


class DataSourceManager:
    """数据源管理器"""

    DATA_SOURCES = {
        "realtime": [
            {"name": "eastmoney", "priority": 1, "reliability": 0.95},
            {"name": "sina", "priority": 2, "reliability": 0.90},
            {"name": "tencent", "priority": 3, "reliability": 0.85}
        ],
        "historical": [
            {"name": "akshare", "priority": 1, "reliability": 0.90},
            {"name": "tushare", "priority": 2, "reliability": 0.95}
        ],
        "fundamentals": [
            {"name": "eastmoney", "priority": 1, "reliability": 0.90},
            {"name": "cninfo", "priority": 2, "reliability": 0.95}
        ]
    }

    def __init__(self):
        self.active_sources = {}
        self.fallback_sources = {}
        self.source_stats = {}

    def get_best_source(self, data_type: str) -> Optional[str]:
        """获取最佳数据源"""
        sources = self.DATA_SOURCES.get(data_type, [])
        if not sources:
            return None
        sorted_sources = sorted(sources, key=lambda x: x["priority"])
        return sorted_sources[0]["name"]

    def switch_source(self, data_type: str, reason: str) -> Optional[str]:
        """切换到备用数据源"""
        sources = self.DATA_SOURCES.get(data_type, [])
        for source in sources:
            if source["name"] != self.get_best_source(data_type):
                logger.info(f"Switching from {self.get_best_source(data_type)} to {source['name']}: {reason}")
                return source["name"]
        return None

    def record_fetch_result(self, source: str, success: bool, error: Optional[str] = None):
        """记录数据获取结果"""
        if source not in self.source_stats:
            self.source_stats[source] = {"success": 0, "failure": 0, "last_error": None}

        if success:
            self.source_stats[source]["success"] += 1
        else:
            self.source_stats[source]["failure"] += 1
            self.source_stats[source]["last_error"] = error


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_ohlcv(data: DataPoint) -> ValidationResult:
        """验证OHLCV数据"""
        errors = []
        warnings = []
        corrected = False
        corrected_values = {}

        # 检查价格范围
        if data.close < 0:
            errors.append(f"收盘价异常: {data.close}")
        if data.high < data.close or data.high < data.open:
            warnings.append(f"最高价异常: high={data.high}, close={data.close}, open={data.open}")
            # 自动修正
            data.high = max(data.close, data.open, data.high)
            corrected = True
            corrected_values["high"] = data.high

        if data.low > data.close or data.low > data.open:
            warnings.append(f"最低价异常: low={data.low}, close={data.close}, open={data.open}")
            # 自动修正
            data.low = min(data.close, data.open, data.low)
            corrected = True
            corrected_values["low"] = data.low

        # 检查涨跌幅
        if abs(data.close - data.open) / data.open > 0.2:
            warnings.append(f"单日涨跌幅过大: {(data.close - data.open) / data.open * 100:.2f}%")

        # 检查成交量
        if data.volume < 0:
            errors.append(f"成交量异常: {data.volume}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrected=corrected,
            corrected_values=corrected_values
        )

    @staticmethod
    def check_consistency(current: DataPoint, previous: Optional[DataPoint]) -> ValidationResult:
        """检查数据一致性"""
        warnings = []

        if previous is None:
            return ValidationResult(is_valid=True)

        # 检查价格跳变
        price_change = abs(current.close - previous.close) / previous.close
        if price_change > 0.20:  # 单日超过20%变化
            warnings.append(f"与前日数据跳变较大: {price_change * 100:.2f}%")

        # 检查成交量异常
        if previous.volume > 0:
            volume_change = abs(current.volume - previous.volume) / previous.volume
            if volume_change > 5.0:  # 成交量变化超过500%
                warnings.append(f"成交量异常变化: {volume_change * 100:.2f}%")

        return ValidationResult(
            is_valid=True,
            warnings=warnings
        )

    @staticmethod
    def check_data_gap(data_list: List[DataPoint], expected_days: List[str]) -> List[str]:
        """检查数据缺口"""
        existing_dates = set(d.date for d in data_list)
        missing_dates = [d for d in expected_days if d not in existing_dates]
        return missing_dates


class DataManager:
    """数据管理器主类"""

    def __init__(self):
        self.source_manager = DataSourceManager()
        self.validator = DataValidator()
        self.realtime_data = {}
        self.historical_data = {}
        self.last_update = {}

    def fetch_realtime_data(self, symbols: List[str]) -> Dict[str, DataPoint]:
        """获取实时数据"""
        results = {}

        for symbol in symbols:
            best_source = self.source_manager.get_best_source("realtime")

            # 模拟数据获取
            try:
                # TODO: 实现实际API调用
                # data = self._fetch_from_source(symbol, best_source)
                data = self._mock_fetch(symbol)

                if data:
                    validation = self.validator.validate_ohlcv(data)
                    if validation.warnings:
                        logger.warning(f"{symbol}: {', '.join(validation.warnings)}")

                    results[symbol] = data
                    self.source_manager.record_fetch_result(best_source, True)
                else:
                    # 尝试备用数据源
                    fallback = self.source_manager.switch_source("realtime", "Primary source returned empty")
                    if fallback:
                        # data = self._fetch_from_source(symbol, fallback)
                        results[symbol] = self._mock_fetch(symbol)
                        self.source_manager.record_fetch_result(fallback, True)
                    else:
                        self.source_manager.record_fetch_result(best_source, False, "No data available")

            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                self.source_manager.record_fetch_result(best_source, False, str(e))

        return results

    def fetch_historical_data(self, symbol: str, start_date: str, end_date: str) -> List[DataPoint]:
        """获取历史数据"""
        # TODO: 实现历史数据获取逻辑
        return []

    def check_and_fill_gaps(self, data: List[DataPoint], symbol: str, start_date: str, end_date: str) -> Tuple[List[DataPoint], List[DataPoint]]:
        """检查并填补数据缺口"""
        # 生成期望的交易日列表
        expected_dates = self._generate_trading_days(start_date, end_date)

        # 找出缺失的日期
        missing_dates = self.validator.check_data_gap(data, expected_dates)

        # 为缺失的日期创建虚拟数据
        virtual_data = []
        for missing_date in missing_dates:
            virtual = self._create_virtual_data_point(symbol, missing_date, data)
            virtual_data.append(virtual)

        # 合并真实数据和虚拟数据
        all_data = data + virtual_data
        all_data.sort(key=lambda x: x.date)

        return all_data, virtual_data

    def _create_virtual_data_point(self, symbol: str, date: str, reference_data: List[DataPoint]) -> DataPoint:
        """创建虚拟数据点"""
        if not reference_data:
            # 无参考数据，创建基础虚拟数据
            return DataPoint(
                symbol=symbol,
                date=date,
                open=0,
                high=0,
                low=0,
                close=0,
                volume=0,
                source="generated",
                is_virtual=True,
                virtual_reason="no_reference_data",
                confidence=0.0,
                status=DataStatus.VIRTUAL
            )

        # 使用最近真实数据作为参考
        latest = reference_data[-1]

        return DataPoint(
            symbol=symbol,
            date=date,
            open=latest.close,
            high=latest.close,
            low=latest.close,
            close=latest.close,
            volume=0,
            source="interpolated",
            is_virtual=True,
            virtual_reason=f"missing_date_{date}",
            confidence=0.5,  # 较低的置信度
            status=DataStatus.VIRTUAL
        )

    def _generate_trading_days(self, start_date: str, end_date: str) -> List[str]:
        """生成交易日列表"""
        # 简化实现，实际应考虑节假日
        dates = []
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")

        current = start
        while current <= end:
            # 跳过周末
            if current.weekday() < 5:
                dates.append(current.strftime("%Y%m%d"))
            current += timedelta(days=1)

        return dates

    def _mock_fetch(self, symbol: str) -> DataPoint:
        """模拟数据获取"""
        import random
        return DataPoint(
            symbol=symbol,
            date=datetime.now().strftime("%Y%m%d"),
            open=round(random.uniform(10, 100), 2),
            high=round(random.uniform(10, 100), 2),
            low=round(random.uniform(10, 100), 2),
            close=round(random.uniform(10, 100), 2),
            volume=round(random.uniform(1000000, 10000000), 0),
            source="mock"
        )

    def get_data_status(self) -> Dict:
        """获取数据状态报告"""
        return {
            "realtime": {
                "symbols": list(self.realtime_data.keys()),
                "last_update": self.last_update.get("realtime"),
                "status": DataStatus.FRESH.value
            },
            "historical": {
                "symbols": list(self.historical_data.keys()),
                "last_update": self.last_update.get("historical"),
                "status": DataStatus.FRESH.value
            },
            "sources": self.source_manager.source_stats
        }


class DataUpdateScheduler:
    """数据更新调度器"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.update_tasks = {}

    def schedule_update(self, task_name: str, data_type: str, interval: int):
        """调度数据更新任务"""
        self.update_tasks[task_name] = {
            "data_type": data_type,
            "interval": interval,
            "last_run": None,
            "next_run": None
        }

    def run_updates(self):
        """执行所有待更新的任务"""
        for task_name, task_info in self.update_tasks.items():
            should_run = self._check_should_run(task_info)
            if should_run:
                self._execute_update(task_name, task_info)

    def _check_should_run(self, task_info: Dict) -> bool:
        """检查是否应该执行更新"""
        if task_info["last_run"] is None:
            return True

        # TODO: 实现时间间隔检查
        return True

    def _execute_update(self, task_name: str, task_info: Dict):
        """执行更新任务"""
        logger.info(f"Running update task: {task_name}")
        task_info["last_run"] = datetime.now().isoformat()


# 主函数
def main():
    """主函数"""
    print("=" * 50)
    print("A股分析系统 - 数据管理中心")
    print("=" * 50)

    # 初始化数据管理器
    dm = DataManager()

    # 获取实时数据
    symbols = ["000001", "399001", "399006"]
    print(f"\n获取实时数据: {symbols}")

    data = dm.fetch_realtime_data(symbols)

    for symbol, dp in data.items():
        print(f"\n{symbol}:")
        print(f"  日期: {dp.date}")
        print(f"  开: {dp.open}, 高: {dp.high}, 低: {dp.low}, 收: {dp.close}")
        print(f"  成交量: {dp.volume}")
        print(f"  来源: {dp.source}")
        print(f"  虚拟: {dp.is_virtual}")

    # 获取数据状态
    status = dm.get_data_status()
    print(f"\n数据状态: {json.dumps(status, indent=2, default=str)}")

    print("\n" + "=" * 50)
    print("数据管理中心初始化完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
