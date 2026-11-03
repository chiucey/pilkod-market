#!/usr/bin/env python3
"""
Stock Market Pro 主入口模块 - 多数据源版本
支持数据源: yfinance, dfcf(东方财富), futu(富途), sina(新浪), tushare, wind, akshare
"""

import sys
import json
import os
import subprocess
import re
from typing import Dict, Any, Optional


class StockMarketPro:
    """多源股票分析主类"""

    def __init__(self):
        self.scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")

    def _is_cn_stock(self, ticker: str) -> bool:
        """判断是否为A股或港股"""
        if re.match(r'^[0-9]{6}$', ticker):
            return True
        if re.match(r'^[0-9]{4,5}$', ticker):
            return True
        if ticker.endswith('.HK') or ticker.endswith('.SS') or ticker.endswith('.SZ'):
            return True
        return False

    def _run_command(self, cmd: list) -> Dict[str, Any]:
        """执行命令并返回结果"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _call_multi_source(self, action: str, ticker: str, source: str, **kwargs) -> Dict[str, Any]:
        """调用 multi_source.py 统一接口"""
        cmd = ["python", os.path.join(self.scripts_dir, "multi_source.py"), action, ticker, f"--source={source}"]
        if "period" in kwargs:
            cmd.extend(["--period", kwargs["period"]])
        if "chart_type" in kwargs:
            cmd.extend(["--chart_type", kwargs["chart_type"]])
        if "indicators" in kwargs and kwargs["indicators"]:
            for ind in kwargs["indicators"]:
                cmd.append(f"--{ind}")
        return self._run_command(cmd)

    def get_price(self, ticker: str, source: str = "auto") -> Dict[str, Any]:
        """获取实时报价"""
        return self._call_multi_source("price", ticker, source)

    def get_fundamentals(self, ticker: str, source: str = "auto") -> Dict[str, Any]:
        """获取基本面数据"""
        return self._call_multi_source("fundamentals", ticker, source)

    def get_history(self, ticker: str, period: str = "6mo", source: str = "auto") -> Dict[str, Any]:
        """获取历史数据"""
        return self._call_multi_source("history", ticker, source, period=period)

    def get_pro_chart(self, ticker: str, period: str = "6mo", chart_type: str = "candlestick",
                     indicators: Optional[list] = None, source: str = "auto") -> Dict[str, Any]:
        """生成专业图表"""
        return self._call_multi_source("pro", ticker, source, period=period, chart_type=chart_type, indicators=indicators)

    def get_report(self, ticker: str, period: str = "6mo", source: str = "auto") -> Dict[str, Any]:
        """生成综合报告"""
        return self._call_multi_source("report", ticker, source, period=period)

    def get_news(self, query: str, max_results: int = 8) -> Dict[str, Any]:
        """搜索新闻"""
        cmd = ["python", os.path.join(self.scripts_dir, "news.py"), query, "--max", str(max_results)]
        return self._run_command(cmd)

    def get_options_links(self, ticker: str) -> Dict[str, Any]:
        """获取期权链接"""
        cmd = ["python", os.path.join(self.scripts_dir, "options_links.py"), ticker]
        return self._run_command(cmd)


def run(input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    主运行函数，供 Agent 调用

    Args:
        input_data: 包含以下键的字典:
            - action: 操作类型 (price/fundamentals/history/pro/report/news/options)
            - ticker: 股票代码
            - data_source: 数据源 (auto/dfcf/futu/sina/tushare/wind/akshare/yfinance)
            - period: 历史周期 (1mo/3mo/6mo/1y)
            - chart_type: 图表类型
            - indicators: 技术指标列表
            - max_results: 新闻最大条数

    Returns:
        包含 status, data, message_for_user 的字典
    """
    try:
        if not input_data:
            input_data = {}

        action = input_data.get("action", "price")
        ticker = input_data.get("ticker", "AAPL")
        source = input_data.get("data_source", "auto")
        smp = StockMarketPro()

        if action == "price":
            result = smp.get_price(ticker, source)
        elif action == "fundamentals":
            result = smp.get_fundamentals(ticker, source)
        elif action == "history":
            period = input_data.get("period", "6mo")
            result = smp.get_history(ticker, period, source)
        elif action == "pro":
            period = input_data.get("period", "6mo")
            chart_type = input_data.get("chart_type", "candlestick")
            indicators = input_data.get("indicators", [])
            result = smp.get_pro_chart(ticker, period, chart_type, indicators, source)
        elif action == "report":
            period = input_data.get("period", "6mo")
            result = smp.get_report(ticker, period, source)
        elif action == "news":
            query = input_data.get("query", ticker)
            max_results = input_data.get("max_results", 8)
            result = smp.get_news(query, max_results)
        elif action == "options":
            result = smp.get_options_links(ticker)
        else:
            return {"status": "error", "data": None, "message_for_user": f"未知操作: {action}"}

        return {
            "status": result["status"],
            "data": result,
            "message_for_user": "操作成功" if result["status"] == "success" else "操作失败"
        }
    except Exception as e:
        return {"status": "error", "data": None, "message_for_user": f"执行失败: {str(e)}"}


if __name__ == "__main__":
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False))
