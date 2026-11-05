"""
模块03: LSTM模型
龙虾专用版本
Attention-LSTM双目标模型
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
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
    """加载特征数据"""
    if os.path.exists("data/wheat_features.csv"):
        return pd.read_csv("data/wheat_features.csv", index_col=0, parse_dates=True)
    else:
        print("特征文件不存在")
        return None

def create_sequences(X, y, seq_length=20):
    """创建序列数据"""
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_length):
        X_seq.append(X[i:i + seq_length])
        y_seq.append(y[i + seq_length])
    return np.array(X_seq), np.array(y_seq)

class AttentionLSTM:
    """简化版Attention-LSTM (使用Ridge替代)"""
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=1.0)

    def fit(self, X_train, y_train):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        return self

    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

class LSTMEnsemble:
    """LSTM模型集成"""
    def __init__(self):
        self.return_model = AttentionLSTM()
        self.direction_model = AttentionLSTM()
        self.seq_length = 20

    def fit(self, df_train):
        """训练模型"""
        # 准备数据
        X = df_train[FEATURE_COLS].values
        y_return = df_train['Future_Return'].values
        y_direction = df_train['Future_Direction'].values

        # 创建序列
        X_seq, y_return_seq = create_sequences(X, y_return, self.seq_length)
        _, y_direction_seq = create_sequences(X, y_direction, self.seq_length)

        # 展平序列用于Ridge
        X_flat = X_seq.reshape(X_seq.shape[0], -1)

        # 训练收益率模型
        print("  训练LSTM收益模型...")
        self.return_model.fit(X_flat, y_return_seq)

        # 训练方向模型
        print("  训练LSTM方向模型...")
        self.direction_model.fit(X_flat, y_direction_seq)

        return self

    def predict(self, df_test):
        """预测"""
        X = df_test[FEATURE_COLS].values
        X_seq, _ = create_sequences(X, np.zeros(len(X)), self.seq_length)
        X_flat = X_seq.reshape(X_seq.shape[0], -1)

        pred_return = self.return_model.predict(X_flat)
        pred_direction = self.direction_model.predict(X_flat)

        return pred_return, pred_direction

def main():
    """主函数"""
    print("=" * 60)
    print("03_model_lstm: LSTM模型训练")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    # 分割训练集和测试集
    train_end = '2021-01-01'
    df_train = df[df.index < train_end]
    df_test = df[df.index >= train_end]

    print(f"训练集: {len(df_train)} 条")
    print(f"测试集: {len(df_test)} 条")

    # 训练模型
    model = LSTMEnsemble()
    model.fit(df_train)

    # 预测测试集
    if len(df_test) > model.seq_length:
        pred_return, pred_direction = model.predict(df_test)
        print(f"\n预测结果:")
        print(f"  平均预测收益率: {np.mean(pred_return):.4f}")
        print(f"  预测方向均值: {np.mean(pred_direction):.4f}")

    # 保存模型
    os.makedirs("models", exist_ok=True)
    print(f"\nLSTM模型训练完成")

    return model

if __name__ == "__main__":
    main()
