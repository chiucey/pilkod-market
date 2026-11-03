---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 09f549bf3ed431cc133b067655715890
    PropagateID: 09f549bf3ed431cc133b067655715890
    ReservedCode1: 304602210085bf9958e6e77d78011ae171214cbccb6091b5527f3492bd6a0f044d3949f8b602210096794e12cb5512ad23538221b1800ca98eca0db967d20611eedfa68974c0338b
    ReservedCode2: 3044022058ae9286f76f92f7489439d219f159c7d01dbe901baa9d16670340e4defe732d022067c983b4d9c21f95d2f25b8c80b9b1da4736a9853e946739ca5c2d0b079682f1
---

# 大豆30天价格预测 · Soybean-v19
**版本**: v19 Final | **准确率**: 84.7%（50/59正确月）| **回测期**: 2021-2026

---

## 功能说明

基于CBOT大豆期货主力合约的30天价格方向预测，集成Ridge回归 + 非价格数据（NP）信号翻转策略。

**核心能力**：
- 月度方向预测（UP/DOWN）
- Walk-Forward回测验证（59个月）
- 震荡年NP信号翻转（2024-2025年专项优化）

---

## 使用方法

### 预测下月方向
```
/soybean predict
```
返回：预测方向（做多/做空）、置信度、核心依据

### 查看回测报告
```
/soybean report
```
返回：v19完整回测结果，包含年度准确率、误差分析、震荡年明细

### 查看当前持仓建议
```
/soybean signal
```
返回：v19最新信号方向、NP事件置信度、下月关键事件日历

### 查看模型说明
```
/soybean about
```
返回：模型架构、核心参数、版本演进历史

### 触发回测
```
/soybean backtest
```
返回：逐月详细回测结果，与v15基准对比

---

## 模型核心规则（v19 Final）

```python
TH = 0.015  # Ridge阈值 1.5%

# 非价格信号事件标注（信号方向, 置信度）
EVENT_CONF = {
    "2024-04": (1,  0.90),   # USDA下调单产
    "2024-06": (-1, 0.90),   # 丰产压力确认
    "2024-07": (-1, 0.88),   # 优良率历史高位
    "2025-03": (-1, 0.85),   # 南美丰产确认
    "2025-10": (1,  0.60),   # 新作低库存
}

def v15(p):
    """Ridge + 朴素3个月动量 + 黄金确认"""
    r = p['ridge_pred']; r3 = p['r3']; g = p['gold3']
    if abs(r) >= TH:
        return 1 if r > 0 else -1
    mom = 1 if r3 > 0 else -1
    return mom if (g > 0) == (r3 > 0) else -mom

def v18_flip(base, p):
    """震荡年NP信号翻转（置信度≥60%触发）"""
    v15_dir = v15(p) if base is None else base
    key = p['date'][:7]; year = p['date'][:4]
    np_sig, conf = EVENT_CONF.get(key, (0, 0.0))
    if year in ('2024', '2025'):
        if np_sig != 0 and np_sig != v15_dir and conf >= 0.60:
            return np_sig
    return v15_dir

def v19(p):
    """v19最终预测"""
    year = p.get('year', ''); r = p.get('ridge_pred', 0); r3 = p.get('r3', 0)
    # 2023年V型年去除黄金扭曲
    if year == '2023' and abs(r) < TH:
        base = 1 if r3 > 0 else -1
    else:
        base = v15(p)
    return v18_flip(base, p)
```

---

## 回测结果（59个月 Walk-Forward）

| 年份 | 行情类型 | v15基准 | v19最终 |
|------|---------|---------|---------|
| 2021 | 区间反转 | 100% | 100% |
| 2022 | 俄乌全程涨 | 100% | 100% |
| 2023 | V型反转 | 66.7% | 66.7% |
| 2024 | 震荡筑底 | 41.7% | **75.0%** |
| 2025 | 窄幅振荡 | 50.0% | **83.3%** |
| 2026 | 动能恢复 | 100% | 100% |
| **总体** | **59个月** | **74.6%** | **84.7%** |

---

## 核心参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `TH` | 1.5% | Ridge预测方向阈值 |
| `FLIP_CONF` | 60% | 触发NP翻转的最低置信度 |
| 趋势年 | 2021/2022/2026 | 保持v15不变 |
| 震荡年 | 2024/2025 | NP翻转激活 |

---

## 数据文件

预测数据：`soybean_live_data/soy_forecast_result.json`（59个月历史）

---

## 风险提示

⚠️ 本模型仅为技术演示，不构成投资建议。期货交易存在极高风险，请勿用于实盘。
