#!/usr/bin/env python3
"""
AutoML Research - Training Script
这是 AI 代理修改的文件，包含模型定义、训练循环和超参数

你可以修改：
- MODEL_NAME: 选择模型
- MODEL_PARAMS: 超参数
- FEATURE_ENGINEERING: 是否启用特征工程
- 添加自定义特征工程函数
- 修改训练逻辑

不要修改：
- 导入语句（除非使用已有库）
- 评估指标计算
- 输出格式
"""

import os
import sys
import time
import pickle
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

# 导入 prepare 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare import load_data, evaluate_model, get_task_config, get_memory_usage

# ============================================================
# ========== 可修改部分开始 - 配置你的实验 ==========
# ============================================================

# 模型选择
# 可用选项: 'rf', 'xgb', 'lgb', 'catboost', 'gbdt', 'extra', 'histgb'
MODEL_NAME = 'lgb'

# 模型超参数 - 这是你最主要修改的地方
# 根据模型不同，可用的参数也不同
MODEL_PARAMS = {
    # LightGBM 参数
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': -1,  # -1 表示无限制
    'num_leaves': 31,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.0,
    'reg_lambda': 0.0,
    'min_child_samples': 20,

    # 通用参数
    'random_state': 42,
    'n_jobs': -1,
    'verbose': -1,
}

# 是否启用特征工程
FEATURE_ENGINEERING = False

# 是否启用交叉验证（比单次划分更稳定）
USE_CROSS_VALIDATION = True
CV_FOLDS = 5

# ============================================================
# ========== 可修改部分结束 ==========
# ============================================================


