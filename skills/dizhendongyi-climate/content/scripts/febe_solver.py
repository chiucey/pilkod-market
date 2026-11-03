#!/usr/bin/env python3
"""
febe_solver.py
==============
分数阶能量平衡方程（FEBE）求解器。

方程:  { }_0^C D_t^h ΔT(t) = -ΔT(t)/τ₀ + F(t)/C
解:   ΔT(t) = (τ₀^h/C) * [1 - E_{h,1}(-(t/τ₀)^h)] * F_orb

其中 E_{h,1} 是单参数 Mittag-Leffler 函数。

用法:
  python3 febe_solver.py <h> <tau_yr> <C> <F_Wm2> <t_end_yr>

参数:
  h       : 记忆指数 (0 < h <= 1)，典型值 0.4–0.9
  tau_yr  : 特征弛豫时间（年），典型值 1e3–1e5
  C       : 热容量（J/m²/K），默认 8.4e8
  F_Wm2   : 辐射强迫（W/m²），默认 30.0
  t_end_yr: 模拟终止时间（年），默认 1e5
"""

import numpy as np
import json, sys, math

# ── Mittag-Leffler 函数 E_{α,β}(z) ──────────────────────────────
def mittag_leffler(alpha, beta, z, n_terms=200):
    """
    计算双参数 Mittag-Leffler 函数 E_{α,β}(z)。

    E_{α,β}(z) = Σ_{k=0}^{∞}  z^k / Γ(αk + β)

    参数:
        alpha, beta: Mittag-Leffler 参数
        z:          自变量（数组或标量）
        n_terms:   级数求和项数（默认200，对 |z|<50 足够）
    返回:
        E_{α,β}(z) 的值
    """
    z = np.asarray(z, dtype=np.float64)
    result = np.zeros_like(z)

    for k in range(n_terms):
        gamma_arg = alpha * k + beta
        if gamma_arg > 200:   # 防止 gamma 函数溢出
            break
        term = np.power(z, k) / gamma_arg
        result += term
        if np.all(np.abs(term) < 1e-15 * np.abs(result)):
            break

    return result if result.shape else float(result)


def E_h_1(alpha, z, n_terms=200):
    """单参数 Mittag-Leffler E_{α,1}(z)"""
    return mittag_leffler(alpha, 1.0, z, n_terms)


# ── FEBE 方程求解 ───────────────────────────────────────────────
def febe_solution(h, tau0, C, F_orb, t_yr):
    """
    计算 FEBE 方程的解析解（零初始条件，单位强迫脉冲 → 稳态强迫）。

    ΔT(t) = (τ₀^h / C) * [1 - E_{h,1}(-(t/τ₀)^h)] * F_orb

    参数:
        h     : 记忆指数 (0 < h <= 1)
        tau0  : 特征弛豫时间（年）
        C     : 等效热容量（J/m²/K）
        F_orb : 辐射强迫（W/m²），可以是数组（须与 t_yr 同长）
        t_yr  : 时间点数组（年）

    返回:
        ΔT(t) 温度异常（K），与 t_yr 同形状
    """
    if np.isscalar(F_orb):
        F_arr = np.full_like(t_yr, F_orb)
    else:
        F_arr = np.asarray(F_orb)

    # 归一化时间
    tau0_arr = np.asarray(tau0)
    if np.isscalar(tau0):
        tau0_arr = np.full_like(t_yr, tau0)

    z = -np.power(t_yr / tau0_arr, h)
    ml_term = E_h_1(h, z)    # E_{h,1}(-(t/τ₀)^h)

    # 零初始条件解
    delta_T = np.power(tau0_arr, h) / C * (1.0 - ml_term) * F_arr

    return delta_T


def febe_transient(h, tau0, C, F_func, t_yr, dt=100):
    """
    计算时变强迫的近似解（分段常值近似 + 卷积核）。

    适用于强迫随时间变化的情况（非恒定 F_orb）。
    用 Mittag-Leffler 核做数值卷积。

    参数:
        h      : 记忆指数
        tau0   : 特征时间
        C      : 热容量
        F_func : callable，接受时间数组返回强迫数组
        t_yr   : 时间点
        dt     : 分段步长（年），默认100年

    返回:
        ΔT(t) 近似解
    """
    F_vals = F_func(t_yr)
    result = np.zeros_like(t_yr, dtype=np.float64)

    for i, ti in enumerate(t_yr):
        if ti == 0:
            result[i] = 0.0
            continue
        # 卷积核: t^h / Γ(1+h) * (t - s)^{-h}
        s_arr = t_yr[t_yr < ti]
        F_s   = F_vals[t_yr < ti]
        if len(s_arr) == 0:
            continue
        # 核: (ti-s)^h / Γ(1+h)
        kernel = np.power(ti - s_arr, h) / math.gamma(1 + h)
        # 步长
        dt_arr = np.diff(s_arr, axis=0) if len(s_arr) > 1 else np.array([dt])
        if len(dt_arr) == 0:
            dt_arr = np.array([dt])
        # 梯形近似
        result[i] = np.sum(kernel * F_s * dt_arr) / C

    return result


