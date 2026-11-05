#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取脚本 - 从各市场获取股票数据

支持：
- A股（上交所、深交所）
- 港股
- 美股

依赖：
    pip install akshare yfinance pandas

用法：
    from fetch_data import StockDataFetcher
    fetcher = StockDataFetcher()
    data = fetcher.fetch_all("600519.SS")
"""

import json
import warnings
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')


class StockDataFetcher:
    """股票数据获取器"""

    def __init__(self):
        self.data_cache = {}
        self.last_fetch = {}

    def normalize_symbol(self, symbol: str, region: str = "auto") -> tuple:
        """
        规范化股票代码

        Args:
            symbol: 股票代码
            region: 市场区域 (auto/cn/hk/us)

        Returns:
            tuple: (normalized_symbol, region, exchange)
        """
        symbol = symbol.upper().strip()

        # 自动识别市场
        if region == "auto":
            if symbol.endswith(".SS") or symbol.endswith(".SZ"):
                region = "cn"
            elif symbol.endswith(".HK"):
                region = "hk"
            elif symbol.isalpha() and len(symbol) <= 5:
                region = "us"
            else:
                region = "cn"  # 默认A股

        # 规范化代码
        if region == "cn":
            if "." not in symbol:
                # 假设上海交易所
                if symbol.startswith("6"):
                    symbol = f"{symbol}.SS"
                else:
                    symbol = f"{symbol}.SZ"
            exchange = "上交所/深交所"
        elif region == "hk":
            if not symbol.endswith(".HK"):
                symbol = f"{symbol}.HK"
            exchange = "港交所"
        else:  # us
            exchange = "纽交所/纳斯达克"

        return symbol, region, exchange

    def fetch_stock_info(self, symbol: str, region: str = "auto") -> Dict:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码
            region: 市场区域

        Returns:
            Dict: 股票基本信息
        """
        symbol, region, exchange = self.normalize_symbol(symbol, region)

        try:
            if region == "cn":
                return self._fetch_cn_info(symbol)
            elif region == "hk":
                return self._fetch_hk_info(symbol)
            else:
                return self._fetch_us_info(symbol)
        except Exception as e:
            return {
                "symbol": symbol,
                "region": region,
                "error": str(e),
                "data": None
            }

    def _fetch_cn_info(self, symbol: str) -> Dict:
        """获取A股信息"""
        try:
            import akshare as ak

            # 获取个股信息
            code = symbol.split(".")[0]
            info = ak.stock_individual_info_em(symbol=code)

            info_dict = {}
            for _, row in info.iterrows():
                info_dict[row['item']] = row['value']

            return {
                "symbol": symbol,
                "region": "cn",
                "exchange": "上交所/深交所",
                "data": info_dict,
                "success": True
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "cn",
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_hk_info(self, symbol: str) -> Dict:
        """获取港股信息"""
        try:
            import akshare as ak

            code = symbol.split(".")[0]
            info = ak.stock_hk_spot_em()

            stock_info = info[info['代码'] == code]
            if len(stock_info) > 0:
                data = stock_info.iloc[0].to_dict()
                return {
                    "symbol": symbol,
                    "region": "hk",
                    "exchange": "港交所",
                    "data": data,
                    "success": True
                }

            return {
                "symbol": symbol,
                "region": "hk",
                "error": "股票未找到",
                "data": None,
                "success": False
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "hk",
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_us_info(self, symbol: str) -> Dict:
        """获取美股信息"""
        try:
            import yfinance as yf

            stock = yf.Ticker(symbol)
            info = stock.info

            return {
                "symbol": symbol,
                "region": "us",
                "exchange": "纽交所/纳斯达克",
                "data": {
                    "name": info.get("shortName", ""),
                    "industry": info.get("industry", ""),
                    "sector": info.get("sector", ""),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", None),
                    "pb_ratio": info.get("priceToBook", None),
                    "dividend_yield": info.get("dividendYield", 0),
                    "52w_high": info.get("fiftyTwoWeekHigh", None),
                    "52w_low": info.get("fiftyTwoWeekLow", None),
                    "volume": info.get("averageVolume", 0),
                    "beta": info.get("beta", None),
                    "eps": info.get("trailingEps", None),
                    "revenue": info.get("totalRevenue", None),
                    "profit_margin": info.get("profitMargins", None),
                },
                "success": True
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "us",
                "error": str(e),
                "data": None,
                "success": False
            }

    def fetch_price_history(self, symbol: str, period: str = "1y",
                           interval: str = "1d", region: str = "auto") -> Dict:
        """
        获取股票历史价格

        Args:
            symbol: 股票代码
            period: 时间周期 (1d/5d/1mo/3mo/6mo/1y/2y/5y/ytd/max)
            interval: 数据间隔 (1m/2m/5m/15m/30m/60m/1h/1d/1wk/1mo)
            region: 市场区域

        Returns:
            Dict: 历史价格数据
        """
        symbol, region, exchange = self.normalize_symbol(symbol, region)

        try:
            import yfinance as yf

            stock = yf.Ticker(symbol)
            history = stock.history(period=period, interval=interval)

            if history.empty:
                return {
                    "symbol": symbol,
                    "region": region,
                    "data": None,
                    "success": False,
                    "message": "无历史数据"
                }

            return {
                "symbol": symbol,
                "region": region,
                "exchange": exchange,
                "data": {
                    "dates": history.index.strftime('%Y-%m-%d').tolist(),
                    "open": history['Open'].tolist(),
                    "high": history['High'].tolist(),
                    "low": history['Low'].tolist(),
                    "close": history['Close'].tolist(),
                    "volume": history['Volume'].tolist(),
                },
                "success": True,
                "period": period,
                "interval": interval
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": region,
                "error": str(e),
                "data": None,
                "success": False
            }

    def fetch_financials(self, symbol: str, region: str = "auto") -> Dict:
        """
        获取财务报表数据

        Args:
            symbol: 股票代码
            region: 市场区域

        Returns:
            Dict: 财务报表数据
        """
        symbol, region, exchange = self.normalize_symbol(symbol, region)

        try:
            if region == "cn":
                return self._fetch_cn_financials(symbol)
            elif region == "hk":
                return self._fetch_hk_financials(symbol)
            else:
                return self._fetch_us_financials(symbol)
        except Exception as e:
            return {
                "symbol": symbol,
                "region": region,
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_cn_financials(self, symbol: str) -> Dict:
        """获取A股财务报表"""
        try:
            import akshare as ak

            code = symbol.split(".")[0]

            # 利润表
            income = ak.stock_profit_sheet_by_report_em(symbol=code)
            # 资产负债表
            balance = ak.stock_balance_sheet_by_report_em(symbol=code)
            # 现金流量表
            cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol=code)
            # 财务指标
            indicators = ak.stock_financial_analysis_indicator(symbol=code)

            return {
                "symbol": symbol,
                "region": "cn",
                "data": {
                    "income": income.to_dict('records') if not income.empty else [],
                    "balance": balance.to_dict('records') if not balance.empty else [],
                    "cashflow": cashflow.to_dict('records') if not cashflow.empty else [],
                    "indicators": indicators.to_dict('records') if not indicators.empty else []
                },
                "success": True
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "cn",
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_hk_financials(self, symbol: str) -> Dict:
        """获取港股财务报表"""
        try:
            import yfinance as yf

            stock = yf.Ticker(symbol)

            return {
                "symbol": symbol,
                "region": "hk",
                "data": {
                    "income": stock.financials.to_dict('records') if stock.financials is not None else [],
                    "balance": stock.balance_sheet.to_dict('records') if stock.balance_sheet is not None else [],
                    "cashflow": stock.cashflow.to_dict('records') if stock.cashflow is not None else []
                },
                "success": True
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "hk",
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_us_financials(self, symbol: str) -> Dict:
        """获取美股财务报表"""
        try:
            import yfinance as yf

            stock = yf.Ticker(symbol)

            return {
                "symbol": symbol,
                "region": "us",
                "data": {
                    "income": stock.financials.to_dict('records') if stock.financials is not None else [],
                    "balance": stock.balance_sheet.to_dict('records') if stock.balance_sheet is not None else [],
                    "cashflow": stock.cashflow.to_dict('records') if stock.cashflow is not None else [],
                    "quarterly": stock.quarterly_financials.to_dict('records') if stock.quarterly_financials is not None else []
                },
                "success": True
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "us",
                "error": str(e),
                "data": None,
                "success": False
            }

    def fetch_statistics(self, symbol: str, region: str = "auto") -> Dict:
        """
        获取估值和统计指标

        Args:
            symbol: 股票代码
            region: 市场区域

        Returns:
            Dict: 估值统计指标
        """
        symbol, region, exchange = self.normalize_symbol(symbol, region)

        try:
            if region == "cn":
                return self._fetch_cn_statistics(symbol)
            elif region == "hk":
                return self._fetch_hk_statistics(symbol)
            else:
                return self._fetch_us_statistics(symbol)
        except Exception as e:
            return {
                "symbol": symbol,
                "region": region,
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_cn_statistics(self, symbol: str) -> Dict:
        """获取A股统计指标"""
        try:
            import akshare as ak

            code = symbol.split(".")[0]
            indicator = ak.stock_financial_analysis_indicator(symbol=code)

            if not indicator.empty:
                latest = indicator.iloc[0].to_dict()
                return {
                    "symbol": symbol,
                    "region": "cn",
                    "data": latest,
                    "success": True
                }

            return {
                "symbol": symbol,
                "region": "cn",
                "error": "无数据",
                "data": None,
                "success": False
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "cn",
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_hk_statistics(self, symbol: str) -> Dict:
        """获取港股统计指标"""
        try:
            import yfinance as yf

            stock = yf.Ticker(symbol)
            info = stock.info

            return {
                "symbol": symbol,
                "region": "hk",
                "data": {
                    "pe_ratio": info.get("trailingPE", None),
                    "pb_ratio": info.get("priceToBook", None),
                    "ps_ratio": info.get("priceToSalesTrailing12Months", None),
                    "peg_ratio": info.get("pegRatio", None),
                    "dividend_yield": info.get("dividendYield", None),
                    "beta": info.get("beta", None),
                    "market_cap": info.get("marketCap", None),
                    "revenue": info.get("totalRevenue", None),
                    "net_income": info.get("netIncomeToCommon", None),
                    "eps": info.get("trailingEps", None),
                    "roe": info.get("returnOnEquity", None),
                    "debt_to_equity": info.get("debtToEquity", None),
                    "current_ratio": info.get("currentRatio", None),
                },
                "success": True
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "region": "hk",
                "error": str(e),
                "data": None,
                "success": False
            }

    def _fetch_us_statistics(self, symbol: str) -> Dict:
        """获取美股统计指标"""
        return self._fetch_hk_statistics(symbol)  # 美股和港股都用yfinance

    def fetch_all(self, symbol: str, region: str = "auto") -> Dict:
        """
        获取股票全部数据

        Args:
            symbol: 股票代码
            region: 市场区域

        Returns:
            Dict: 完整股票数据
        """
        symbol, region, exchange = self.normalize_symbol(symbol, region)

        result = {
            "symbol": symbol,
            "region": region,
            "exchange": exchange,
            "fetch_time": datetime.now().isoformat(),
            "info": self.fetch_stock_info(symbol, region),
            "price": self.fetch_price_history(symbol, region=region),
            "financials": self.fetch_financials(symbol, region),
            "statistics": self.fetch_statistics(symbol, region),
        }

        # 标记整体成功状态
        result["success"] = any([
            result["info"].get("success", False),
            result["price"].get("success", False),
            result["financials"].get("success", False),
            result["statistics"].get("success", False)
        ])

        return result

    def save_to_json(self, data: Dict, filepath: str) -> bool:
        """
        保存数据到JSON文件

        Args:
            data: 要保存的数据
            filepath: 文件路径

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False


def main():
    """测试脚本"""
    fetcher = StockDataFetcher()

    # 测试A股
    print("测试获取A股数据...")
    result = fetcher.fetch_all("600519.SS")
    print(f"结果: {result.get('success', False)}")
    print(f"股票: {result.get('info', {}).get('data', {}).get('股票简称', 'N/A')}")

    # 测试美股
    print("\n测试获取美股数据...")
    result_us = fetcher.fetch_all("AAPL")
    print(f"结果: {result_us.get('success', False)}")


if __name__ == "__main__":
    main()
