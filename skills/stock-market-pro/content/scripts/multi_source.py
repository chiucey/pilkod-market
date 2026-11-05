#!/usr/bin/env python3
"""
多数据源统一接口
支持: yfinance, dfcf(东方财富), futu(富途), sina(新浪), tushare, wind, akshare
"""

import sys
import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re

# 全局配置
OUTPUT_DIR = "/tmp"


def load_config():
    """加载环境变量配置"""
    return {
        "tushare_token": os.environ.get("TUSHARE_TOKEN"),
        "wind_username": os.environ.get("WIND_USERNAME"),
        "wind_password": os.environ.get("WIND_PASSWORD")
    }


def get_source_from_code(ticker, prefer="auto"):
    """根据股票代码推荐最优数据源"""
    if prefer != "auto":
        return prefer
    # 美股
    if re.match(r'^[A-Z]{1,5}$', ticker) and not ticker.isdigit():
        return "yfinance"
    # A股
    if re.match(r'^[0-9]{6}$', ticker):
        return "dfcf"  # 东方财富为A股首选
    # 港股
    if re.match(r'^[0-9]{4,5}$', ticker) or ticker.endswith('.HK'):
        return "futu"  # 富途为港股首选
    return "akshare"


# ---------- 东方财富 (efinance) ----------
def get_price_dfcf(ticker):
    """获取东方财富实时行情"""
    try:
        import efinance as ef
        df = ef.stock.get_realtime_quotes(ticker)
        if df is not None and not df.empty:
            row = df.iloc[0]
            current = row['最新价']
            change = row['涨跌额']
            pct = row['涨跌幅']
            print(f"{ticker}: {current} ({change:+.2f} / {pct:+.2f}%)")
        else:
            print(f"未获取到 {ticker} 行情")
    except ImportError:
        print("请安装 efinance: pip install efinance")
    except Exception as e:
        print(f"东方财富获取失败: {e}")


def get_fundamentals_dfcf(ticker):
    """获取东方财富基本面数据"""
    try:
        import efinance as ef
        info = ef.stock.get_base_info(ticker)
        print(f"=== {ticker} 基本面 (东方财富) ===")
        for k, v in info.items():
            print(f"{k}: {v}")
    except ImportError:
        print("请安装 efinance: pip install efinance")
    except Exception as e:
        print(f"东方财富基本面获取失败: {e}")


def get_history_dfcf(ticker, period="6mo"):
    """获取东方财富历史数据"""
    try:
        import efinance as ef
        end = datetime.now().strftime("%Y%m%d")
        start = _get_start_date(period)
        df = ef.stock.get_quote_history(ticker, start=start, end=end)
        if df is not None and not df.empty:
            df = _normalize_df_columns(df)
            print(f"=== {ticker} {period} 历史数据 (东方财富) ===")
            print(df.tail(30).to_string())
            return df
        else:
            print("无数据")
            return None
    except ImportError:
        print("请安装 efinance: pip install efinance")
    except Exception as e:
        print(f"东方财富历史数据获取失败: {e}")
        return None


# ---------- 新浪财经 (akshare 新浪源) ----------
def get_price_sina(ticker):
    """获取新浪实时行情"""
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_sina()
        row = df[df['symbol'] == ticker]
        if not row.empty:
            current = row['price'].values[0]
            change = row['change'].values[0]
            pct = row['percent'].values[0]
            print(f"{ticker}: {current} ({change:+.2f} / {pct:+.2f}%)")
        else:
            print(f"未找到 {ticker} 行情")
    except ImportError:
        print("请安装 akshare: pip install akshare")
    except Exception as e:
        print(f"新浪获取失败: {e}")


def get_history_sina(ticker, period="6mo"):
    """获取新浪历史数据"""
    try:
        import akshare as ak
        start = _get_start_date(period)
        end = datetime.now().strftime("%Y%m%d")
        df = ak.stock_zh_a_hist(symbol=ticker, period="daily", start_date=start, end_date=end, adjust='')
        if not df.empty:
            df = _normalize_df_columns(df)
            print(f"=== {ticker} {period} 历史数据 (新浪) ===")
            print(df.tail(30).to_string())
            return df
        else:
            print("无数据")
            return None
    except ImportError:
        print("请安装 akshare: pip install akshare")
    except Exception as e:
        print(f"新浪历史数据获取失败: {e}")
        return None


# ---------- 富途牛牛 (futu-api) ----------
def get_price_futu(ticker):
    """获取富途实时行情"""
    try:
        from futu import OpenQuoteContext, RET_OK
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = quote_ctx.get_market_snapshot([ticker])
        if ret == RET_OK:
            row = data.iloc[0]
            current = row['last_price']
            change = row['change_val']
            pct = row['change_rate']
            print(f"{ticker}: {current} ({change:+.2f} / {pct:+.2f}%)")
        else:
            print(f"富途获取失败: {data}")
        quote_ctx.close()
    except ImportError:
        print("请安装 futu-api: pip install futu-api")
        print("并确保 OpenD 网关正在运行 (默认端口 11111)")
    except Exception as e:
        print(f"富途牛牛获取失败: {e}")