def sensitivity_factor(h, tau0, F_orb, t_target):
    """
    计算目标时间的平衡气候敏感度因子。

    返回：单位强迫下的温度响应（K / (W/m²)）
    """
    delta_T = febe_solution(h, tau0, 8.4e8, F_orb, np.array([t_target]))
    return float(delta_T[0] / F_orb) if F_orb != 0 else 0.0


# ── 组件叠加 ────────────────────────────────────────────────────
COMPONENT_PARAMS = {
    'atmosphere': {'h': 0.40, 'tau': 3e2,  'C': 1e8},
    'thermocline':{'h': 0.60, 'tau': 1e4,  'C': 5e8},
    'deep_ocean': {'h': 0.75, 'tau': 5e4,  'C': 1e9},
    'ice_sheet':  {'h': 0.85, 'tau': 1e5,  'C': 5e9},
}

def multi_layer_response(F_orb, t_yr):
    """
    计算多圈层耦合的温度响应（各组件加权叠加）。

    返回:
        dict: {component_name: ΔT} 和总响应
    """
    weights = [0.15, 0.20, 0.35, 0.30]  # 大气/温跃/深海/冰盖
    names   = list(COMPONENT_PARAMS.keys())
    results = {}

    for name, w in zip(names, weights):
        p   = COMPONENT_PARAMS[name]
        dT  = febe_solution(p['h'], p['tau'], p['C'], F_orb, t_yr)
        results[name] = (dT * w).tolist()

    total = sum(results[n] for n in names)
    results['total'] = total.tolist() if hasattr(total, 'tolist') else total
    return results


# ── 反馈放大 ────────────────────────────────────────────────────
def apply_feedbacks(delta_T_base, h, lambda_sys=2.5):
    """
    将四大反馈机制的放大效应应用于基础温度响应。

    λ_sys: 系统敏感度（默认2.5，即基础辐射强迫放大约2.5倍）
    """
    return delta_T_base * lambda_sys


# ── 主程序 ──────────────────────────────────────────────────────
if __name__ == '__main__':
    h, tau, C, F0, t_end = 0.6, 3e4, 8.4e8, 30.0, 1e5
    if len(sys.argv) >= 2: h     = float(sys.argv[1])
    if len(sys.argv) >= 3: tau    = float(sys.argv[2])
    if len(sys.argv) >= 4: C      = float(sys.argv[3])
    if len(sys.argv) >= 5: F0     = float(sys.argv[4])
    if len(sys.argv) >= 6: t_end  = float(sys.argv[5])

    t_yr  = np.linspace(0, t_end, 1001)
    dT    = febe_solution(h, tau, C, F0, t_yr)
    dT_amp = apply_feedbacks(dT, h)

    # 找关键时间点
    key_times = [1000, 5000, 10000, 23000, 41000, 100000]
    key_idx   = [np.argmin(np.abs(t_yr - tt)) for tt in key_times]

    print("="*62)
    print("地动仪模型 · FEBE方程求解结果")
    print("="*62)
    print(f"参数: h={h}, τ₀={tau:.0e} yr, C={C:.0e} J/m²/K, F={F0} W/m²")
    print(f"反馈放大倍数 λ_sys = 2.5（四大反馈综合）")
    print()
    print(f"{'时间(yr)':>12} | {'ΔT基础(K)':>12} | {'ΔT放大(K)':>12} | {'说明'}")
    print("-"*62)
    labels = {1000:'千年', 5000:'5千年', 10000:'1万年', 23000:'2.3万年', 41000:'4.1万年', 100000:'10万年'}
    for tt, idx in zip(key_times, key_idx):
        lbl = labels.get(tt, '')
        print(f"{tt:>12,.0f} | {dT[idx]:>12.3f} | {dT_amp[idx]:>12.3f} | {lbl}")

    # 平衡敏感度（100kyr）
    ECS = sensitivity_factor(h, tau, F0, 100000)
    print(f"\n平衡气候敏感度（@100kyr）: {ECS*F0:.2f} K  (基础)")
    print(f"含反馈平衡敏感度          : {ECS*F0*2.5:.2f} K")

    out = {
        't_yr': t_yr.tolist(), 'dT_base': dT.tolist(), 'dT_amped': dT_amp.tolist(),
        'params': {'h': h, 'tau_yr': tau, 'C': C, 'F_Wm2': F0, 'lambda_sys': 2.5},
        'key_points': {str(tt): float(dT[idx]) for tt, idx in zip(key_times, key_idx)},
        'ECS_amped': float(ECS*F0*2.5)
    }
    with open('/tmp/febe_results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\n数据已存: /tmp/febe_results.json")
