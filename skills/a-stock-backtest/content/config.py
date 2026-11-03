# -*- coding: utf-8 -*-
"""
A股量化回测系统 - 配置文件
提供系统运行所需的各项参数配置
"""

import os
from pathlib import Path

# ============================================================
# 项目路径配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# 回测参数配置
# ============================================================
BACKTEST_CONFIG = {
    # 初始资金（元）
    "initial_capital": 1000000,
    # 交易手续费率（%）
    "commission_rate": 0.0003,
    # 印花税率（%，仅卖出时收取）
    "stamp_tax_rate": 0.001,
    # 滑点（%）
    "slippage_rate": 0.0001,
    # 最小交易单位（手）
    "min_trade_unit": 100,
}

# ============================================================
# 数据源配置
# ============================================================
DATA_CONFIG = {
    # 数据源类型：akshare - 使用AKShare库获取数据
    "source": "akshare",
    # 数据缓存目录
    "cache_dir": DATA_DIR,
    # 数据获取超时时间（秒）
    "timeout": 30,
}

# ============================================================
# 策略默认参数
# ============================================================
STRATEGY_CONFIG = {
    # 移动平均线策略
    "ma": {
        "short_window": 5,
        "long_window": 20,
    },
    # RSI策略
    "rsi": {
        "period": 14,
        "oversold": 30,
        "overbought": 70,
    },
    # 布林带策略
    "bollinger": {
        "period": 20,
        "std_dev": 2,
    },
    # MACD策略
    "macd": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
    },
}

# ============================================================
# 可视化配置
# ============================================================
VISUALIZATION_CONFIG = {
    # 图表风格
    "style": "seaborn",
    # 图表尺寸
    "figsize": (14, 8),
    # 字体大小
    "font_size": 12,
    # 图表DPI
    "dpi": 100,
}

# ============================================================
# 日志配置
# ============================================================
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": RESULTS_DIR / "backtest.log",
}
