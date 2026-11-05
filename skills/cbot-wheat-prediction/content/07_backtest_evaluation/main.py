"""
模块07: 回测评估
龙虾专用版本
60个月Walk-Forward回测
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

def mape(actual, predicted):
    """计算MAPE"""
    actual = np.array(actual)
    predicted = np.array(predicted)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

def calculate_metrics(df_results):
    """计算评估指标"""
    correct_direction = (df_results['Actual_Direction'] == df_results['Pred_Direction']).sum()
    total = len(df_results)
    direction_accuracy = correct_direction / total * 100

    # MAPE
    mape_value = mape(
        df_results['Actual_Price'].values,
        df_results['Predicted_Price'].values
    )

    return {
        'direction_accuracy': direction_accuracy,
        'mape': mape_value,
        'total_predictions': total
    }

def walk_forward_backtest(df, train_window=252 * 3, test_window=22):
    """
    Walk-Forward回测
    train_window: 训练窗口 (约3年)
    test_window: 测试窗口 (约22交易日/月)
    """
    print("\n" + "=" * 70)
    print("07_backtest_evaluation: 60个月Walk-Forward回测")
    print("=" * 70)

    # 准备数据
    df = df[df['Future_Return'].notna()].copy()

    results = []
    n_periods = 60  # 60个月
    predictions_per_period = 22

    start_idx = train_window
    current_idx = start_idx

    print(f"\n回测配置:")
    print(f"  训练窗口: {train_window} 天")
    print(f"  预测周期: {test_window} 天")
    print(f"  目标周期: {n_periods} 个月")

    # 简化版本: 每月进行一次预测
    monthly_predictions = []
    actual_returns = []

    for month in range(n_periods):
        if current_idx + test_window > len(df):
            break

        # 训练数据
        train_end = current_idx
        train_start = max(0, train_end - train_window)
        df_train = df.iloc[train_start:train_end]

        # 预测点
        test_idx = current_idx
        if test_idx + test_window >= len(df):
            break

        # 当前价格 (预测时点的价格)
        current_price = df.iloc[test_idx]['Close']

        # 使用特征数据中预计算的Future_Return
        future_return = df.iloc[test_idx]['Future_Return']
        future_direction = df.iloc[test_idx]['Future_Direction']

        # 训练模型
        scaler = StandardScaler()
        X_train = scaler.fit_transform(df_train[FEATURE_COLS].values)
        y_train_return = df_train['Future_Return'].values
        y_train_direction = df_train['Future_Direction'].values

        # Ridge回归
        model_return = Ridge(alpha=1.0)
        model_return.fit(X_train, y_train_return)

        # Logistic回归
        model_direction = LogisticRegression(max_iter=1000)
        model_direction.fit(X_train, y_train_direction)

        # 预测
        X_test = scaler.transform(df.iloc[[test_idx]][FEATURE_COLS].values)

        pred_return = model_return.predict(X_test)[0]
        pred_direction_prob = model_direction.predict_proba(X_test)[0][1]

        # === 历史中位数 + 方向修正策略 ===
        historical_returns = df_train['Future_Return'].values
        median_return = np.median(historical_returns)

        model_weight = 0.3
        final_pred_return = model_weight * pred_return + (1 - model_weight) * median_return

        # 方向一致性修正
        if pred_direction_prob > 0.5:
            final_pred_return = max(0, final_pred_return)
        else:
            final_pred_return = min(0, final_pred_return)

        # 实际值
        actual_return = future_return
        actual_direction = int(future_direction)

        # 预测价格
        pred_price = current_price * np.exp(final_pred_return)

        # 实际22天后价格
        actual_price = df.iloc[test_idx]['Close'] * np.exp(actual_return)

        monthly_predictions.append(pred_direction_prob)
        actual_returns.append(actual_return)

        # 保存结果
        results.append({
            'Month': month + 1,
            'Date': df.iloc[test_idx].name,
            'Current_Price': current_price,
            'Predicted_Price': pred_price,
            'Actual_Price': actual_price,
            'Pred_Return': pred_return,
            'Actual_Return': actual_return,
            'Pred_Direction': 1 if pred_direction_prob > 0.5 else 0,
            'Actual_Direction': actual_direction
        })

        current_idx += test_window

        # 进度显示
        if (month + 1) % 12 == 0:
            print(f"  完成 {month + 1}/{n_periods} 个月...")

    # 转换为DataFrame
    df_results = pd.DataFrame(results)

    # 计算指标
    metrics = calculate_metrics(df_results)

    print("\n" + "=" * 70)
    print("回测结果汇总")
    print("=" * 70)
    print(f"\n方向准确率: {metrics['direction_accuracy']:.2f}%")
    print(f"MAPE: {metrics['mape']:.2f}%")
    print(f"总预测次数: {metrics['total_predictions']}")

    # 目标检查
    print("\n目标达成情况:")
    print(f"  方向准确率 ≥95%: {'达成' if metrics['direction_accuracy'] >= 95 else '未达成'}")
    print(f"  MAPE ≤3.57%: {'达成' if metrics['mape'] <= 3.57 else '未达成'}")

    # 保存结果
    os.makedirs("results", exist_ok=True)
    df_results.to_csv("results/backtest_results.csv", index=False)

    # 打印样本
    print("\n预测样本 (前5个月):")
    print(df_results[['Month', 'Date', 'Current_Price', 'Predicted_Price', 'Actual_Price',
                      'Pred_Return', 'Actual_Return', 'Pred_Direction', 'Actual_Direction']].head().to_string())

    return df_results, metrics

def main():
    """主函数"""
    print("=" * 70)
    print("CBOT小麦价格预测 - 60个月Walk-Forward回测（龙虾专用）")
    print("目标: 方向准确率 ≥95%, MAPE ≤3.57%")
    print("=" * 70)

    df = load_data()
    if df is None:
        print("特征文件不存在，请先运行数据获取和预处理")
        return

    print(f"数据范围: {df.index[0].date()} 至 {df.index[-1].date()}")
    print(f"数据点数: {len(df)}")

    # 执行回测
    df_results, metrics = walk_forward_backtest(df)

    # 保存指标
    with open("results/metrics.txt", "w") as f:
        f.write(f"方向准确率: {metrics['direction_accuracy']:.2f}%\n")
        f.write(f"MAPE: {metrics['mape']:.2f}%\n")
        f.write(f"总预测次数: {metrics['total_predictions']}\n")

    print(f"\n回测完成，结果保存至 results/")

    return df_results, metrics

if __name__ == "__main__":
    main()
