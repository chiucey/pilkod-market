# -*- coding: utf-8 -*-
"""
数据获取模块 - 基于TuShare的A股数据获取
使用TuShare Pro API获取股票历史行情数据
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Union
from pathlib import Path
import pandas as pd
import time

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    raise ImportError("请先安装 tushare: pip install tushare")

from config import DATA_CONFIG

logger = logging.getLogger(__name__)

# TuShare Token
TUSHARE_TOKEN = "57c09c9e47412e19e8afd77cb575ed948ce37e048b9a563525c06b62"


class StockDataFetcher:
    """
    股票数据获取器
    从TuShare Pro获取A股历史数据，支持缓存功能
    禁止使用模拟数据，确保数据真实性
    """

    def __init__(self, token: Optional[str] = None, cache_dir: Optional[Path] = None):
        """
        初始化数据获取器

        Args:
            token: TuShare Token，默认使用预设token
            cache_dir: 数据缓存目录
        """
        self.cache_dir = cache_dir or DATA_CONFIG.get("cache_dir")
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        if not TUSHARE_AVAILABLE:
            raise RuntimeError("TuShare未安装，请执行: pip install tushare")

        # 初始化TuShare
        try:
            ts.set_token(token or TUSHARE_TOKEN)
            self.pro = ts.pro_api()
            logger.info("TuShare Pro API 初始化成功")
            
            # 测试连接
            test_df = self.pro.query('trade_cal', exchange='SSE', start_date='20240101', end_date='20240110')
            if test_df is not None:
                logger.info("TuShare API 连接正常")
            else:
                logger.warning("TuShare API 返回空数据，请检查网络和Token")
                
        except Exception as e:
            logger.error(f"TuShare初始化失败: {e}")
            raise RuntimeError(f"TuShare初始化失败: {e}")

    def _get_cache_path(self, symbol: str, start_date: str, end_date: str) -> Path:
        """获取缓存文件路径"""
        cache_file = f"{symbol}_{start_date}_{end_date}.csv"
        return self.cache_dir / cache_file

    def _load_from_cache(self, cache_path: Path) -> Optional[pd.DataFrame]:
        """从缓存加载数据"""
        if cache_path.exists():
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                logger.info(f"从缓存加载数据: {cache_path.name}")
                return df
            except Exception as e:
                logger.warning(f"缓存读取失败: {e}")
                return None
        return None

    def _save_to_cache(self, df: pd.DataFrame, cache_path: Path) -> None:
        """保存数据到缓存"""
        try:
            df.to_csv(cache_path)
            logger.info(f"数据已缓存: {cache_path.name}")
        except Exception as e:
            logger.warning(f"缓存保存失败: {e}")

    def _normalize_date(self, date) -> str:
        """标准化日期格式为YYYYMMDD"""
        if isinstance(date, datetime):
            return date.strftime("%Y%m%d")
        elif isinstance(date, str):
            return date.replace("-", "")
        return str(date)

    def fetch_stock_data(
        self,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        获取股票历史数据（真实数据，不使用模拟数据）

        Args:
            symbol: 股票代码（如 000001、600000）
            start_date: 开始日期（YYYY-MM-DD格式）
            end_date: 结束日期（YYYY-MM-DD格式）
            use_cache: 是否使用缓存

        Returns:
            包含OHLCV数据的DataFrame

        Raises:
            RuntimeError: 当无法获取真实数据时抛出异常
        """
        # 标准化日期格式
        start_str = self._normalize_date(start_date)
        end_str = self._normalize_date(end_date)

        # 尝试从缓存加载
        if use_cache:
            cache_path = self._get_cache_path(symbol, start_str, end_str)
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data

        # 从TuShare获取真实数据
        logger.info(f"正在从TuShare获取 {symbol} 的真实数据...")
        df = self._fetch_from_tushare(symbol, start_str, end_str)
        
        if df is None or df.empty:
            raise RuntimeError(f"无法获取 {symbol} 的真实数据，请检查网络或股票代码是否正确")
        
        # 验证数据真实性
        if len(df) < 10:
            logger.warning(f"获取到的数据量较少: {len(df)} 条记录")
        
        # 检查价格范围是否合理
        avg_price = df['close'].mean()
        if symbol.startswith('6') and avg_price < 100:
            logger.warning(f"注意: {symbol} 平均价格 {avg_price:.2f} 元，请确认是否正确")
        elif not symbol.startswith('6') and avg_price < 5:
            logger.warning(f"注意: {symbol} 平均价格 {avg_price:.2f} 元，请确认是否正确")

        # 保存到缓存
        if use_cache and not df.empty:
            cache_path = self._get_cache_path(symbol, start_str, end_str)
            self._save_to_cache(df, cache_path)

        return df

    def _fetch_from_tushare(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        从TuShare Pro获取真实数据

        Args:
            symbol: 股票代码（如 000001、600000）
            start_date: 开始日期（YYYYMMDD格式）
            end_date: 结束日期（YYYYMMDD格式）

        Returns:
            股票数据DataFrame
        """
        try:
            # 标准化股票代码
            ts_code = self._to_tushare_code(symbol)
            logger.info(f"请求TuShare: {ts_code}, {start_date} - {end_date}")
            
            # 获取日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )

            if df is None or df.empty:
                logger.error(f"TuShare返回空数据: {symbol}")
                return pd.DataFrame()

            # 按日期排序
            df = df.sort_values('trade_date')

            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.rename(columns={'trade_date': 'date'})
            df.set_index('date', inplace=True)

            # 重命名列
            df = df.rename(columns={
                'ts_code': 'symbol',
                'vol': 'volume',
            })

            # 确保列顺序
            columns_order = ['symbol', 'open', 'high', 'low', 'close', 'volume', 'amount']
            for col in columns_order:
                if col not in df.columns:
                    df[col] = 0
            df = df[columns_order]

            logger.info(f"成功获取 {symbol} 真实数据，共 {len(df)} 条记录")
            if len(df) > 0:
                logger.info(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
            
            return df

        except Exception as e:
            logger.error(f"TuShare数据获取失败: {e}")
            return pd.DataFrame()

    def _to_tushare_code(self, symbol: str) -> str:
        """
        转换股票代码为TuShare格式

        Args:
            symbol: 原始代码（如 000001、600000）

        Returns:
            TuShare格式代码（如 000001.SZ、600000.SH）
        """
        symbol = symbol.strip()
        if '.' in symbol:
            return symbol

        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith('0'):
            return f"{symbol}.SZ"
        elif symbol.startswith('3'):
            return f"{symbol}.SZ"
        else:
            return f"{symbol}.SZ"

    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        批量获取多只股票数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            字典，键为股票代码，值为对应的DataFrame
        """
        results = {}
        for symbol in symbols:
            try:
                df = self.fetch_stock_data(symbol, start_date, end_date, use_cache)
                if df is not None and not df.empty:
                    results[symbol] = df
                else:
                    logger.error(f"获取 {symbol} 数据失败: 返回空数据")
            except Exception as e:
                logger.error(f"获取 {symbol} 数据失败: {e}")
        return results

    def get_stock_basic_info(self, symbol: str = None) -> pd.DataFrame:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码，不传则获取所有股票

        Returns:
            股票基本信息DataFrame
        """
        try:
            if symbol:
                ts_code = self._to_tushare_code(symbol)
                df = self.pro.stock_basic(ts_code=ts_code, list_status='L')
            else:
                df = self.pro.stock_basic(exchange='', list_status='L')
            return df
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return pd.DataFrame()

    def clear_cache(self, symbol: Optional[str] = None):
        """
        清除缓存数据

        Args:
            symbol: 股票代码，不传则清除所有缓存
        """
        if symbol:
            for cache_file in self.cache_dir.glob(f"{symbol}_*.csv"):
                cache_file.unlink()
                logger.info(f"已删除缓存: {cache_file.name}")
        else:
            for cache_file in self.cache_dir.glob("*.csv"):
                cache_file.unlink()
                logger.info(f"已删除缓存: {cache_file.name}")


# 便捷函数
def fetch_stock(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """便捷函数：获取单只股票数据"""
    fetcher = StockDataFetcher()
    return fetcher.fetch_stock_data(symbol, start_date, end_date)


def test_connection():
    """测试TuShare连接"""
    print("=" * 60)
    print("测试TuShare连接")
    print("=" * 60)
    
    try:
        fetcher = StockDataFetcher()
        
        # 测试获取平安银行数据（2024年）
        df = fetcher.fetch_stock_data("000001", "2024-01-01", "2024-03-31", use_cache=False)
        
        if df is not None and not df.empty:
            print("\n✅ TuShare连接成功！")
            print(f"\n平安银行(000001) 2024年Q1数据:")
            print(df.head(10))
            print(f"\n数据条数: {len(df)}")
            print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
            print(f"平均价格: {df['close'].mean():.2f}")
            
            # 验证价格合理性
            if 8 < df['close'].mean() < 15:
                print("\n✅ 价格范围合理（平安银行实际价格10-12元）")
            else:
                print(f"\n⚠️ 价格范围异常，请检查")
            
            return True
        else:
            print("\n❌ TuShare返回空数据")
            return False
            
    except Exception as e:
        print(f"\n❌ TuShare连接失败: {e}")
        print("\n请检查:")
        print("1. 网络连接是否正常")
        print("2. TuShare Token是否有效")
        print("3. 是否已安装 tushare: pip install tushare")
        return False


if __name__ == "__main__":
    # 测试数据获取
    logging.basicConfig(level=logging.INFO)
    
    # 测试连接
    test_connection()
