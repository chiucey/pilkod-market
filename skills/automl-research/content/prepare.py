#!/usr/bin/env python3
"""
AutoML Research - Data Preparation Module
固定代码：数据加载、预处理、评估指标
不要修改此文件！
"""

import os
import sys
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, log_loss,
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error
)

# 缓存目录
CACHE_DIR = '.automl_cache'


def get_task_config():
    """从配置文件或环境变量读取任务配置"""
    config_file = os.path.join(CACHE_DIR, 'config.json')

    config = {
        'data_path': './data.csv',
        'target_col': 'target',
        'task_type': 'classification',  # classification, regression, multiclass
        'metric': 'accuracy',  # 默认指标
        'time_budget': 120,  # 秒
        'random_seed': 42,
        'test_size': 0.2,
        'cv_folds': 5,
    }

    # 从文件加载
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
            config.update(file_config)

    # 环境变量覆盖
    if os.environ.get('AUTOML_DATA'):
        config['data_path'] = os.environ['AUTOML_DATA']
    if os.environ.get('AUTOML_TARGET'):
        config['target_col'] = os.environ['AUTOML_TARGET']
    if os.environ.get('AUTOML_TASK'):
        config['task_type'] = os.environ['AUTOML_TASK']
    if os.environ.get('AUTOML_METRIC'):
        config['metric'] = os.environ['AUTOML_METRIC']
    if os.environ.get('AUTOML_TIME_BUDGET'):
        config['time_budget'] = int(os.environ['AUTOML_TIME_BUDGET'])
    if os.environ.get('AUTOML_SEED'):
        config['random_seed'] = int(os.environ['AUTOML_SEED'])

    return config


def infer_task_type(y):
    """自动推断任务类型"""
    n_unique = len(np.unique(y))

    if pd.api.types.is_numeric_dtype(y):
        if n_unique <= 20 and n_unique / len(y) < 0.05:
            # 可能是分类
            return 'multiclass' if n_unique > 2 else 'classification'
        else:
            return 'regression'
    else:
        # 非数值类型，是分类
        return 'multiclass' if n_unique > 2 else 'classification'


def get_default_metric(task_type):
    """根据任务类型获取默认评估指标"""
    metrics_map = {
        'classification': 'accuracy',
        'multiclass': 'f1_macro',
        'regression': 'rmse'
    }
    return metrics_map.get(task_type, 'accuracy')


