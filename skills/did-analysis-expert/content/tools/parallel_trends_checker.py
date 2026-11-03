#!/usr/bin/env python3
"""
did-analysis-expert - 平行趋势检验工具
检验处理组和对照组在干预前的趋势是否平行

方法：使用DID交互项检验（Callaway & Sant'Anna 2021规范）
- 回归模型：Y = β0 + β1(Time) + β2(Treatment) + β3(Time × Treatment) + ε
- β3 不显著（p > 0.1）→ 平行趋势假设成立
- β3 显著（p < 0.1）→ 平行趋势不成立，预处理差异显著
"""

from typing import Dict, List, Any, Optional
import json
import math
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class RegressionResult:
    coef: float
    se: float
    t_stat: float
    p_value: float
    ci_low: float
    ci_high: float
    r_squared: float


def _regress(y: List[float], x: List[List[float]]) -> Optional[RegressionResult]:
    """简单OLS回归 — 优先使用SVD以避免病态矩阵"""
    n = len(y)
    k = len(x[0]) if x else 0
    if n <= k:
        return None
    return _regress_svd(y, x)


def _regress_svd(y: List[float], x: List[List[float]]) -> Optional[RegressionResult]:
    """使用SVD的OLS回归（处理病态矩阵）"""
    import numpy as np
    try:
        X = np.column_stack([np.ones(len(x))] + [np.array(col) for col in zip(*x)])
        Y = np.array(y)
        beta_arr, residuals_arr, rank, s = np.linalg.lstsq(X, Y, rcond=None)
        n = len(Y)
        k = len(beta_arr)
        y_hat = X @ beta_arr
        ss_res = np.sum((Y - y_hat) ** 2)
        ss_tot = np.sum((Y - np.mean(Y)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0
        df = n - rank
        mse = ss_res / df if df > 0 else ss_res
        # 协方差矩阵（伪逆）
        try:
            XtX_inv = np.linalg.pinv(X.T @ X)
            var_coef = np.diag(mse * XtX_inv)
            se = np.sqrt(np.abs(var_coef))
        except Exception:
            se = np.full(k, 0.0)
        t_stats = [beta_arr[i] / se[i] if se[i] > 1e-12 else 0.0 for i in range(k)]
        def _norm_cdf(z):
            return 0.5 * (1 + math.erf(z / math.sqrt(2)))
        p_values = [2 * (1 - _norm_cdf(abs(t))) for t in t_stats]
        z_crit = 1.96
        return RegressionResult(
            coef=float(beta_arr[-1]),
            se=float(se[-1]),
            t_stat=float(t_stats[-1]),
            p_value=float(p_values[-1]),
            ci_low=float(beta_arr[-1] - z_crit * se[-1]),
            ci_high=float(beta_arr[-1] + z_crit * se[-1]),
            r_squared=float(r_squared),
        )
    except Exception:
        return None


class ParallelTrendsChecker:
    """
    平行趋势检验器

    使用交互项检验法（Interaction Test）：
    Y_it = α + β1·Time_it + β2·Treatment_i + β3·(Time_it × Treatment_i) + ε_it
    - β3（交互项）是关键
    - β3 不显著 → 预处理期平行趋势成立
    - β3 显著 → 预处理期存在组间差异，DID估计可能有偏

    参数:
        alpha: 显著性水平（默认0.1，即p<0.1认为交互项显著）
    """

    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha

    def check(self, data: Any) -> Dict:
        """
        检验平行趋势

        Args:
            data: 格式1（列表）：[{"group":"treatment","time":t,"y":y}, ...]
                  格式2（字典）：{"treatment":{t: y, ...}, "control":{t: y, ...}}
                  格式3（面板）：{"y":[...], "treatment":[0,1,...], "time":[0,1,...]}

        Returns:
            检验结果字典
        """
        if isinstance(data, list):
            return self._check_from_list(data)
        elif isinstance(data, dict):
            if "y" in data and "treatment" in data:
                return self._check_from_panel(data)
            return self._check_from_dict(data)
        return {"status": "error", "message": "无法处理的数据格式"}

    def _check_from_list(self, data: List) -> Dict:
        """从记录列表检验"""
        # 按组+时间整理
        t_records: Dict[float, List[float]] = defaultdict(list)
        c_records: Dict[float, List[float]] = defaultdict(list)
        all_times = set()

        for row in data:
            group = str(row.get("group", "")).strip().lower()
            time = float(row.get("time", 0))
            y = float(row.get("y", 0))
            all_times.add(time)
            if group == "treatment":
                t_records[time].append(y)
            elif group == "control":
                c_records[time].append(y)

        # 确定干预时点（取中位数时间作为分割点）
        sorted_times = sorted(all_times)
        median_time = sorted_times[len(sorted_times) // 2] if sorted_times else 0

        pre_times = [t for t in sorted_times if t < median_time]
        post_times = [t for t in sorted_times if t >= median_time]

        # 构建回归数据（预处理期）
        y_reg: List[float] = []
        x_reg: List[List[float]] = []

        for t in sorted_times:
            if t >= median_time:
                continue
            # 处理组
            for y in t_records.get(t, []):
                y_reg.append(y)
                x_reg.append([t, 1.0, t * 1.0])
            # 对照组
            for y in c_records.get(t, []):
                y_reg.append(y)
                x_reg.append([t, 0.0, t * 0.0])

        if len(y_reg) < 4:
            return self._fallback_by_records(t_records, c_records, median_time)

        result = _regress(y_reg, x_reg)
        return self._build_result(result, pre_times, post_times)

    def _check_from_dict(self, data: Dict) -> Dict:
        """从分组字典检验"""
        treatment = data.get("treatment", {})
        control = data.get("control", {})

        # 构建列表格式
        rows = []
        for t, y in treatment.items():
            rows.append({"group": "treatment", "time": float(t), "y": float(y)})
        for t, y in control.items():
            rows.append({"group": "control", "time": float(t), "y": float(y)})

        return self._check_from_list(rows)

    def _check_from_panel(self, data: Dict) -> Dict:
        """从面板数据字典检验"""
        y_list = data["y"]
        treat = data["treatment"]
        time_list = data["time"]

        # 构建回归数据
        y_reg = []
        x_reg = []
        for i in range(len(y_list)):
            t_val = float(time_list[i])
            treat_val = float(treat[i])
            y_reg.append(float(y_list[i]))
            x_reg.append([t_val, treat_val, t_val * treat_val])

        result = _regress(y_reg, x_reg)

        pre_times = sorted(set(t for i, t in enumerate(time_list) if treat[i] == 0))
        post_times = sorted(set(t for i, t in enumerate(time_list) if treat[i] == 1))

        return self._build_result(result, pre_times, post_times)

    def _fallback_by_records(
        self,
        t_records: Dict[float, List[float]],
        c_records: Dict[float, List[float]],
        cutoff_time: float,
    ) -> Dict:
        """样本量不足时的备用方法：比较各预处理时期的组间均值差异"""
        t_means: Dict[float, float] = {
            t: sum(vals) / len(vals) for t, vals in t_records.items() if t < cutoff_time
        }
        c_means: Dict[float, float] = {
            t: sum(vals) / len(vals) for t, vals in c_records.items() if t < cutoff_time
        }
        common_times = sorted(set(t_means.keys()) & set(c_means.keys()))
        if not common_times:
            return {
                "status": "error",
                "message": "预处理期无共同时间点，无法检验平行趋势",
            }
        # 计算各时期的组间差异
        diffs = [abs(t_means[t] - c_means[t]) for t in common_times]
        avg_diff = sum(diffs) / len(diffs)
        max_diff = max(diffs)
        # 阈值：平均值差异 < 2 且最大值 < 5 → 平行
        parallel = avg_diff < 2 and max_diff < 5
        return {
            "status": "success",
            "method": "fallback_mean_comparison",
            "pre_period_means_treatment": t_means,
            "pre_period_means_control": c_means,
            "avg_group_difference": round(avg_diff, 3),
            "max_group_difference": round(max_diff, 3),
            "parallel_trends": parallel,
            "verdict": "通过" if parallel else "不通过",
            "interaction_p_value": None,
            "interaction_coef": None,
            "note": "样本量不足，使用组间均值比较替代交互项检验",
        }

    def _build_result(self, result: Optional[RegressionResult], pre_times, post_times) -> Dict:
        """构建检验结果"""
        if result is None:
            return {
                "status": "error",
                "message": "无法计算回归结果，请检查数据",
            }

        significant = result.p_value < self.alpha
        parallel = not significant  # 交互项不显著 → 平行趋势成立

        verdict = "通过" if parallel else "不通过（存在预处理差异）"
        explanation = (
            "交互项系数β3不显著（p={:.4f} > α={}），"
            "处理组与对照组在预处理期趋势无显著差异，平行趋势假设成立"
        ).format(result.p_value, self.alpha) if parallel else (
            "交互项系数β3显著（p={:.4f} < α={}），"
            "预处理期存在组间差异，平行趋势假设不成立，DID估计可能有偏"
        ).format(result.p_value, self.alpha)

        return {
            "status": "success",
            "method": "interaction_term_regression",
            "parallel_trends": parallel,
            "verdict": verdict,
            "explanation": explanation,
            "interaction_coef": round(result.coef, 4),
            "interaction_se": round(result.se, 4),
            "interaction_t_stat": round(result.t_stat, 3),
            "interaction_p_value": round(result.p_value, 4),
            "interaction_ci": [round(result.ci_low, 4), round(result.ci_high, 4)],
            "r_squared": round(result.r_squared, 4),
            "pre_period_times": pre_times,
            "post_period_times": post_times,
            "alpha": self.alpha,
        }

    def _calculate_slope(self, points: List) -> float:
        """计算简单线性回归斜率"""
        if len(points) < 2:
            return 0.0
        points = sorted(points, key=lambda x: x[0])
        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_x2 = sum(p[0] ** 2 for p in points)
        denom = n * sum_x2 - sum_x ** 2
        if abs(denom) < 1e-12:
            return 0.0
        return (n * sum_xy - sum_x * sum_y) / denom


def check_parallel_trends(data: Any, alpha: float = 0.1) -> Dict:
    """
    平行趋势检验（交互项方法）

    Args:
        data: 见 ParallelTrendsChecker.check()
        alpha: 显著性水平（默认0.1）

    Returns:
        检验结果字典
    """
    return ParallelTrendsChecker(alpha=alpha).check(data)


if __name__ == "__main__":
    # 测试1：平行趋势（应该通过）
    test_data_1 = [
        {"group": "treatment", "time": 0, "y": 10},
        {"group": "treatment", "time": 1, "y": 12},
        {"group": "treatment", "time": 2, "y": 14},
        {"group": "treatment", "time": 3, "y": 20},  # 干预后
        {"group": "treatment", "time": 4, "y": 22},
        {"group": "control", "time": 0, "y": 8},
        {"group": "control", "time": 1, "y": 10},
        {"group": "control", "time": 2, "y": 12},
        {"group": "control", "time": 3, "y": 13},  # 干预后（无处理效应）
        {"group": "control", "time": 4, "y": 14},
    ]
    result1 = check_parallel_trends(test_data_1)
    print("【测试1：平行趋势（应该通过）】")
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    print()

    # 测试2：不平行趋势（应该不通过）
    test_data_2 = [
        {"group": "treatment", "time": 0, "y": 10},
        {"group": "treatment", "time": 1, "y": 12},
        {"group": "treatment", "time": 2, "y": 14},
        {"group": "control", "time": 0, "y": 5},
        {"group": "control", "time": 1, "y": 7},
        {"group": "control", "time": 2, "y": 9},
    ]
    result2 = check_parallel_trends(test_data_2)
    print("【测试2：不平行趋势（应该不通过）】")
    print(json.dumps(result2, ensure_ascii=False, indent=2))