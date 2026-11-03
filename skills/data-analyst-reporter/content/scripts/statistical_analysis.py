#!/usr/bin/env python3
"""
统计分析脚本 — A/B测试结果分析、趋势检验、异常检测

用法:
    python statistical_analysis.py --mode ab_test --control ctrl.csv --treatment trt.csv
    python statistical_analysis.py --mode trend --input timeseries.csv --metric revenue
    python statistical_analysis.py --mode anomaly --input metrics.csv --metric daily_orders

依赖: pandas, numpy, scipy, statsmodels
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, Optional
import argparse
import json


# ============================================================
# A/B 测试分析
# ============================================================

def ab_test_proportions(
    control_conversions: int, control_n: int,
    treatment_conversions: int, treatment_n: int,
    alpha: float = 0.05
) -> Dict:
    """
    比较两组转化率的 A/B 测试（z检验）。

    Returns:
        包含 p值、置信区间、效应量、建议的字典
    """
    p_ctrl = control_conversions / control_n
    p_trt  = treatment_conversions / treatment_n
    lift   = (p_trt - p_ctrl) / p_ctrl * 100

    # z 检验
    count  = np.array([treatment_conversions, control_conversions])
    nobs   = np.array([treatment_n, control_n])

    try:
        from statsmodels.stats.proportion import proportions_ztest, proportion_confint
        z_stat, p_value = proportions_ztest(count, nobs)

        # 95% 置信区间（对差值）
        diff = p_trt - p_ctrl
        se   = np.sqrt(p_ctrl * (1 - p_ctrl) / control_n + p_trt * (1 - p_trt) / treatment_n)
        ci_lower = diff - 1.96 * se
        ci_upper = diff + 1.96 * se
    except ImportError:
        # Fallback: 手动计算
        p_pool = (control_conversions + treatment_conversions) / (control_n + treatment_n)
        se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/control_n + 1/treatment_n))
        z_stat  = (p_trt - p_ctrl) / se_pool
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        diff    = p_trt - p_ctrl
        se      = np.sqrt(p_ctrl*(1-p_ctrl)/control_n + p_trt*(1-p_trt)/treatment_n)
        ci_lower, ci_upper = diff - 1.96*se, diff + 1.96*se

    # 效应量 Cohen's h
    cohens_h = 2 * np.arcsin(np.sqrt(p_trt)) - 2 * np.arcsin(np.sqrt(p_ctrl))

    significant = p_value < alpha
    return {
        'control_rate':    round(p_ctrl * 100, 4),
        'treatment_rate':  round(p_trt * 100, 4),
        'absolute_lift':   round((p_trt - p_ctrl) * 100, 4),
        'relative_lift_pct': round(lift, 2),
        'z_statistic':     round(z_stat, 4),
        'p_value':         round(p_value, 6),
        'ci_95_lower':     round(ci_lower * 100, 4),
        'ci_95_upper':     round(ci_upper * 100, 4),
        'cohens_h':        round(abs(cohens_h), 4),
        'significant':     significant,
        'confidence_level': f"{(1-alpha)*100:.0f}%",
        'recommendation':  (
            f"✅ 实验组显著优于对照组 (p={p_value:.4f} < {alpha})，"
            f"转化率提升 {lift:.2f}%，建议推全。"
        ) if significant and p_trt > p_ctrl else (
            f"⏳ 差异不显著 (p={p_value:.4f})，"
            f"建议继续收集数据或重新审视实验设计。"
        ) if not significant else (
            f"❌ 实验组表现劣于对照组 (p={p_value:.4f})，建议停止实验。"
        )
    }


def ab_test_means(
    control_values: np.ndarray,
    treatment_values: np.ndarray,
    alpha: float = 0.05
) -> Dict:
    """
    比较两组均值的 A/B 测试（独立样本 t 检验）。
    """
    n_ctrl, n_trt = len(control_values), len(treatment_values)
    mean_ctrl, mean_trt = np.mean(control_values), np.mean(treatment_values)
    std_ctrl,  std_trt  = np.std(control_values, ddof=1), np.std(treatment_values, ddof=1)

    t_stat, p_value = stats.ttest_ind(treatment_values, control_values)

    # Cohen's d 效应量
    pooled_std = np.sqrt(((n_ctrl - 1) * std_ctrl**2 + (n_trt - 1) * std_trt**2)
                         / (n_ctrl + n_trt - 2))
    cohens_d   = (mean_trt - mean_ctrl) / pooled_std

    # 95% 置信区间（均值差）
    se_diff = np.sqrt(std_ctrl**2 / n_ctrl + std_trt**2 / n_trt)
    df_     = n_ctrl + n_trt - 2
    t_crit  = stats.t.ppf(1 - alpha/2, df_)
    diff    = mean_trt - mean_ctrl
    ci_lower, ci_upper = diff - t_crit * se_diff, diff + t_crit * se_diff

    effect_label = (
        '微小' if abs(cohens_d) < 0.2 else
        '小'   if abs(cohens_d) < 0.5 else
        '中等' if abs(cohens_d) < 0.8 else '大'
    )

    return {
        'control_mean':     round(mean_ctrl, 4),
        'treatment_mean':   round(mean_trt, 4),
        'mean_diff':        round(diff, 4),
        'relative_lift_pct': round(diff / abs(mean_ctrl) * 100, 2),
        't_statistic':      round(t_stat, 4),
        'p_value':          round(p_value, 6),
        'ci_95': f"[{ci_lower:.4f}, {ci_upper:.4f}]",
        'cohens_d':         round(cohens_d, 4),
        'effect_size_label': effect_label,
        'significant':      p_value < alpha,
        'n_control':        n_ctrl,
        'n_treatment':      n_trt,
    }


# ============================================================
# 趋势分析
# ============================================================

def trend_analysis(series: pd.Series, dates: pd.Series = None) -> Dict:
    """
    对时间序列进行趋势分析（线性回归 + 趋势方向）。

    Args:
        series: 指标值序列
        dates: 对应日期序列（可选，用于格式化输出）

    Returns:
        趋势分析结果字典
    """
    values = series.dropna().values
    n = len(values)
    x = np.arange(n)

    # 线性回归
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

    # 变化率（相对起点）
    pct_change = (values[-1] - values[0]) / abs(values[0]) * 100 if values[0] != 0 else 0

    # 波动率（变异系数）
    cv = np.std(values) / np.mean(values) * 100 if np.mean(values) != 0 else 0

    trend_direction = '上升' if slope > 0 else '下降' if slope < 0 else '平稳'
    trend_strength  = '强' if abs(r_value) > 0.7 else '中等' if abs(r_value) > 0.4 else '弱'

    return {
        'n_points':          n,
        'mean':              round(np.mean(values), 4),
        'std':               round(np.std(values), 4),
        'min':               round(np.min(values), 4),
        'max':               round(np.max(values), 4),
        'slope':             round(slope, 6),
        'r_squared':         round(r_value**2, 4),
        'p_value':           round(p_value, 6),
        'trend_direction':   trend_direction,
        'trend_strength':    trend_strength,
        'total_change_pct':  round(pct_change, 2),
        'coefficient_of_variation_pct': round(cv, 2),
        'significant_trend': p_value < 0.05,
        'summary': (
            f"{trend_direction}趋势（{trend_strength}），"
            f"期间变化 {pct_change:+.1f}%，"
            f"R²={r_value**2:.3f}，"
            f"{'统计显著' if p_value < 0.05 else '不显著'} (p={p_value:.4f})"
        )
    }


# ============================================================
# 异常检测
# ============================================================

def detect_anomalies(series: pd.Series,
                     method: str = 'iqr',
                     sigma: float = 3.0) -> pd.DataFrame:
    """
    检测时间序列中的异常点。

    Args:
        series: 数值序列（带日期 index 更佳）
        method: 'iqr' 或 'zscore'
        sigma:  z-score 方法中的 sigma 阈值

    Returns:
        标注了异常标志的 DataFrame
    """
    df = pd.DataFrame({'value': series})

    if method == 'iqr':
        Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        df['is_anomaly'] = (series < lower) | (series > upper)
        df['lower_bound'] = lower
        df['upper_bound'] = upper
    else:  # z-score
        z_scores = np.abs(stats.zscore(series.dropna()))
        df['z_score']    = np.nan
        df.loc[series.notna(), 'z_score'] = z_scores
        df['is_anomaly'] = df['z_score'] > sigma

    df['anomaly_type'] = 'normal'
    if 'lower_bound' in df.columns:
        df.loc[series < df['lower_bound'], 'anomaly_type'] = '偏低异常'
        df.loc[series > df['upper_bound'], 'anomaly_type'] = '偏高异常'

    return df


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='统计分析工具')
    parser.add_argument('--mode', choices=['ab_test', 'trend', 'anomaly'],
                        required=True, help='分析模式')
    parser.add_argument('--control',   help='对照组 CSV（ab_test模式）')
    parser.add_argument('--treatment', help='实验组 CSV（ab_test模式）')
    parser.add_argument('--input',     help='输入 CSV（trend/anomaly模式）')
    parser.add_argument('--metric',    default='value', help='要分析的指标列名')
    parser.add_argument('--alpha',     type=float, default=0.05, help='显著性水平')
    args = parser.parse_args()

    if args.mode == 'ab_test':
        ctrl = pd.read_csv(args.control)
        trt  = pd.read_csv(args.treatment)
        result = ab_test_means(ctrl[args.metric].values, trt[args.metric].values, args.alpha)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.mode == 'trend':
        df = pd.read_csv(args.input)
        result = trend_analysis(df[args.metric])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.mode == 'anomaly':
        df = pd.read_csv(args.input)
        result = detect_anomalies(df[args.metric])
        anomalies = result[result['is_anomaly']]
        print(f"检测到 {len(anomalies)} 个异常点：")
        print(anomalies.to_string())


if __name__ == '__main__':
    main()
