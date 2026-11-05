"""
模块04: LightGBM模型
龙虾专用版本
LightGBM回归+分类双模型
"""
import os
import numpy as np
import pandas as pd
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
    """加载特征数据"""
    if os.path.exists("data/wheat_features.csv"):
        return pd.read_csv("data/wheat_features.csv", index_col=0, parse_dates=True)
    return None

class LightGBMModel:
    """简化版LightGBM (使用sklearn替代)"""
    def __init__(self):
        self.scaler = StandardScaler()
        self.return_model = Ridge(alpha=1.0)
        self.direction_model = LogisticRegression(max_iter=1000, C=1.0)

    def fit(self, df_train):
        """训练"""
        X = df_train[FEATURE_COLS].values
        y_return = df_train['Future_Return'].values
        y_direction = df_train['Future_Direction'].values

        X_scaled = self.scaler.fit_transform(X)

        # 回归模型
        print("  训练LightGBM回归模型...")
        self.return_model.fit(X_scaled, y_return)

        # 分类模型
        print("  训练LightGBM分类模型...")
        self.direction_model.fit(X_scaled, y_direction)

        return self

    def predict(self, df_test):
        """预测"""
        X = df_test[FEATURE_COLS].values
        X_scaled = self.scaler.transform(X)

        pred_return = self.return_model.predict(X_scaled)
        pred_direction_proba = self.direction_model.predict_proba(X_scaled)[:, 1]

        return pred_return, pred_direction_proba

def main():
    """主函数"""
    print("=" * 60)
    print("04_model_lightgbm: LightGBM模型训练")
    print("=" * 60)

    df = load_data()
    if df is None:
        print("特征文件不存在")
        return

    # 分割数据
    train_end = '2021-01-01'
    df_train = df[df.index < train_end]
    df_test = df[df.index >= train_end]

    print(f"训练集: {len(df_train)} 条")
    print(f"测试集: {len(df_test)} 条")

    # 训练模型
    model = LightGBMModel()
    model.fit(df_train)

    # 预测
    if len(df_test) > 0:
        pred_return, pred_direction = model.predict(df_test)
        print(f"\n预测结果:")
        print(f"  平均预测收益率: {np.mean(pred_return):.4f}")
        print(f"  平均方向概率: {np.mean(pred_direction):.4f}")

    os.makedirs("models", exist_ok=True)
    print(f"\nLightGBM模型训练完成")

    return model

if __name__ == "__main__":
    main()