def validate_config(config):
    """验证配置是否有效"""
    # 检查数据文件
    if not os.path.exists(config['data_path']):
        raise FileNotFoundError(f"数据文件不存在: {config['data_path']}")

    # 读取数据检查目标列
    df = pd.read_csv(config['data_path'], nrows=5)
    if config['target_col'] not in df.columns:
        raise ValueError(f"目标列 '{config['target_col']}' 不存在。可用列: {list(df.columns)}")

    # 验证任务类型
    valid_tasks = ['classification', 'regression', 'multiclass']
    if config['task_type'] not in valid_tasks:
        raise ValueError(f"无效的任务类型: {config['task_type']}。可用: {valid_tasks}")

    # 验证指标
    valid_metrics = {
        'classification': ['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
        'multiclass': ['accuracy', 'f1_macro', 'f1_weighted', 'f1_micro'],
        'regression': ['rmse', 'mae', 'r2', 'mape']
    }

    task_metrics = valid_metrics.get(config['task_type'], [])
    if config['metric'] not in task_metrics:
        print(f"警告: 指标 '{config['metric']}' 可能不适合任务类型 '{config['task_type']}'")
        print(f"推荐指标: {task_metrics}")


def load_raw_data(config):
    """加载原始数据"""
    print(f"加载数据: {config['data_path']}")

    # 尝试不同编码
    encodings = ['utf-8', 'gbk', 'latin1']
    for encoding in encodings:
        try:
            df = pd.read_csv(config['data_path'], encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("无法解码数据文件，请检查编码")

    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")

    # 分离特征和目标
    if config['target_col'] not in df.columns:
        raise ValueError(f"目标列 '{config['target_col']}' 不存在")

    X = df.drop(columns=[config['target_col']])
    y = df[config['target_col']].copy()

    # 自动推断任务类型（如果未指定）
    if config.get('auto_infer_task', True):
        inferred_task = infer_task_type(y)
        if config['task_type'] == 'classification' and inferred_task == 'multiclass':
            config['task_type'] = 'multiclass'
            print(f"自动推断为多分类任务 (类别数: {len(np.unique(y))})")
        elif config['task_type'] not in ['classification', 'regression', 'multiclass']:
            config['task_type'] = inferred_task
            print(f"自动推断任务类型: {inferred_task}")

    return X, y


def analyze_features(X):
    """分析特征类型"""
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

    # 检查数值列中是否有应该是类别的
    for col in numeric_cols[:]:
        n_unique = X[col].nunique()
        if n_unique <= 10 and n_unique / len(X) < 0.01:
            # 可能是类别编码
            print(f"注意: {col} 可能是类别特征 (唯一值: {n_unique})")

    return numeric_cols, categorical_cols


def preprocess_features(X_train, X_val, config=None):
    """特征预处理"""
    X_train = X_train.copy()
    X_val = X_val.copy()

    # 识别特征类型
    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()

    # 处理缺失值
    for col in numeric_cols:
        if X_train[col].isnull().any():
            median_val = X_train[col].median()
            X_train[col] = X_train[col].fillna(median_val)
            X_val[col] = X_val[col].fillna(median_val)

    for col in categorical_cols:
        if X_train[col].isnull().any():
            mode_val = X_train[col].mode()[0] if not X_train[col].mode().empty else 'missing'
            X_train[col] = X_train[col].fillna(mode_val)
            X_val[col] = X_val[col].fillna(mode_val)

    # 类别特征编码
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        # 合并训练集和验证集的唯一值
        all_values = pd.concat([X_train[col], X_val[col]]).astype(str).unique()
        le.fit(all_values)

        X_train[col] = le.transform(X_train[col].astype(str))
        X_val[col] = le.transform(X_val[col].astype(str))

        encoders[col] = le

    # 数值特征标准化
    scalers = {}
    if numeric_cols:
        scaler = StandardScaler()
        X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
        X_val[numeric_cols] = scaler.transform(X_val[numeric_cols])
        scalers['numeric'] = scaler

    # 保存预处理器
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, 'encoders.pkl'), 'wb') as f:
        pickle.dump({'encoders': encoders, 'scalers': scalers,
                     'numeric_cols': numeric_cols, 'categorical_cols': categorical_cols}, f)

    return X_train, X_val


def encode_target(y_train, y_val, task_type):
    """编码目标变量"""
    if task_type == 'regression':
        return y_train.values.astype(float), y_val.values.astype(float), None

    # 分类任务
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train.astype(str))
    y_val_encoded = le.transform(y_val.astype(str))

    # 保存编码器
    with open(os.path.join(CACHE_DIR, 'label_encoder.pkl'), 'wb') as f:
        pickle.dump(le, f)

    return y_train_encoded, y_val_encoded, le


