"""
模块05: SARIMA模型
龙虾专用版本
季节性时序模型
"""
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """加载数据"""
    if os.path.exists("data/wheat_features.csv"):
        return pd.read_csv("data/wheat_features.csv", index_col=0, parse_dates=True)
    elif os.path.exists("data/wheat_prices.csv"):
        return pd.read_csv("data/wheat_prices.csv", index_col=0, parse_dates=True)
    return None

class SARIMAModel:
    """简化版SARIMA模型"""
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=10.0)

    def fit(self, df_train):
        """训练"""
        # 使用对数收益率序列
        returns = df_train['Log_Return'].values

        # 构建滞后特征
        n = len(returns)
        features = []
        targets = []

        for i in range(20, n - 22):
            # AR特征
            ar = returns[i - 20:i]

            # MA特征
            ma = returns[i - 5:i]

            # 季节性特征 (约21天/月)
            seasonal = []
            for lag in [21, 42, 63]:
                if i - lag >= 0:
                    seasonal.append(returns[i - lag])

            # 组合特征
            feat = np.concatenate([ar[-10:], ma[-3:], seasonal])
            features.append(feat)
            targets.append(returns[i])

        features = np.array(features)
        targets = np.array(targets)

        print(f"  训练数据: {len(features)} 条")
        self.model.fit(features, targets)

        return self

    def predict(self, df_test, horizon=22):
        """预测未来收益"""
        returns = df_test['Log_Return'].values
        n = len(returns)

        predictions = []
        for i in range(max(20, n - 100), n):
            ar = returns[i - 20:i]
            ma = returns[i - 5:i]

            seasonal = []
            for lag in [21, 42, 63]:
                if i - lag >= 0:
                    seasonal.append(returns[i - lag])

            feat = np.concatenate([ar[-10:], ma[-3:], seasonal])
            predictions.append(self.model.predict([feat])[0])

        # 返回多个预测取平均
        avg_return = np.mean(predictions)

        # 方向预测
        direction = 1 if avg_return > 0 else 0

        return avg_return, direction

def main():
    """主函数"""
    print("=" * 60)
    print("05_model_sarima: SARIMA模型训练")
    print("=" * 60)

    df = load_data()
    if df is None:
        print("数据文件不存在")
        return

    # 分割
    train_end = '2021-01-01'
    df_train = df[df.index < train_end]
    df_test = df[df.index >= train_end]

    print(f"训练集: {len(df_train)} 条")
    print(f"测试集: {len(df_test)} 条")

    # 训练
    model = SARIMAModel()
    model.fit(df_train)

    # 预测
    pred_return, pred_direction = model.predict(df_test)
    print(f"\n预测结果:")
    print(f"  预测收益率: {pred_return:.4f}")
    print(f"  预测方向: {'上涨' if pred_direction else '下跌'}")

    os.makedirs("models", exist_ok=True)
    print(f"\nSARIMA模型训练完成")

    return model

if __name__ == "__main__":
    main()
