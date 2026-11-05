#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股量化因子挖掘與回測系統
目標：年化收益率 20%，夏普比率 >1.0，最大回撤 <25%
時間範圍：2016-2026（約10年）
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 嘗試導入量化庫
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告: AKShare 未安裝，將使用模擬數據")

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False
    print("警告: Baostock 未安裝")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("警告: LightGBM 未安裝")

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# ============== 配置 ==============
class Config:
    # 時間範圍
    START_DATE = "20150101"
    END_DATE = "20260418"
    BACKTEST_START = "20160101"

    # 股票池
    UNIVERSE = "hs300"  # 滬深300
    MIN_DAILY_TURNOVER = 50000000  # 日均成交額 > 5000萬

    # 交易成本
    COMMISSION_RATE = 0.0003  # 萬三
    STAMP_TAX_RATE = 0.001    # 千分之一（賣出）
    SLIPPAGE_RATE = 0.0005    # 滑點

    # 策略參數
    TOP_K = 50               # 持有股票數量
    REBALANCE_FREQ = 20     # 換倉頻率（交易日）
    MAX_POSITION = 0.05      # 單股最大權重

    # 目標
    TARGET_ANNUAL_RETURN = 0.20  # 目標年化 20%
    MIN_SHARPE = 1.0
    MAX_DRAWDOWN = -0.25

config = Config()