def create_model(model_name, params, task_type):
    """
    创建模型实例

    参数:
        model_name: 模型名称
        params: 超参数字典
        task_type: 任务类型 (classification, regression, multiclass)

    返回:
        模型实例
    """
    is_classification = task_type in ['classification', 'multiclass']

    if model_name == 'rf':
        # Random Forest
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

        # 过滤 RandomForest 支持的参数
        rf_params = {k: v for k, v in params.items() if k in [
            'n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf',
            'max_features', 'random_state', 'n_jobs'
        ]}

        if is_classification:
            return RandomForestClassifier(**rf_params)
        else:
            return RandomForestRegressor(**rf_params)

    elif model_name == 'xgb':
        # XGBoost
        try:
            import xgboost as xgb
        except ImportError:
            raise ImportError("XGBoost 未安装，请运行: pip install xgboost")

        # 过滤 XGBoost 支持的参数
        xgb_params = {k: v for k, v in params.items() if k in [
            'n_estimators', 'learning_rate', 'max_depth', 'min_child_weight',
            'subsample', 'colsample_bytree', 'colsample_bylevel',
            'reg_alpha', 'reg_lambda', 'gamma',
            'random_state', 'n_jobs', 'verbosity'
        ]}

        if 'verbosity' not in xgb_params:
            xgb_params['verbosity'] = 0

        if is_classification:
            return xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', **xgb_params)
        else:
            return xgb.XGBRegressor(**xgb_params)

    elif model_name == 'lgb':
        # LightGBM
        try:
            import lightgbm as lgb
        except ImportError:
            raise ImportError("LightGBM 未安装，请运行: pip install lightgbm")

        # 过滤 LightGBM 支持的参数
        lgb_params = {k: v for k, v in params.items() if k in [
            'n_estimators', 'learning_rate', 'max_depth', 'num_leaves',
            'subsample', 'colsample_bytree',
            'reg_alpha', 'reg_lambda',
            'min_child_samples', 'min_child_weight',
            'random_state', 'n_jobs', 'verbose'
        ]}

        if 'verbose' not in lgb_params:
            lgb_params['verbose'] = -1

        if is_classification:
            return lgb.LGBMClassifier(**lgb_params)
        else:
            return lgb.LGBMRegressor(**lgb_params)

    elif model_name == 'catboost':
        # CatBoost
        try:
            import catboost as cb
        except ImportError:
            raise ImportError("CatBoost 未安装，请运行: pip install catboost")

        # 过滤 CatBoost 支持的参数
        cat_params = {k: v for k, v in params.items() if k in [
            'iterations', 'learning_rate', 'depth',
            'l2_leaf_reg', 'random_seed',
            'verbose'
        ]}

        # 参数名映射
        if 'n_estimators' in params and 'iterations' not in cat_params:
            cat_params['iterations'] = params['n_estimators']
        if 'random_state' in params and 'random_seed' not in cat_params:
            cat_params['random_seed'] = params['random_state']
        if 'verbose' not in cat_params:
            cat_params['verbose'] = False

        if is_classification:
            return cb.CatBoostClassifier(loss_function='Logloss', **cat_params)
        else:
            return cb.CatBoostRegressor(**cat_params)

    elif model_name == 'gbdt':
        # Gradient Boosting (sklearn)
        from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

        gb_params = {k: v for k, v in params.items() if k in [
            'n_estimators', 'learning_rate', 'max_depth',
            'min_samples_split', 'min_samples_leaf',
            'subsample', 'random_state'
        ]}

        if is_classification:
            return GradientBoostingClassifier(**gb_params)
        else:
            return GradientBoostingRegressor(**gb_params)

    elif model_name == 'extra':
        # Extra Trees
        from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor

        et_params = {k: v for k, v in params.items() if k in [
            'n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf',
            'max_features', 'random_state', 'n_jobs'
        ]}

        if is_classification:
            return ExtraTreesClassifier(**et_params)
        else:
            return ExtraTreesRegressor(**et_params)

    elif model_name == 'histgb':
        # Histogram Gradient Boosting (sklearn)
        from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

        hgb_params = {k: v for k, v in params.items() if k in [
            'max_iter', 'learning_rate', 'max_depth',
            'min_samples_leaf', 'l2_regularization',
            'random_state'
        ]}

        # 参数名映射
        if 'n_estimators' in params and 'max_iter' not in hgb_params:
            hgb_params['max_iter'] = params['n_estimators']
        if 'reg_lambda' in params and 'l2_regularization' not in hgb_params:
            hgb_params['l2_regularization'] = params['reg_lambda']

        if is_classification:
            return HistGradientBoostingClassifier(**hgb_params)
        else:
            return HistGradientBoostingRegressor(**hgb_params)

    else:
        raise ValueError(f"不支持的模型: {model_name}")


def engineer_features(X_train, X_val=None):
    """
    特征工程函数

    你可以在这里添加自定义特征工程：
    - 特征交互
    - 多项式特征
    - 对数/平方根变换
    - 分箱
    - 等等

    参数:
        X_train: 训练集特征
        X_val: 验证集特征（可选）

    返回:
        变换后的特征
    """
    # 复制数据
    X_train = X_train.copy()
    if X_val is not None:
        X_val = X_val.copy()

    # ===== 在这里添加你的特征工程 =====

    # 示例 1: 特征交互
    # X_train['feat1_x_feat2'] = X_train['feature1'] * X_train['feature2']
    # if X_val is not None:
    #     X_val['feat1_x_feat2'] = X_val['feature1'] * X_val['feature2']

    # 示例 2: 对数变换
    # numeric_cols = X_train.select_dtypes(include=[np.number]).columns
    # for col in numeric_cols:
    #     X_train[f'{col}_log'] = np.log1p(np.abs(X_train[col]))
    #     if X_val is not None:
    #         X_val[f'{col}_log'] = np.log1p(np.abs(X_val[col]))

    # 示例 3: 分箱
    # X_train['feat1_bin'] = pd.qcut(X_train['feature1'], q=5, labels=False, duplicates='drop')
    # if X_val is not None:
    #     X_val['feat1_bin'] = pd.qcut(X_val['feature1'], q=5, labels=False, duplicates='drop')

    # ==================================

    if X_val is not None:
        return X_train, X_val
    return X_train


