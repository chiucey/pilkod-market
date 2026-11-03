# -*- coding: utf-8 -*-
"""
market-data skill 桥接模块

用于与 market-data skill 集成，获取更稳定的ETF数据
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


class MarketDataBridge:
    """market-data skill 桥接器"""

    def __init__(self, skill_path: Optional[str] = None):
        """
        初始化桥接器

        Args:
            skill_path: market-data skill 的路径
        """
        self.skill_path = self._find_skill_path(skill_path)
        self.enabled = self.skill_path is not None

        if self.enabled:
            logger.info(f"market-data skill 桥接已启用: {self.skill_path}")
        else:
            logger.warning("market-data skill 未找到，将使用 akshare 获取数据")

    def _find_skill_path(self, skill_path: Optional[str]) -> Optional[str]:
        """查找 market-data skill 路径"""
        if skill_path and os.path.exists(skill_path):
            return skill_path

        # 尝试常见路径
        possible_paths = [
            Path(__file__).parent.parent.parent / "market-data",
            Path.home() / "workspace" / "skills" / "market-data",
            Path("/workspace/skills/market-data"),
        ]

        for path in possible_paths:
            if path.exists() and (path / "SKILL.md").exists():
                return str(path)

        return None

    def get_etf_data(self, code: str, days: int = 60) -> Optional[pd.DataFrame]:
        """
        通过 market-data skill 获取 ETF 数据

        Args:
            code: ETF 代码
            days: 获取天数

        Returns:
            DataFrame 或 None
        """
        if not self.enabled:
            return None

        try:
            # 动态导入 market-data skill 的数据获取模块
            sys.path.insert(0, self.skill_path)
            from scripts.data_fetcher import get_etf_historical_data

            result = get_etf_historical_data(code, days=days)
            sys.path.remove(self.skill_path)

            return result
        except Exception as e:
            logger.warning(f"通过 market-data skill 获取 ETF 数据失败: {e}")
            return None

    def is_available(self) -> bool:
        """检查桥接是否可用"""
        return self.enabled


# 全局实例
_bridge_instance: Optional[MarketDataBridge] = None


def get_bridge(skill_path: Optional[str] = None) -> MarketDataBridge:
    """获取桥接器全局实例"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = MarketDataBridge(skill_path)
    return _bridge_instance


def is_market_data_available() -> bool:
    """检查 market-data skill 是否可用"""
    bridge = get_bridge()
    return bridge.is_available()
