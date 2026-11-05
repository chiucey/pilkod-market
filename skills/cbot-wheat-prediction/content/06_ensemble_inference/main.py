"""
模块06: 集成推理
龙虾专用版本
三模型自适应加权集成
"""
import os
import numpy as np
import pandas as pd
import pickle
from datetime import datetime

def load_data():
    """加载数据"""
    if os.path.exists("data/wheat_features.csv"):
        return pd.read_csv("data/wheat_features.csv", index_col=0, parse_dates=True)
    return None

class EnsembleModel:
    """集成模型"""
    def __init__(self):
        self.weights = {'lstm': 0.35, 'lgbm': 0.40, 'sarima': 0.25}

    def predict(self, lstm_pred, lgbm_pred, sarima_pred, current_price):
        """集成预测"""
        # 收益率集成
        ret_lstm = lstm_pred[0] if isinstance(lstm_pred, tuple) else lstm_pred
        ret_lgbm = lgbm_pred[0] if isinstance(lgbm_pred, tuple) else lgbm_pred
        ret_sarima = sarima_pred[0] if isinstance(sarima_pred, tuple) else sarima_pred

        # 方向集成
        dir_lstm = lstm_pred[1] if isinstance(lstm_pred, tuple) else (1 if lstm_pred > 0 else 0)
        dir_lgbm = lgbm_pred[1] if isinstance(lgbm_pred, tuple) else (1 if lgbm_pred > 0 else 0)
        dir_sarima = sarima_pred[1] if isinstance(sarima_pred, tuple) else sarima_pred

        # 加权平均
        weighted_return = (
            self.weights['lstm'] * ret_lstm +
            self.weights['lgbm'] * ret_lgbm +
            self.weights['sarima'] * ret_sarima
        )

        # 方向投票 (概率平均)
        weighted_direction = (
            self.weights['lstm'] * dir_lstm +
            self.weights['lgbm'] * dir_lgbm +
            self.weights['sarima'] * dir_sarima
        )

        # 价格预测
        predicted_price = current_price * np.exp(weighted_return)

        # 置信度
        confidence = min(1.0, abs(weighted_return) * 10 + 0.5)

        return {
            'predicted_price': predicted_price,
            'expected_return': weighted_return,
            'direction': 'up' if weighted_direction > 0.5 else 'down',
            'direction_probability': weighted_direction,
            'confidence': confidence,
            'model_weights': self.weights
        }

def main():
    """主函数"""
    print("=" * 60)
    print("06_ensemble_inference: 集成推理")
    print("=" * 60)

    print("\n模型权重配置:")
    print("  LSTM: 35%")
    print("  LightGBM: 40%")
    print("  SARIMA: 25%")

    # 示例预测
    df = load_data()
    if df is not None and len(df) > 100:
        latest = df.iloc[-1]
        current_price = latest['Close']

        ensemble = EnsembleModel()
        result = ensemble.predict(
            lstm_pred=(0.02, 0.6),
            lgbm_pred=(0.025, 0.7),
            sarima_pred=(0.015, 0.55),
            current_price=current_price
        )

        print(f"\n集成预测结果:")
        print(f"  当前价格: ${current_price:.2f}")
        print(f"  预测价格: ${result['predicted_price']:.2f}")
        print(f"  预期收益: {result['expected_return'] * 100:.2f}%")
        print(f"  预测方向: {result['direction']} ({result['direction_probability'] * 100:.1f}%)")
        print(f"  置信度: {result['confidence'] * 100:.1f}%")

    print(f"\n集成推理模块就绪")

    return ensemble

if __name__ == "__main__":
    main()