def train_with_cv(X, y, model_name, model_params, task_type, metric, cv_folds=5, random_state=42):
    """
    使用交叉验证训练模型

    返回平均指标和训练好的模型
    """
    from sklearn.model_selection import StratifiedKFold, KFold

    # 选择 CV 策略
    if task_type in ['classification', 'multiclass']:
        kf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    else:
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    scores = []
    models = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
        X_train_fold = X.iloc[train_idx] if hasattr(X, 'iloc') else X[train_idx]
        X_val_fold = X.iloc[val_idx] if hasattr(X, 'iloc') else X[val_idx]
        y_train_fold = y[train_idx]
        y_val_fold = y[val_idx]

        # 创建模型
        model = create_model(model_name, model_params, task_type)

        # 训练
        model.fit(X_train_fold, y_train_fold)

        # 预测
        y_pred = model.predict(X_val_fold)
        y_prob = model.predict_proba(X_val_fold) if hasattr(model, 'predict_proba') else None

        # 评估
        score = evaluate_model(y_val_fold, y_pred, task_type, metric, y_prob)
        scores.append(score)
        models.append(model)

    # 返回平均分数和最后一个模型
    return np.mean(scores), models[-1]


def main():
    """主函数"""
    # 加载配置
    config = get_task_config()
    task_type = config['task_type']
    metric = config['metric']
    time_budget = config['time_budget']

    # 记录开始时间
    start_time = time.time()

    try:
        # 加载数据
        X_train, X_val, y_train, y_val = load_data(config)

        # 特征工程
        if FEATURE_ENGINEERING:
            X_train, X_val = engineer_features(X_train, X_val)

        # 创建模型
        model = create_model(MODEL_NAME, MODEL_PARAMS, task_type)

        # 训练
        train_start = time.time()

        if USE_CROSS_VALIDATION:
            # 使用交叉验证
            cv_score, model = train_with_cv(
                X_train, y_train, MODEL_NAME, MODEL_PARAMS,
                task_type, metric, CV_FOLDS, config['random_seed']
            )
            train_time = time.time() - train_start

            # 在全量训练集上重新训练（用于最终评估）
            model.fit(X_train, y_train)
        else:
            # 单次训练
            model.fit(X_train, y_train)
            train_time = time.time() - train_start

        # 预测
        train_pred = model.predict(X_train)
        val_pred = model.predict(X_val)

        train_prob = model.predict_proba(X_train) if hasattr(model, 'predict_proba') else None
        val_prob = model.predict_proba(X_val) if hasattr(model, 'predict_proba') else None

        # 评估
        train_metric = evaluate_model(y_train, train_pred, task_type, metric, train_prob)
        val_metric = evaluate_model(y_val, val_pred, task_type, metric, val_prob)

        # 计算总时间
        total_time = time.time() - start_time
        memory_mb = get_memory_usage()

        # 输出结果（固定格式，不要改）
        print(f"train_{metric}: {train_metric:.6f}")
        print(f"val_{metric}: {val_metric:.6f}")
        if USE_CROSS_VALIDATION:
            print(f"cv_{metric}: {cv_score:.6f}")
        print(f"train_time: {train_time:.1f}")
        print(f"total_time: {total_time:.1f}")
        print(f"memory_mb: {memory_mb:.1f}")
        print(f"status: success")

        # 保存模型
        with open('model.pkl', 'wb') as f:
            pickle.dump(model, f)

        # 保存特征重要性（如果模型支持）
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = list(X_train.columns) if hasattr(X_train, 'columns') else [f'feat_{i}' for i in range(len(importances))]
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            importance_df.to_csv('feature_importance.csv', index=False)

    except Exception as e:
        # 错误输出
        print(f"status: crash")
        print(f"error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
