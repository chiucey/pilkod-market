#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取脚本 - 支持A股、港股、美股实时行情
使用yfinance库获取多市场股票数据
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json
import sys


class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        """初始化"""
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def get_realtime_quote(self, symbol: str) -> Dict:
        """
        获取实时报价
        
        参数:
            symbol: 股票代码
                A股: 600519.SS (茅台), 000001.SZ (平安)
                港股: 0700.HK (腾讯)
                美股: AAPL, TSLA, MSFT
        
        返回:
            包含实时报价信息的字典
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # 获取最新价格
            hist = stock.history(period="1d", interval="1m")
            if hist.empty:
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            else:
                current_price = hist['Close'].iloc[-1]
            
            result = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'current_price': round(current_price, 2),
                'change': round(info.get('regularMarketChange', 0), 2),
                'change_percent': round(info.get('regularMarketChangePercent', 0), 2),
                'open': info.get('regularMarketOpen', 0),
                'high': info.get('regularMarketDayHigh', 0),
                'low': info.get('regularMarketDayLow', 0),
                'volume': info.get('regularMarketVolume', 0),
                'previous_close': info.get('previousClose', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f"获取实时报价失败: {str(e)}",
                'symbol': symbol
            }
    
    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        获取历史数据
        
        参数:
            symbol: 股票代码
            period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: 数据间隔 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        返回:
            包含历史数据的DataFrame
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                print(f"警告: 无法获取 {symbol} 的历史数据", file=sys.stderr)
                return pd.DataFrame()
            
            return hist
            
        except Exception as e:
            print(f"获取历史数据失败: {str(e)}", file=sys.stderr)
            return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息
        
        参数:
            symbol: 股票代码
        
        返回:
            包含股票基本信息的字典
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            result = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'industry': info.get('industry', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'trailing_pe': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'enterprise_to_revenue': info.get('enterpriseToRevenue', 0),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda', 0),
                'beta': info.get('beta', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                '52_week_change': info.get('52WeekChange', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'profit_margins': info.get('profitMargins', 0),
                'operating_margins': info.get('operatingMargins', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'quarterly_revenue_growth': info.get('revenueQuarterlyGrowth', 0),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0),
                'total_cash': info.get('totalCash', 0),
                'total_debt': info.get('totalDebt', 0),
                'total_revenue': info.get('totalRevenue', 0),
                'total_income': info.get('netIncomeToCommon', 0),
                'float_shares': info.get('floatShares', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'shares_short': info.get('sharesShort', 0)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f"获取股票信息失败: {str(e)}",
                'symbol': symbol
            }
    
    def get_financial_statements(self, symbol: str) -> Dict:
        """
        获取财务报表数据
        
        参数:
            symbol: 股票代码
        
        返回:
            包含财务报表的字典
        """
        try:
            stock = yf.Ticker(symbol)
            
            # 获取财务数据
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            
            result = {
                'symbol': symbol,
                'income_statement': financials.to_dict() if not financials.empty else {},
                'balance_sheet': balance_sheet.to_dict() if not balance_sheet.empty else {},
                'cash_flow_statement': cashflow.to_dict() if not cashflow.empty else {}
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f"获取财务报表失败: {str(e)}",
                'symbol': symbol
            }
    
    def get_technical_indicators(self, symbol: str, period: str = "3mo") -> Dict:
        """
        获取技术指标
        
        参数:
            symbol: 股票代码
            period: 数据周期
        
        返回:
            包含技术指标的字典
        """
        try:
            hist = self.get_historical_data(symbol, period=period, interval="1d")
            
            if hist.empty:
                return {'error': '无法获取数据', 'symbol': symbol}
            
            # 计算移动平均线
            hist['MA5'] = hist['Close'].rolling(window=5).mean()
            hist['MA10'] = hist['Close'].rolling(window=10).mean()
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA60'] = hist['Close'].rolling(window=60).mean()
            
            # 计算MACD
            hist['EMA12'] = hist['Close'].ewm(span=12, adjust=False).mean()
            hist['EMA26'] = hist['Close'].ewm(span=26, adjust=False).mean()
            hist['MACD'] = hist['EMA12'] - hist['EMA26']
            hist['Signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
            hist['Histogram'] = hist['MACD'] - hist['Signal']
            
            # 计算RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            
            # 获取最新值
            latest = hist.iloc[-1]
            
            result = {
                'symbol': symbol,
                'price': round(latest['Close'], 2),
                'ma5': round(latest['MA5'], 2) if not pd.isna(latest['MA5']) else None,
                'ma10': round(latest['MA10'], 2) if not pd.isna(latest['MA10']) else None,
                'ma20': round(latest['MA20'], 2) if not pd.isna(latest['MA20']) else None,
                'ma60': round(latest['MA60'], 2) if not pd.isna(latest['MA60']) else None,
                'macd': round(latest['MACD'], 4) if not pd.isna(latest['MACD']) else None,
                'macd_signal': round(latest['Signal'], 4) if not pd.isna(latest['Signal']) else None,
                'macd_histogram': round(latest['Histogram'], 4) if not pd.isna(latest['Histogram']) else None,
                'rsi': round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else None,
                'volume': int(latest['Volume']) if not pd.isna(latest['Volume']) else 0,
                'timestamp': latest.name.strftime('%Y-%m-%d %H:%M:%S') if hasattr(latest.name, 'strftime') else str(latest.name)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f"获取技术指标失败: {str(e)}",
                'symbol': symbol
            }
    
    def batch_get_quotes(self, symbols: List[str]) -> List[Dict]:
        """
        批量获取实时报价
        
        参数:
            symbols: 股票代码列表
        
        返回:
            包含多个股票报价的列表
        """
        results = []
        for symbol in symbols:
            quote = self.get_realtime_quote(symbol)
            results.append(quote)
        return results


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票数据获取工具')
    parser.add_argument('symbol', help='股票代码 (如: 600519.SS, AAPL, 0700.HK)')
    parser.add_argument('--type', choices=['quote', 'info', 'financial', 'technical', 'history'], 
                       default='quote', help='数据类型')
    parser.add_argument('--period', default='3mo', help='历史数据周期 (用于history和technical)')
    parser.add_argument('--interval', default='1d', help='数据间隔 (用于history)')
    parser.add_argument('--output', help='输出文件路径 (JSON格式)')
    
    args = parser.parse_args()
    
    fetcher = StockDataFetcher()
    
    if args.type == 'quote':
        result = fetcher.get_realtime_quote(args.symbol)
    elif args.type == 'info':
        result = fetcher.get_stock_info(args.symbol)
    elif args.type == 'financial':
        result = fetcher.get_financial_statements(args.symbol)
    elif args.type == 'technical':
        result = fetcher.get_technical_indicators(args.symbol, period=args.period)
    elif args.type == 'history':
        hist = fetcher.get_historical_data(args.symbol, period=args.period, interval=args.interval)
        result = {
            'symbol': args.symbol,
            'period': args.period,
            'interval': args.interval,
            'data': hist.to_dict('records') if not hist.empty else []
        }
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