def load_data(config=None):
    """主函数：加载和预处理数据"""
    if config is None:
        config = get_task_config()

    # 创建缓存目录
    os.makedirs(CACHE_DIR, exist_ok=True)

    # 保存配置
    with open(os.path.join(CACHE_DIR, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 加载原始数据
    X, y = load_raw_data(config)

    # 分析特征
    numeric_cols, categorical_cols = analyze_features(X)
    print(f"数值特征: {len(numeric_cols)} 个, 类别特征: {len(categorical_cols)} 个")

    # 划分训练集和验证集
    stratify = y if config['task_type'] != 'regression' else None
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=config['test_size'],
        random_state=config['random_seed'],
        stratify=stratify
    )

    print(f"训练集: {len(X_train)}, 验证集: {len(X_val)}")

    # 预处理特征
    X_train_processed, X_val_processed = preprocess_features(X_train, X_val, config)

    # 编码目标
    y_train_encoded, y_val_encoded, label_encoder = encode_target(
        y_train, y_val, config['task_type']
    )

    # 保存数据缓存（可选，用于调试）
    data_cache = {
        'X_train': X_train_processed,
        'X_val': X_val_processed,
        'y_train': y_train_encoded,
        'y_val': y_val_encoded,
        'feature_names': list(X_train_processed.columns),
    }
    with open(os.path.join(CACHE_DIR, 'data_cache.pkl'), 'wb') as f:
        pickle.dump(data_cache, f)

    return X_train_processed, X_val_processed, y_train_encoded, y_val_encoded


def evaluate_model(y_true, y_pred, task_type, metric, y_prob=None):
    """
    评估模型性能

    参数:
        y_true: 真实标签
        y_pred: 预测标签
        task_type: 任务类型
        metric: 评估指标
        y_prob: 预测概率（某些指标需要）

    返回:
        指标值（分类任务越高越好，回归任务越低越好）
    """
    # 确保是 numpy 数组
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    try:
        if task_type == 'regression':
            if metric == 'rmse':
                return float(np.sqrt(mean_squared_error(y_true, y_pred)))
            elif metric == 'mae':
                return float(mean_absolute_error(y_true, y_pred))
            elif metric == 'r2':
                return float(r2_score(y_true, y_pred))
            elif metric == 'mape':
                # 避免除零
                mask = y_true != 0
                if mask.sum() == 0:
                    return float('inf')
                return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
            else:
                return float(mean_squared_error(y_true, y_pred))  # 默认 MSE

        else:  # classification or multiclass
            # 确保是整数标签
            y_true = y_true.astype(int)
            y_pred = y_pred.astype(int)

            if metric == 'accuracy':
                return float(accuracy_score(y_true, y_pred))
            elif metric == 'precision':
                return float(precision_score(y_true, y_pred, average='binary' if len(np.unique(y_true)) == 2 else 'macro', zero_division=0))
            elif metric == 'recall':
                return float(recall_score(y_true, y_pred, average='binary' if len(np.unique(y_true)) == 2 else 'macro', zero_division=0))
            elif metric == 'f1':
                return float(f1_score(y_true, y_pred, average='binary' if len(np.unique(y_true)) == 2 else 'macro', zero_division=0))
            elif metric == 'f1_macro':
                return float(f1_score(y_true, y_pred, average='macro', zero_division=0))
            elif metric == 'f1_weighted':
                return float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
            elif metric == 'f1_micro':
                return float(f1_score(y_true, y_pred, average='micro', zero_division=0))
            elif metric == 'roc_auc':
                # 二分类
                if len(np.unique(y_true)) == 2:
                    if y_prob is not None and len(y_prob.shape) > 1:
                        y_prob = y_prob[:, 1]  # 取正类概率
                    elif y_prob is None:
                        # 没有概率，用预测标签计算（不准确）
                        return float(accuracy_score(y_true, y_pred))
                    return float(roc_auc_score(y_true, y_prob))
                else:
                    # 多分类不支持 ROC AUC，用 macro F1
                    return float(f1_score(y_true, y_pred, average='macro', zero_division=0))
            else:
                return float(accuracy_score(y_true, y_pred))  # 默认 accuracy

    except Exception as e:
        print(f"评估指标计算错误: {e}")
        return 0.0 if task_type != 'regression' else float('inf')


def get_memory_usage():
    """获取当前内存占用（MB）"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


def check_data():
    """检查数据文件（用于初始化验证）"""
    config = get_task_config()

    print("=" * 50)
    print("数据检查报告")
    print("=" * 50)

    try:
        validate_config(config)
        print(f"✓ 配置文件有效")

        X, y = load_raw_data(config)
        print(f"✓ 数据加载成功")
        print(f"  - 样本数: {len(X)}")
        print(f"  - 特征数: {X.shape[1]}")
        print(f"  - 目标分布:")

        if config['task_type'] == 'regression':
            print(f"    均值: {y.mean():.3f}, 标准差: {y.std():.3f}")
        else:
            dist = y.value_counts().head(10)
            for idx, count in dist.items():
                pct = count / len(y) * 100
                print(f"    {idx}: {count} ({pct:.1f}%)")

        # 检查缺失值
        missing = X.isnull().sum().sum()
        if missing > 0:
            print(f"⚠ 缺失值: {missing} 个")
        else:
            print(f"✓ 无缺失值")

        return True

    except Exception as e:
        print(f"✗ 数据检查失败: {e}")
        return False


if __name__ == '__main__':
    # 命令行检查数据
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-data', action='store_true', help='检查数据文件')
    args = parser.parse_args()

    if args.check_data:
        check_data()
    else:
        # 测试加载
        X_train, X_val, y_train, y_val = load_data()
        print(f"\n数据加载成功!")
        print(f"训练集: X={X_train.shape}, y={y_train.shape}")
        print(f"验证集: X={X_val.shape}, y={y_val.shape}")