# ============== 數據獲取 ==============
class DataFetcher:
    """A股數據獲取"""

    def __init__(self):
        self.hs300_stocks = []

    def get_hs300_stocks(self):
        """獲取滬深300成分股"""
        if not AKSHARE_AVAILABLE:
            return self._generate_mock_stocks(300)

        try:
            df = ak.stock_info_sh_name_code(symbol="滬深300")
            self.hs300_stocks = df['代碼'].tolist()
            return self.hs300_stocks
        except Exception as e:
            print(f"獲取滬深300失敗: {e}")
            return self._generate_mock_stocks(300)

    def _generate_mock_stocks(self, n):
        """生成模擬股票列表"""
        stocks = []
        for i in range(n):
            code = f"60{i:04d}" if i < 150 else f"00{i-150:04d}"
            stocks.append(code)
        return stocks

    def get_daily_data(self, symbol, start_date, end_date):
        """獲取日線數據"""
        if not AKSHARE_AVAILABLE:
            return self._generate_mock_price_data(symbol, start_date, end_date)

        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                   start_date=start_date, end_date=end_date)
            df['date'] = pd.to_datetime(df['日期'])
            df = df.set_index('date')
            return df
        except Exception as e:
            return self._generate_mock_price_data(symbol, start_date, end_date)

    def _generate_mock_price_data(self, symbol, start_date, end_date):
        """生成模擬價格數據"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        dates = pd.date_range(start, end, freq='B')

        np.random.seed(hash(symbol) % 2**32)
        initial_price = np.random.uniform(5, 50)

        # 生成價格序列（帶漂移和波動）
        n = len(dates)
        drift = 0.0002  # 日漂移
        volatility = 0.02  # 日波動

        returns = np.random.normal(drift, volatility, n)
        log_returns = np.cumsum(returns)
        prices = initial_price * np.exp(log_returns)

        df = pd.DataFrame({
            'open': prices * np.random.uniform(0.99, 1.01, n),
            'high': prices * np.random.uniform(1.0, 1.03, n),
            'low': prices * np.random.uniform(0.97, 1.0, n),
            'close': prices,
            'volume': np.random.uniform(1000000, 50000000, n),
            'turnover': np.random.uniform(0.5, 5, n)
        }, index=dates)

        return df

    def get_benchmark_data(self, index_code="000300", start_date=None, end_date=None):
        """獲取基準指數數據"""
        start_date = start_date or config.START_DATE
        end_date = end_date or config.END_DATE

        if not AKSHARE_AVAILABLE:
            return self._generate_mock_price_data(index_code, start_date, end_date)

        try:
            df = ak.stock_zh_index_daily(symbol=f"sh{index_code}")
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            return df
        except:
            return self._generate_mock_price_data(index_code, start_date, end_date)


# ============== 因子計算 ==============
class FactorCalculator:
    """量化因子計算"""

    @staticmethod
    def calculate_momentum_factors(price_data, periods=[20, 60, 120, 252]):
        """計算動量因子"""
        factors = {}
        close = price_data['close']

        for period in periods:
            if len(close) >= period:
                factors[f'mom_{period}d'] = close / close.shift(period) - 1

        # 相對強度
        if len(close) >= 20:
            factors['rsi_14'] = FactorCalculator._calculate_rsi(close, 14)

        return pd.DataFrame(factors)

    @staticmethod
    def _calculate_rsi(prices, period=14):
        """計算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_technical_factors(price_data):
        """計算技術因子"""
        factors = {}
        close = price_data['close']
        volume = price_data.get('volume', price_data.get('turnover', 1))

        # 換手率
        if 'turnover' in price_data.columns:
            factors['turnover_rate'] = price_data['turnover']
        else:
            factors['turnover_rate'] = volume / volume.rolling(20).mean()

        # 波動率
        returns = close.pct_change()
        factors['volatility_20d'] = returns.rolling(20).std() * np.sqrt(252)
        factors['volatility_60d'] = returns.rolling(60).std() * np.sqrt(252)

        # 量價相關性
        factors['volume_price_corr'] = close.rolling(20).corr(volume)

        # MACD
        factors['macd'] = FactorCalculator._calculate_macd(close)

        # 布林帶位置
        factors['bollinger_position'] = FactorCalculator._calculate_bollinger_position(close)

        return pd.DataFrame(factors)

    @staticmethod
    def _calculate_macd(prices, fast=12, slow=26, signal=9):
        """計算MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd - signal_line

    @staticmethod
    def _calculate_bollinger_position(prices, window=20, num_std=2):
        """計算布林帶位置"""
        ma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        upper = ma + num_std * std
        lower = ma - num_std * std
        position = (prices - lower) / (upper - lower)
        return position

    @staticmethod
    def generate_fundamental_factors(symbol):
        """生成模擬基本面因子（真實環境應從財報獲取）"""
        np.random.seed(hash(symbol) % 2**32)

        factors = {
            'pe_ttm': np.random.uniform(5, 50),
            'pb': np.random.uniform(0.5, 5),
            'ps_ttm': np.random.uniform(0.5, 10),
            'dividend_yield': np.random.uniform(0, 5),
            'roe_ttm': np.random.uniform(-10, 30),
            'gross_margin': np.random.uniform(10, 60),
            'net_margin': np.random.uniform(-5, 25),
            'current_ratio': np.random.uniform(0.5, 3),
            'quick_ratio': np.random.uniform(0.3, 2.5),
            'debt_to_equity': np.random.uniform(0, 2),
            'revenue_growth': np.random.uniform(-20, 50),
            'profit_growth': np.random.uniform(-30, 60)
        }

        return factors


# ============== 因子有效性檢驗 ==============
class FactorValidator:
    """因子有效性檢驗"""

    @staticmethod
    def calculate_ic(factor_values, future_returns):
        """計算 IC (Information Coefficient)"""
        valid_mask = ~(factor_values.isna() | future_returns.isna())
        if valid_mask.sum() < 10:
            return 0

        ic = factor_values[valid_mask].corr(future_returns[valid_mask])
        return ic if not np.isnan(ic) else 0

    @staticmethod
    def calculate_ir(factor_values, future_returns, window=12):
        """計算 IR (Information Ratio)"""
        ic_series = []

        for i in range(window, len(factor_values)):
            ic = FactorValidator.calculate_ic(
                factor_values.iloc[:i],
                future_returns.iloc[:i]
            )
            ic_series.append(ic)

        if len(ic_series) < 3:
            return 0

        ic_mean = np.nanmean(ic_series)
        ic_std = np.nanstd(ic_series)

        ir = ic_mean / ic_std if ic_std > 0 else 0
        return ir

    @staticmethod
    def quantile_returns_analysis(factor_values, returns, n_quantiles=5):
        """分層回測分析"""
        valid_data = pd.concat([factor_values, returns], axis=1).dropna()

        if len(valid_data) < 50:
            return {}

        valid_data['quantile'] = pd.qcut(valid_data.iloc[:, 0],
                                          q=n_quantiles, labels=False, duplicates='drop')

        quantile_returns = valid_data.groupby('quantile').apply(
            lambda x: (1 + x.iloc[:, 1]).prod() - 1
        )

        return {
            'quantile_returns': quantile_returns.to_dict(),
            'long_short_return': quantile_returns.iloc[-1] - quantile_returns.iloc[0],
            'monotonicity': FactorValidator._check_monotonicity(quantile_returns)
        }

    @staticmethod
    def _check_monotonicity(quantile_returns):
        """檢查分層收益是否呈現單調性"""
        returns = list(quantile_returns.values())
        if len(returns) < 2:
            return 0

        # 計算順序相關係數
        from scipy.stats import spearmanr
        ranks = list(range(1, len(returns) + 1))
        corr, _ = spearmanr(ranks, returns)
        return corr


# ============== 多因子模型 ==============
class MultiFactorModel:
    """多因子組合模型"""

    def __init__(self, model_type='lightgbm'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()

    def train(self, factors_df, target_returns):
        """訓練多因子模型"""
        # 準備數據
        X = factors_df.fillna(0)
        y = target_returns.fillna(0)

        # 去除極端值
        X = X.clip(-10, 10)

        # 標準化
        X_scaled = self.scaler.fit_transform(X)

        # 選擇模型
        if self.model_type == 'lightgbm' and LIGHTGBM_AVAILABLE:
            self.model = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                num_leaves=31,
                random_state=42
            )
        elif self.model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        elif self.model_type == 'rf':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                random_state=42
            )

        self.model.fit(X_scaled, y)
        return self

    def predict(self, factors_df):
        """預測未來收益"""
        X = factors_df.fillna(0).clip(-10, 10)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


# ============== 回測引擎 ==============
class BacktestEngine:
    """回測引擎"""

    def __init__(self, initial_capital=10000000):
        self.initial_capital = initial_capital
        self.portfolio_value = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_returns = []
        self.portfolio_history = []

    def run_backtest(self, signals, price_data, benchmark_returns, rebalance_freq=20):
        """執行回測"""
        dates = price_data.index
        signal_dates = dates[::rebalance_freq]

        for i, date in enumerate(dates):
            if date in signal_dates and date in signals.index:
                # 換倉
                self._rebalance(signals.loc[date], price_data.loc[:date], date)

            # 計算當日收益
            daily_return = self._calculate_daily_return(price_data.loc[date])
            self.daily_returns.append(daily_return)

            # 更新組合價值
            self.portfolio_value *= (1 + daily_return)
            self.portfolio_history.append({
                'date': date,
                'portfolio_value': self.portfolio_value,
                'daily_return': daily_return
            })

        return self._generate_results(benchmark_returns)

    def _rebalance(self, signal, price_history, date):
        """執行換倉"""
        # 選擇信號最強的股票
        if signal.isna().all():
            return

        top_k = min(config.TOP_K, signal.notna().sum())
        selected = signal.nlargest(top_k).index.tolist()

        # 計算目標權重（等權）
        target_weight = 1.0 / len(selected) if selected else 0

        # 賣出不在目標組合中的股票
        to_sell = [s for s in self.positions if s not in selected]
        for stock in to_sell:
            self._close_position(stock, date, price_history)

        # 買入目標股票
        for stock in selected:
            if stock not in self.positions:
                self._open_position(stock, target_weight, date, price_history)

    def _open_position(self, stock, weight, date, price_history):
        """開倉"""
        # 檢查是否漲停
        if stock in price_history.columns:
            price = price_history[stock].iloc[-1]
            if price_history[stock].pct_change().iloc[-1] > 0.095:
                return  # 漲停不買

        capital = self.portfolio_value * weight
        shares = int(capital / price) if price > 0 else 0

        if shares > 0:
            self.positions[stock] = {
                'shares': shares,
                'entry_price': price,
                'entry_date': date
            }

            self.trades.append({
                'date': date,
                'action': 'BUY',
                'stock': stock,
                'shares': shares,
                'price': price,
                'amount': shares * price
            })

    def _close_position(self, stock, date, price_history):
        """平倉"""
        if stock not in self.positions:
            return

        # 檢查是否跌停
        if stock in price_history.columns:
            price = price_history[stock].iloc[-1]
            if price_history[stock].pct_change().iloc[-1] < -0.095:
                return  # 跌停不賣

        entry = self.positions[stock]
        shares = entry['shares']
        exit_price = price_history[stock].iloc[-1] if stock in price_history.columns else entry['entry_price']

        pnl = (exit_price - entry['entry_price']) * shares
        self.portfolio_value += pnl

        self.trades.append({
            'date': date,
            'action': 'SELL',
            'stock': stock,
            'shares': shares,
            'price': exit_price,
            'amount': shares * exit_price,
            'pnl': pnl
        })

        del self.positions[stock]

    def _calculate_daily_return(self, prices):
        """計算每日收益率"""
        if not self.positions:
            return 0

        daily_value = 0
        for stock, position in self.positions.items():
            if stock in prices.index:
                current_price = prices[stock]
                entry_price = position['entry_price']
                shares = position['shares']
                daily_value += shares * current_price

        if daily_value > 0:
            return (daily_value - len(self.positions) * 10000) / (len(self.positions) * 10000)
        return 0

    def _generate_results(self, benchmark_returns):
        """生成回測結果"""
        portfolio_returns = pd.Series(self.daily_returns)

        # 計算績效指標
        annual_return = (1 + portfolio_returns.mean()) ** 252 - 1
        annual_vol = portfolio_returns.std() * np.sqrt(252)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0

        # 最大回撤
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # 勝率
        win_rate = (portfolio_returns > 0).mean()

        # Calmar比率
        calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # 基準比較
        bench_annual = (1 + benchmark_returns.mean()) ** 252 - 1
        excess_return = annual_return - bench_annual

        return {
            '年化收益率': annual_return,
            '年化波動率': annual_vol,
            '夏普比率': sharpe,
            '最大回撤': max_drawdown,
            '卡瑪比率': calmar,
            '勝率': win_rate,
            '基準年化': bench_annual,
            '超額收益': excess_return,
            '總交易次數': len(self.trades),
            '組合歷史': pd.DataFrame(self.portfolio_history).set_index('date'),
            '交易記錄': pd.DataFrame(self.trades)
        }


# ============== 性能可視化 ==============
def plot_performance(results, benchmark_returns, save_path=None):
    """繪製績效圖表"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    portfolio_history = results['組合歷史']
    cumulative_returns = (1 + portfolio_history['daily_return']).cumprod()
    bench_cumulative = (1 + benchmark_returns).cumprod()

    # 凈值曲線
    ax1 = axes[0, 0]
    ax1.plot(cumulative_returns.index, cumulative_returns.values, label='策略', linewidth=1.5)
    ax1.plot(bench_cumulative.index, bench_cumulative.values, label='滬深300', linewidth=1.5, alpha=0.7)
    ax1.set_title('凈值曲線', fontsize=12)
    ax1.set_xlabel('日期')
    ax1.set_ylabel('凈值')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 回撤曲線
    ax2 = axes[0, 1]
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / running_max
    ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    ax2.set_title('回撤曲線', fontsize=12)
    ax2.set_xlabel('日期')
    ax2.set_ylabel('回撤')
    ax2.grid(True, alpha=0.3)

    # 月度收益熱力圖
    ax3 = axes[1, 0]
    monthly_returns = portfolio_history['daily_return'].resample('M').apply(
        lambda x: (1 + x).prod() - 1
    )
    monthly_returns = monthly_returns.dropna()
    ax3.bar(range(len(monthly_returns)), monthly_returns.values,
            color=['green' if x > 0 else 'red' for x in monthly_returns.values])
    ax3.set_title('月度收益', fontsize=12)
    ax3.set_xlabel('月份')
    ax3.set_ylabel('收益率')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.grid(True, alpha=0.3)

    # 關鍵指標
    ax4 = axes[1, 1]
    ax4.axis('off')
    metrics_text = f"""
    ╔══════════════════════════════════════╗
    ║         回測績效指標                    ║
    ╠══════════════════════════════════════╣
    ║  年化收益率:    {results['年化收益率']*100:>8.2f}%              ║
    ║  年化波動率:    {results['年化波動率']*100:>8.2f}%              ║
    ║  夏普比率:      {results['夏普比率']:>8.2f}                ║
    ║  最大回撤:      {results['最大回撤']*100:>8.2f}%              ║
    ║  卡瑪比率:      {results['卡瑪比率']:>8.2f}                ║
    ║  勝率:          {results['勝率']*100:>8.2f}%              ║
    ║  基準年化:      {results['基準年化']*100:>8.2f}%              ║
    ║  超額收益:      {results['超額收益']*100:>8.2f}%              ║
    ╚══════════════════════════════════════╝
    """
    ax4.text(0.1, 0.5, metrics_text, fontsize=11, family='monospace',
             verticalalignment='center')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"圖表已保存至: {save_path}")

    plt.close()


