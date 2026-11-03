"""
CBOT小麦价格预测模型 - OpenClaw 主入口 v5.0
龙虾专用版本
集成所有模块，一键运行完整预测流程
"""
import os
import sys

def print_header():
    """打印欢迎信息"""
    print("=" * 80)
    print("CBOT Wheat Price Prediction - OpenClaw v5.0（龙虾专用）")
    print("目标: 方向准确率 ≥95%, MAPE ≤3.57%")
    print("=" * 80)

def run_module(module_name):
    """运行指定模块"""
    module_paths = {
        "01_data_acquisition": "01_data_acquisition/main.py",
        "02_data_preprocessing": "02_data_preprocessing/main.py",
        "03_model_lstm": "03_model_lstm/main.py",
        "04_model_lightgbm": "04_model_lightgbm/main.py",
        "05_model_sarima": "05_model_sarima/main.py",
        "06_ensemble_inference": "06_ensemble_inference/main.py",
        "07_backtest_evaluation": "07_backtest_evaluation/main.py",
        "08_realtime_forecast": "08_realtime_forecast/main.py",
    }

    if module_name in module_paths:
        module_path = module_paths[module_name]
        if os.path.exists(module_path):
            print(f"\n>>> 运行模块: {module_name}")
            os.system(f"python3 {module_path}")
        else:
            print(f"[警告] 找不到模块: {module_path}")
    else:
        print(f"[错误] 未知模块: {module_name}")
        print_available_modules()

def run_full_pipeline():
    """运行完整流程"""
    modules = [
        "01_data_acquisition",
        "02_data_preprocessing",
        "03_model_lstm",
        "04_model_lightgbm",
        "05_model_sarima",
        "06_ensemble_inference",
        "07_backtest_evaluation",
        "08_realtime_forecast"
    ]

    print("\n" + "=" * 80)
    print("开始执行完整预测流程")
    print("=" * 80)

    for module in modules:
        run_module(module)
        print()

    print("=" * 80)
    print("完整流程执行完成！")
    print("=" * 80)

def print_available_modules():
    """打印可用模块列表"""
    print("\n可用模块:")
    print("  01_data_acquisition      - 数据获取与合成")
    print("  02_data_preprocessing    - 特征工程与标准化")
    print("  03_model_lstm            - LSTM时序预测")
    print("  04_model_lightgbm        - LightGBM回归预测")
    print("  05_model_sarima          - SARIMA季节性预测")
    print("  06_ensemble_inference    - 模型集成推理")
    print("  07_backtest_evaluation   - Walk-Forward回测评估")
    print("  08_realtime_forecast     - 实时预测输出")
    print("\n使用方法:")
    print("  python3 main.py                           - 运行完整流程")
    print("  python3 main.py <module_name>             - 运行指定模块")
    print("  python3 main.py 08_realtime_forecast      - 仅运行实时预测")

if __name__ == "__main__":
    print_header()

    if len(sys.argv) > 1:
        module_name = sys.argv[1]
        run_module(module_name)
    else:
        print_available_modules()
        print("\n正在运行完整流程...")
        run_full_pipeline()
