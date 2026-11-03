"""
模块02: 数据预处理
龙虾专用版本
数据清洗、特征工程
"""
import os
import pandas as pd
import numpy as np

def load_raw_data():
    """加载原始数据"""
    if os.path.exists("data/wheat_prices.csv"):
        df = pd.read_csv("data/wheat_prices.csv", index_col=0, parse_dates=True)
        return df
    else:
        print("数据文件不存在，请先运行01_data_acquisition")
        return None

def clean_data(df):
    """数据清洗"""
    df_clean = df.copy()

    # 处理缺失值
    df_clean = df_clean.dropna()

    # 处理异常值 (使用3σ原则)
    close = df_clean['Close']
    mean = close.mean()
    std = close.std()
    lower = mean - 3 * std
    upper = mean + 3 * std
    df_clean = df_clean[(close >= lower) & (close <= upper)]

    # 计算对数收益率
    df_clean['Log_Return'] = np.log(df_clean['Close'] / df_clean['Close'].shift(1))
    df_clean = df_clean.dropna()

    return df_clean

def add_features(df):
    """特征工程"""
    df_feat = df.copy()

    # === 技术指标 ===
    # 移动平均线
    for window in [5, 10, 20, 60]:
        df_feat[f'MA_{window}'] = df_feat['Close'].rolling(window=window).mean()
        df_feat[f'Log_Return_MA_{window}'] = df_feat['Log_Return'].rolling(window=window).mean()

    # 波动率指标
    df_feat['Volatility_5'] = df_feat['Log_Return'].rolling(window=5).std()
    df_feat['Volatility_20'] = df_feat['Log_Return'].rolling(window=20).std()

    # RSI
    delta = df_feat['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_feat['RSI'] = 100 - (100 / (1 + rs))

    # 动量指标
    df_feat['Momentum_5'] = df_feat['Close'] / df_feat['Close'].shift(5) - 1
    df_feat['Momentum_20'] = df_feat['Close'] / df_feat['Close'].shift(20) - 1

    # 价格相对位置
    df_feat['Price_Position_20'] = (df_feat['Close'] - df_feat['MA_20']) / df_feat['MA_20']
    df_feat['Price_Position_60'] = (df_feat['Close'] - df_feat['MA_60']) / df_feat['MA_60']

    # === 季节性特征 ===
    df_feat['Month'] = df_feat.index.month
    df_feat['DayOfWeek'] = df_feat.index.dayofweek

    # 月份编码 (正弦/余弦)
    df_feat['Month_Sin'] = np.sin(2 * np.pi * df_feat['Month'] / 12)
    df_feat['Month_Cos'] = np.cos(2 * np.pi * df_feat['Month'] / 12)

    # === 滞后特征 ===
    for lag in [1, 2, 3, 5]:
        df_feat[f'Log_Return_Lag_{lag}'] = df_feat['Log_Return'].shift(lag)

    # 目标变量: 未来22个交易日收益率
    df_feat['Future_Return'] = np.log(df_feat['Close'].shift(-22) / df_feat['Close'])
    df_feat['Future_Direction'] = (df_feat['Future_Return'] > 0).astype(int)

    # 删除NaN
    df_feat = df_feat.dropna()

    return df_feat

def main():
    """主函数"""
    print("=" * 60)
    print("02_data_preprocessing: 数据预处理")
    print("=" * 60)

    df = load_raw_data()
    if df is None:
        return

    print(f"原始数据: {len(df)} 条")

    # 清洗
    df_clean = clean_data(df)
    print(f"清洗后: {len(df_clean)} 条")

    # 特征工程
    df_features = add_features(df_clean)
    print(f"特征工程后: {len(df_features)} 条")
    print(f"特征数量: {len(df_features.columns)}")

    # 保存
    os.makedirs("data", exist_ok=True)
    df_features.to_csv("data/wheat_features.csv")
    print(f"数据保存至 data/wheat_features.csv")

    return df_features

if __name__ == "__main__":
    main()