def get_history_futu(ticker, period="6mo"):
    """获取富途历史数据"""
    try:
        from futu import OpenQuoteContext, RET_OK, KLType, AuType
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = quote_ctx.get_cur_kline(ticker, 300, KLType.K_DAY, AuType.QFQ)
        if ret == RET_OK:
            data = _normalize_df_columns(data)
            print(f"=== {ticker} {period} 历史数据 (富途) ===")
            print(data.tail(30).to_string())
            return data
        else:
            print(f"富途历史数据获取失败: {data}")
        quote_ctx.close()
    except ImportError:
        print("请安装 futu-api 并运行 OpenD")
    except Exception as e:
        print(f"富途牛牛获取失败: {e}")
        return None


# ---------- Tushare ----------
def get_price_tushare(ticker):
    """获取Tushare实时行情"""
    try:
        import tushare as ts
        config = load_config()
        if not config['tushare_token']:
            print("请设置环境变量 TUSHARE_TOKEN")
            return
        ts.set_token(config['tushare_token'])
        pro = ts.pro_api()
        ts_code = _convert_to_tushare_code(ticker)
        df = pro.daily(ts_code=ts_code, start_date=(datetime.now()-timedelta(days=5)).strftime("%Y%m%d"),
                      end_date=datetime.now().strftime("%Y%m%d"))
        if not df.empty:
            latest = df.iloc[0]
            print(f"{ticker}: {latest['close']} (涨跌幅: {latest['pct_chg']:.2f}%)")
        else:
            print("未获取到数据")
    except ImportError:
        print("请安装 tushare: pip install tushare")
    except Exception as e:
        print(f"Tushare 获取失败: {e}")


def get_history_tushare(ticker, period="6mo"):
    """获取Tushare历史数据"""
    try:
        import tushare as ts
        config = load_config()
        if not config['tushare_token']:
            print("请设置环境变量 TUSHARE_TOKEN")
            return None
        ts.set_token(config['tushare_token'])
        pro = ts.pro_api()
        ts_code = _convert_to_tushare_code(ticker)
        start = _get_start_date(period)
        end = datetime.now().strftime("%Y%m%d")
        df = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
        if not df.empty:
            df = _normalize_df_columns(df)
            print(f"=== {ticker} {period} 历史数据 (Tushare) ===")
            print(df.tail(30).to_string())
            return df
        else:
            print("无数据")
            return None
    except ImportError:
        print("请安装 tushare: pip install tushare")
    except Exception as e:
        print(f"Tushare 历史数据获取失败: {e}")
        return None


# ---------- Wind (框架，需要Wind终端) ----------
def get_price_wind(ticker):
    """Wind 实时行情 (框架)"""
    print(f"Wind 数据源需要配置 WindPy 和 Wind 终端。当前仅提供框架。请手动获取 {ticker} 行情。")


def get_history_wind(ticker, period="6mo"):
    """Wind 历史数据 (框架)"""
    print(f"Wind 历史数据需要 WindPy 接口。跳过。")


# ---------- AkShare (通用) ----------
def get_price_akshare(ticker):
    """获取AkShare实时行情"""
    try:
        import akshare as ak
        if re.match(r'^[0-9]{6}$', ticker):
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == ticker]
            if not row.empty:
                current = row['最新价'].values[0]
                change = row['涨跌额'].values[0]
                pct = row['涨跌幅'].values[0]
                print(f"{ticker}: {current} ({change:+.2f} / {pct:+.2f}%)")
            else:
                print(f"未找到 {ticker}")
        else:
            df = ak.stock_hk_spot()
            row = df[df['代码'] == ticker]
            if not row.empty:
                current = row['现价'].values[0]
                change = row['涨跌'].values[0]
                pct = row['涨跌幅'].values[0]
                print(f"{ticker}: {current} ({change:+.2f} / {pct:+.2f}%)")
            else:
                print(f"未找到 {ticker}")
    except ImportError:
        print("请安装 akshare: pip install akshare")
    except Exception as e:
        print(f"AkShare 获取失败: {e}")


