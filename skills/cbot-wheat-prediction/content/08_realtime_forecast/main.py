"""
模块08: 实时预测
龙虾专用版本
30天价格预测
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
import warnings
warnings.filterwarnings('ignore')

# 特征列表
FEATURE_COLS = [
    'Log_Return', 'MA_5', 'MA_10', 'MA_20', 'MA_60',
    'Volatility_5', 'Volatility_20', 'RSI',
    'Momentum_5', 'Momentum_20',
    'Price_Position_20', 'Price_Position_60',
    'Month_Sin', 'Month_Cos',
    'Log_Return_Lag_1', 'Log_Return_Lag_2', 'Log_Return_Lag_3'
]

def load_data():
    """加载最新数据"""
    if os.path.exists("data/wheat_features.csv"):
        return pd.read_csv("data/wheat_features.csv", index_col=0, parse_dates=True)
    return None

def get_latest_features(df):
    """获取最新特征"""
    return df[FEATURE_COLS].iloc[-1:]

class RealtimeForecast:
    """实时预测"""
    def __init__(self):
        self.scaler = StandardScaler()
        self.model_return = Ridge(alpha=1.0)
        self.model_direction = LogisticRegression(max_iter=1000)

    def train(self, df_train):
        """训练模型"""
        X = df_train[FEATURE_COLS].values
        y_return = df_train['Future_Return'].values
        y_direction = df_train['Future_Direction'].values

        X_scaled = self.scaler.fit_transform(X)
        self.model_return.fit(X_scaled, y_return)
        self.model_direction.fit(X_scaled, y_direction)

        return self

    def predict(self, df_latest, horizon=22):
        """预测"""
        X = df_latest[FEATURE_COLS].values
        X_scaled = self.scaler.transform(X)

        # 预测收益率
        pred_return = self.model_return.predict(X_scaled)[0]

        # 预测方向概率
        pred_direction_prob = self.model_direction.predict_proba(X_scaled)[0][1]

        # 当前价格
        current_price = df_latest['Close'].values[0]

        # 预测价格
        pred_price = current_price * np.exp(pred_return)

        # 置信度
        confidence = min(1.0, max(0.5, abs(pred_return) * 20 + 0.6))

        # 预测日期
        last_date = df_latest.index[-1]
        pred_date = last_date + timedelta(days=30)

        return {
            'current_price': current_price,
            'predicted_price': pred_price,
            'predicted_date': pred_date,
            'expected_return': pred_return * 100,
            'direction': '上涨' if pred_direction_prob > 0.5 else '下跌',
            'direction_probability': pred_direction_prob * 100,
            'confidence': confidence * 100,
            'horizon_days': horizon
        }

def main():
    """主函数"""
    print("=" * 70)
    print("08_realtime_forecast: 实时预测（龙虾专用）")
    print("=" * 70)

    df = load_data()
    if df is None:
        print("数据不存在")
        return

    # 最新数据
    latest = df.iloc[-1]
    print(f"\n最新数据日期: {df.index[-1].date()}")
    print(f"最新收盘价: ${latest['Close']:.2f}")

    # 训练数据
    train_end = '2021-01-01'
    df_train = df[df.index < train_end]

    print(f"训练数据: {len(df_train)} 条")

    # 训练模型
    model = RealtimeForecast()
    model.train(df_train)

    # 获取最新特征
    df_latest = df.iloc[-1:]

    # 预测
    result = model.predict(df_latest)

    print("\n" + "=" * 70)
    print("30天价格预测结果")
    print("=" * 70)
    print(f"\n当前价格: ${result['current_price']:.2f}")
    print(f"预测价格: ${result['predicted_price']:.2f}")
    print(f"预测日期: {result['predicted_date'].date()}")
    print(f"预期收益: {result['expected_return']:.2f}%")
    print(f"预测方向: {result['direction']} ({result['direction_probability']:.1f}%)")
    print(f"置信度: {result['confidence']:.1f}%")

    # 置信区间
    volatility = latest['Volatility_20']
    upper = result['current_price'] * np.exp(result['expected_return'] / 100 + 1.96 * volatility)
    lower = result['current_price'] * np.exp(result['expected_return'] / 100 - 1.96 * volatility)

    print(f"\n95%置信区间: ${lower:.2f} - ${upper:.2f}")

    # 保存预测
    os.makedirs("results", exist_ok=True)
    with open("results/latest_forecast.txt", "w") as f:
        f.write(f"预测日期: {datetime.now().date()}\n")
        f.write(f"当前价格: ${result['current_price']:.2f}\n")
        f.write(f"预测价格: ${result['predicted_price']:.2f}\n")
        f.write(f"预期收益: {result['expected_return']:.2f}%\n")
        f.write(f"预测方向: {result['direction']}\n")
        f.write(f"置信度: {result['confidence']:.1f}%\n")

    print(f"\n预测完成")

    return result

if __name__ == "__main__":
    main()