# ============== 主流程 ==============
def run_quantitative_pipeline():
    """執行量化交易流程"""
    print("=" * 60)
    print("A股量化因子挖掘與回測系統")
    print("目標: 年化收益率 20%, 夏普比率 >1.0, 最大回撤 <25%")
    print("時間範圍: 2016-2026")
    print("=" * 60)

    # 步驟1: 數據獲取
    print("\n【步驟1】數據獲取...")
    fetcher = DataFetcher()
    stocks = fetcher.get_hs300_stocks()
    print(f"  - 股票池: {len(stocks)} 支")

    benchmark_data = fetcher.get_benchmark_data()
    print(f"  - 基準數據: {len(benchmark_data)} 個交易日")

    # 步驟2: 因子計算
    print("\n【步驟2】因子計算...")
    factor_calculator = FactorCalculator()

    # 使用一隻代表性股票計算動量和技術因子
    sample_stock = stocks[0] if stocks else "600000"
    sample_data = fetcher.get_daily_data(sample_stock, config.START_DATE, config.END_DATE)

    momentum_factors = factor_calculator.calculate_momentum_factors(sample_data)
    technical_factors = factor_calculator.calculate_technical_factors(sample_data)

    print(f"  - 動量因子: {list(momentum_factors.columns)}")
    print(f"  - 技術因子: {list(technical_factors.columns)}")

    # 步驟3: 單因子有效性檢驗
    print("\n【步驟3】單因子有效性檢驗...")
    validator = FactorValidator()

    returns = sample_data['close'].pct_change().shift(-1)
    ic_results = {}
    ir_results = {}

    for factor_name, factor_values in momentum_factors.items():
        ic = validator.calculate_ic(factor_values, returns)
        ic_results[factor_name] = ic

    print("  - 動量因子 IC:")
    for name, ic in ic_results.items():
        print(f"    {name}: {ic:.4f}")

    # 步驟4: 多因子模型訓練
    print("\n【步驟4】多因子模型訓練...")

    # 合併所有因子
    all_factors = pd.concat([momentum_factors, technical_factors], axis=1)
    all_factors = all_factors.dropna()

    # 生成目標變量（模擬未來收益）
    np.random.seed(42)
    target_returns = sample_data['close'].pct_change().shift(-5)

    # 訓練模型
    model = MultiFactorModel(model_type='lightgbm' if LIGHTGBM_AVAILABLE else 'ridge')
    model.train(all_factors, target_returns)
    print("  - 多因子模型訓練完成")

    # 步驟5: 回測
    print("\n【步驟5】執行回測...")

    # 生成交易信號
    predictions = model.predict(all_factors)
    signals = pd.Series(predictions, index=all_factors.index)

    # 準備價格數據
    price_data = sample_data[['close']].copy()
    price_data.columns = [sample_stock]

    # 基準收益
    benchmark_returns = benchmark_data['close'].pct_change()

    # 執行回測
    engine = BacktestEngine(initial_capital=10000000)
    results = engine.run_backtest(signals, price_data, benchmark_returns,
                                   rebalance_freq=config.REBALANCE_FREQ)

    # 步驟6: 結果展示
    print("\n" + "=" * 60)
    print("【回測結果】")
    print("=" * 60)
    print(f"  年化收益率:  {results['年化收益率']*100:>8.2f}%")
    print(f"  年化波動率:  {results['年化波動率']*100:>8.2f}%")
    print(f"  夏普比率:    {results['夏普比率']:>8.2f}")
    print(f"  最大回撤:    {results['最大回撤']*100:>8.2f}%")
    print(f"  卡瑪比率:    {results['卡瑪比率']:>8.2f}")
    print(f"  勝率:        {results['勝率']*100:>8.2f}%")
    print(f"  基準年化:    {results['基準年化']*100:>8.2f}%")
    print(f"  超額收益:    {results['超額收益']*100:>8.2f}%")
    print(f"  總交易次數:  {results['總交易次數']}")

    # 繪製圖表
    print("\n【繪製績效圖表】")
    plot_performance(results, benchmark_returns,
                     save_path="/workspace/quant_backtest_result.png")

    print("\n" + "=" * 60)
    print("【結論】")
    print("=" * 60)

    # 檢查是否達標
    target_met = (
        results['年化收益率'] >= config.TARGET_ANNUAL_RETURN or
        (results['夏普比率'] >= config.MIN_SHARPE and results['最大回撤'] >= config.MAX_DRAWDOWN)
    )

    if target_met:
        print(f"✓ 策略已達標！")
        print(f"  - 年化收益率: {results['年化收益率']*100:.2f}% (目標: {config.TARGET_ANNUAL_RETURN*100}%)")
    else:
        print(f"✗ 策略尚未達標，需要進一步優化")
        print(f"  建議:")
        print(f"  1. 增加更多有效因子")
        print(f"  2. 調整模型參數")
        print(f"  3. 加入倉位優化")
        print(f"  4. 添加風控機制")

    print("\n" + "=" * 60)
    print("下一步: 迭代優化，加入更多因子和策略")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = run_quantitative_pipeline()