def get_history_akshare(ticker, period="6mo"):
    """获取AkShare历史数据"""
    try:
        import akshare as ak
        start = _get_start_date(period)
        end = datetime.now().strftime("%Y%m%d")
        if re.match(r'^[0-9]{6}$', ticker):
            df = ak.stock_zh_a_hist(symbol=ticker, period="daily", start_date=start, end_date=end, adjust='')
        else:
            df = ak.stock_hk_hist(symbol=ticker, start_date=start, end_date=end, adjust='')
        if not df.empty:
            df = _normalize_df_columns(df)
            print(f"=== {ticker} {period} 历史数据 (AkShare) ===")
            print(df.tail(30).to_string())
            return df
        else:
            print("无数据")
            return None
    except ImportError:
        print("请安装 akshare: pip install akshare")
    except Exception as e:
        print(f"AkShare 历史数据获取失败: {e}")
        return None


# ---------- Yahoo Finance ----------
def get_price_yfinance(ticker):
    """获取Yahoo Finance实时行情"""
    try:
        import yfinance as yf
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        current = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        prev = info.get('regularMarketPreviousClose', 'N/A')
        if isinstance(current, (int, float)) and isinstance(prev, (int, float)):
            change = current - prev
            pct = (change / prev) * 100 if prev else 0
            print(f"{ticker}: {current} ({change:+.2f} / {pct:+.2f}%)")
        else:
            print(f"{ticker}: 当前价 {current}")
    except ImportError:
        print("请安装 yfinance: pip install yfinance")
    except Exception as e:
        print(f"YFinance 获取失败: {e}")


def get_history_yfinance(ticker, period="6mo"):
    """获取Yahoo Finance历史数据"""
    try:
        import yfinance as yf
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period)
        if not df.empty:
            df = _normalize_df_columns(df)
            print(f"=== {ticker} {period} 历史数据 (YFinance) ===")
            print(df.tail(30).to_string())
            return df
        else:
            print("无数据")
            return None
    except ImportError:
        print("请安装 yfinance: pip install yfinance")
    except Exception as e:
        print(f"YFinance 历史数据获取失败: {e}")
        return None


# ---------- 辅助函数 ----------
def _get_start_date(period):
    """根据周期获取开始日期"""
    today = datetime.now()
    period_map = {
        "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
    }
    days = period_map.get(period, 180)
    return (today - timedelta(days=days)).strftime("%Y%m%d")


def _normalize_df_columns(df):
    """标准化DataFrame列名"""
    column_map = {
        '日期': 'Date', '开盘': 'Open', '最高': 'High', '最低': 'Low',
        '收盘': 'Close', '成交量': 'Volume', 'time_key': 'Date',
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
        'vol': 'Volume', 'volume': 'Volume'
    }
    df.rename(columns=column_map, inplace=True)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    return df


def _convert_to_tushare_code(ticker):
    """转换股票代码为Tushare格式"""
    if ticker.endswith('.SH') or ticker.startswith('6'):
        return f"{ticker.zfill(6)}.SH"
    elif ticker.endswith('.SZ') or ticker.startswith('0') or ticker.startswith('3'):
        return f"{ticker.zfill(6)}.SZ"
    elif ticker.endswith('.HK'):
        return ticker
    return ticker


