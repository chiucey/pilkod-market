# DCF核心公式汇总

## 一、现金流折现基础

### 1.1 净现值 (NPV)
```
NPV = Σ [CFt / (1 + r)^t]
```
其中：
- CFt = 第t期的现金流
- r = 折现率
- t = 期数

### 1.2 内部收益率 (IRR)
使NPV = 0的折现率：
```
Σ [CFt / (1 + IRR)^t] = 0
```

---

## 二、企业自由现金流 (FCFF)

### 2.1 基本公式
```
FCFF = EBIT × (1 - Tax Rate) + D&A - CapEx - ΔNWC
```

### 2.2 详细分解
```
FCFF = 息税前利润 (EBIT)
     - EBIT税费
     + 折旧摊销 (D&A)
     - 资本支出 (CapEx)
     - 营运资本变动 (ΔNWC)
```

### 2.3 简化公式（使用EBIT）
```
NOPAT = EBIT × (1 - Tax Rate)
FCFF = NOPAT + D&A - CapEx - ΔNWC
```

---

## 三、股权自由现金流 (FCFE)

```
FCFE = 净利润 + D&A - CapEx - ΔNWC + 净借款
```

---

## 四、终值计算

### 4.1 永续增长法 (Gordon Growth Model)
```
TVn = FCFFn+1 / (WACC - g)
    = FCFFn × (1 + g) / (WACC - g)
```
其中：
- g = 永续增长率
- WACC = 加权平均资本成本

### 4.2 退出倍数法
```
TVn = EBITn+1 × EV/EBIT倍数
    = Revenuen+1 × EV/Revenue倍数
    = NetIncomen+1 × P/E倍数
```

---

## 五、WACC计算

### 5.1 基本公式
```
WACC = Re × E/(D+E) + Rd × (1-T) × D/(D+E)
```

### 5.2 股权成本 (CAPM)
```
Re = Rf + β × (Rm - Rf)
   = Rf + β × ERP
```

### 5.3 债务成本
```
Rd = 年利息支出 / 债务总额 × 100%
```

---

## 六、每股内在价值

### 6.1 两阶段模型
```
Enterprise Value = Σ [FCFFt / (1 + WACC)^t] + TVn / (1 + WACC)^n

Equity Value = Enterprise Value - Net Debt
Intrinsic Value per Share = Equity Value /  Shares Outstanding
```

### 6.2 三阶段模型（考虑过渡期）
```
Enterprise Value = Σ [FCFFt / (1 + WACC)^t] (高速增长期)
                 + Σ [FCFFt / (1 + WACC)^t] (过渡期)
                 + TVn / (1 + WACC)^n (永续期)
```

---

## 七、关键比率

### 7.1 利润率指标
```
Gross Margin = (Revenue - COGS) / Revenue
EBIT Margin = EBIT / Revenue
Net Margin = Net Income / Revenue
```

### 7.2 估值倍数
```
EV/EBITDA = Enterprise Value / EBITDA
EV/Revenue = Enterprise Value / Revenue
P/E = Market Cap / Net Income
P/B = Market Cap / Book Value
```

### 7.3 增长指标
```
Revenue Growth = (Revenue_t - Revenue_t-1) / Revenue_t-1
EPS Growth = (EPS_t - EPS_t-1) / EPS_t-1
```

---

## 八、敏感性分析

### 8.1 双因素敏感性
| 变量 | 低值 | 中值 | 高值 |
|------|------|------|------|
| WACC | X% | Y% | Z% |
| g (永续增长率) | A% | B% | C% |

### 8.2 情景设置
```
乐观情景: 营收增长X%, 利润率Y%
基准情景: 营收增长A%, 利润率B%
悲观情景: 营收增长M%, 利润率N%
```

---

## 九、模型检查清单

- [ ] FCFF与净利润的勾稽关系
- [ ] CapEx与D&A的匹配（长期D&A应≈CapEx）
- [ ] NWC变动的合理性
- [ ] WACC与公司风险匹配
- [ ] g < 长期GDP增长率
- [ ] 终值占总价值比例（通常<60%）