# ---------- 技术指标计算 ----------
def calculate_rsi(data, window=14):
    """计算RSI指标"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(data, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram


def calculate_bollinger_bands(data, window=20, num_std=2):
    """计算布林带"""
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band


def calculate_vwap(data):
    """计算VWAP"""
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
    return vwap


def calculate_atr(data, window=14):
    """计算ATR指标"""
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=window).mean()
    return atr


def generate_chart(df, ticker, period, chart_type, indicators, source):
    """生成专业图表"""
    try:
        if df is None or df.empty:
            print("无数据，无法生成图表")
            return
        # 计算指标
        if 'rsi' in indicators:
            df['RSI'] = calculate_rsi(df)
        if 'macd' in indicators:
            df['MACD'], df['Signal'], df['Histogram'] = calculate_macd(df)
        if 'bb' in indicators:
            df['Upper_BB'], df['Middle_BB'], df['Lower_BB'] = calculate_bollinger_bands(df)
        if 'vwap' in indicators:
            df['VWAP'] = calculate_vwap(df)
        if 'atr' in indicators:
            df['ATR'] = calculate_atr(df)

        num_plots = 1
        if 'rsi' in indicators:
            num_plots += 1
        if 'macd' in indicators:
            num_plots += 1
        if 'atr' in indicators:
            num_plots += 1

        fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3*num_plots), sharex=True)
        if num_plots == 1:
            axes = [axes]

        plot_idx = 0
        ax = axes[plot_idx]
        if chart_type == "line":
            ax.plot(df.index, df['Close'], label='Close', color='blue')
        else:
            ax.plot(df.index, df['Close'], label='Close', color='blue', alpha=0.7)
            ax.fill_between(df.index, df['Low'], df['High'], alpha=0.3, color='gray')
        if 'bb' in indicators:
            ax.plot(df.index, df['Upper_BB'], label='Upper BB', color='red', linestyle='--')
            ax.plot(df.index, df['Middle_BB'], label='Middle BB', color='orange', linestyle='--')
            ax.plot(df.index, df['Lower_BB'], label='Lower BB', color='green', linestyle='--')
        if 'vwap' in indicators:
            ax.plot(df.index, df['VWAP'], label='VWAP', color='purple')
        ax.set_title(f'{ticker} {period} Chart (Source: {source})')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True)
        plot_idx += 1

        if 'rsi' in indicators:
            ax = axes[plot_idx]
            ax.plot(df.index, df['RSI'], label='RSI', color='purple')
            ax.axhline(70, color='red', linestyle='--')
            ax.axhline(30, color='green', linestyle='--')
            ax.set_ylabel('RSI')
            ax.legend()
            ax.grid(True)
            plot_idx += 1

        if 'macd' in indicators:
            ax = axes[plot_idx]
            ax.plot(df.index, df['MACD'], label='MACD', color='blue')
            ax.plot(df.index, df['Signal'], label='Signal', color='orange')
            ax.bar(df.index, df['Histogram'], label='Histogram', color='gray', alpha=0.5)
            ax.set_ylabel('MACD')
            ax.legend()
            ax.grid(True)
            plot_idx += 1

        if 'atr' in indicators:
            ax = axes[plot_idx]
            ax.plot(df.index, df['ATR'], label='ATR', color='brown')
            ax.set_ylabel('ATR')
            ax.set_xlabel('Date')
            ax.legend()
            ax.grid(True)

        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_path = os.path.join(OUTPUT_DIR, f"{ticker}_{source}_{timestamp}.png")
        plt.savefig(chart_path)
        plt.close()
        print(f"Chart saved to: {chart_path}")
        print(f"CHART_PATH:{chart_path}")
    except Exception as e:
        print(f"Chart generation failed: {e}")


# ---------- 统一调度 ----------
def get_price_dispatch(ticker, source):
    """行情获取调度"""
    source_map = {
        "dfcf": get_price_dfcf,
        "sina": get_price_sina,
        "futu": get_price_futu,
        "tushare": get_price_tushare,
        "wind": get_price_wind,
        "akshare": get_price_akshare,
        "yfinance": get_price_yfinance,
    }
    if source in source_map:
        source_map[source](ticker)
    else:
        print(f"Unsupported data source: {source}")


def get_history_dispatch(ticker, period, source):
    """历史数据获取调度"""
    source_map = {
        "dfcf": get_history_dfcf,
        "sina": get_history_sina,
        "futu": get_history_futu,
        "tushare": get_history_tushare,
        "wind": get_history_wind,
        "akshare": get_history_akshare,
        "yfinance": get_history_yfinance,
    }
    if source in source_map:
        return source_map[source](ticker, period)
    else:
        print(f"Unsupported history data source: {source}")
        return None


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="Multi-source stock data interface")
    parser.add_argument("action", choices=["price", "fundamentals", "history", "pro", "report"])
    parser.add_argument("ticker")
    parser.add_argument("--source", default="auto",
                        help="Data source: auto, dfcf, futu, sina, tushare, wind, akshare, yfinance")
    parser.add_argument("--period", default="6mo")
    parser.add_argument("--chart_type", default="candlestick")
    parser.add_argument("--rsi", action="store_true")
    parser.add_argument("--macd", action="store_true")
    parser.add_argument("--bb", action="store_true")
    parser.add_argument("--vwap", action="store_true")
    parser.add_argument("--atr", action="store_true")

    args = parser.parse_args()
    source = args.source if args.source != "auto" else get_source_from_code(args.ticker)

    if args.action == "price":
        get_price_dispatch(args.ticker, source)
    elif args.action == "fundamentals":
        if source in ["dfcf", "auto"]:
            get_fundamentals_dfcf(args.ticker)
        else:
            print(f"{source} does not support fundamentals. Please use dfcf data source.")
    elif args.action == "history":
        get_history_dispatch(args.ticker, args.period, source)
    elif args.action == "pro":
        indicators = []
        for ind in ['rsi', 'macd', 'bb', 'vwap', 'atr']:
            if getattr(args, ind):
                indicators.append(ind)
        df = get_history_dispatch(args.ticker, args.period, source)
        if df is not None:
            generate_chart(df, args.ticker, args.period, args.chart_type, indicators, source)
    elif args.action == "report":
        print(f"=== {args.ticker} Comprehensive Report (Source: {source}) ===")
        get_price_dispatch(args.ticker, source)
        if source in ["dfcf", "auto"]:
            get_fundamentals_dfcf(args.ticker)
        else:
            print("Fundamentals data not available. Please use dfcf data source.")
        df = get_history_dispatch(args.ticker, args.period, source)
        if df is not None:
            generate_chart(df, args.ticker, args.period, "candlestick", ['rsi', 'macd', 'bb'], source)


if __name__ == "__main__":
    main()
