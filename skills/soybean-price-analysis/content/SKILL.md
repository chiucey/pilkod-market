---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9a0d1b23dec690e1b7b1ebc2e86ae00e
    PropagateID: 9a0d1b23dec690e1b7b1ebc2e86ae00e
    ReservedCode1: 304602210087456822110c2a88fe47053adacd2b4638eec1dff435a2e96bd7b154a3daec3c022100a782a94e7ba956ecccadb585cf4867c8d5cd0857c061798e474d02ac14dec728
    ReservedCode2: 304502206f9dff62a032cac3c3b4c812dd4ab64b26533fd1f2bddd6ff19a7dad068ac952022100dfb6a56fc51185e22da9e23608932333ce8736065ca1a3764e4c4e89aa32451d
description: 大豆（Soybean ZS/USD）价格分析、量化模型与交易系统。覆盖：CBOT大豆期货行情、USDA WASDE供需解读、中美贸易政策影响、南美产区供给分析、媒体情绪量化、7因子+因子H实时打分、8层仓位护栏系统、交互式HTML行情助手。数据源：CME Group、Barchart、Reuters、Bloomberg、X/Twitter、新华社、ProFarmer、DTN、USDA。
name: soybean-price-analysis
---

# 大豆价格分析技能包 v5.21
## Soybean Price Analysis & Trading System
**更新：2026-03-24 | 状态：生产运行中**

---

## 核心文件索引

| 文件路径 | 说明 |
|---------|------|
| `scripts/soy_v521_model.py` | v5.21纯多头回测引擎（279行） |
| `scripts/soy_v520_model.py` | v5.20基准（含做空） |
| `../soybean-trading/SKILL.md` | v5.21完整交易系统手册 |
| `../soybean-trading/scripts/soybean_gap_model_v4.py` | v4三因子量化模型 |
| `/workspace/soybean_live_data/index.html` | 交互式行情助手（直接打开） |
| `/workspace/soybean_live_data/soy_live_data.json` | MCP实时数据缓存 |

---

## 当前行情快照（2026-03-24）

| 品种 | 价格 | 涨跌 | 来源 |
|------|------|------|------|
| ZS May26 | 1160-2¢/bu | -0.09% | CME |
| ZS Jul26 | 1176-0¢/bu | -0.04% | CME |
| ZS Nov26 | 1148-4¢/bu | +0.17% | Barchart |
| DXY | 104.3 | — | — |
| USDA期末库存 | 350 M bu | 未变动 | WASDE Mar26 |
| 巴西产量 | 178 MT | 纪录新高 | USDA |
| 美豆关税 | 13%（部分减免） | — | S&P Global |

---

## v5.21 量化模型关键参数

### 七因子打分（0-100分制）

| 因子 | 说明 | PEACE权重 | TENSION权重 | BOOM权重 |
|------|------|----------|------------|---------|
| A. 天气 | VIX+La Nina+种植期溢价 | 5% | 10% | 15% |
| B. 美元 | DXY Z-Score标准化 | **35%** | 20% | 8% |
| C. 供需 | USDA出口+检验量 | 25% | 20% | 10% |
| D. 压榨 | 豆油/豆粕需求代理 | 20% | 20% | 12% |
| E. 联动 | CBOT玉米+WTI原油 | 5% | 5% | 20% |
| F. 产区 | US/Brazil/Argentina独立 | 5% | 15% | **25%** |
| G. 贸易 | 关税分级+采购承诺 | 5% | 10% | 10% |
| **H. 媒体** ⭐ | 来源权重×情感分析 | 25% | 15% | 10% |

### 因子H计算细则
```
H = Σ(news_i_score × source_weight_i) / Σsource_weight_i
news_score: 利多=70-100, 中性=40-60, 利空=0-30
source_weight: ProFarmer×1.6 > Reuters×1.5 > Argus×1.4 > Bloomberg×1.3 > X×1.2 > 新华社×1.1 > CNN×1.0

仓位影响 = clip(H × 0.15, -15%, +15%)
最终仓位 = max(TENSION保底60%, base_pos + 仓位影响)
```

---

## 8层仓位护栏速查

```
✅ pos = max(0, pscore)  ← 纯多头核心约束，永不小于0

① RSI≥80 → cap 55%    （RSI≥75 → cap 65%）
② TENSION+rr≥1.5% → cap 70%   BOOM+rr≥1.5% → cap 55%
③ ⭐ TENSION → floor = max(pscore, 60%)     ← 21个月系统性低估修复
④ PEACE+mom3>0 → floor 60%   PEACE+mom3<-3% → cap 25%
⑤ 压榨<0 → cap 40%
⑥ ⭐ 2大产区减产 → floor 50%    3大丰产 → cap 40%
⑦ ⭐ 关税≥25% → cap 10%    10-25% → cap 30%    3-10% → cap 60%
⑧ WASDE月 → pos × 80%
```

---

## 回测绩效（v5.20 60个月）

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 年化收益 | >8% | +9.84% | ✅ |
| 夏普比率 | >1.1 | 2.65 | ✅ |
| 方向准确率 | >85% | 86.44% | ✅ |
| MAPE | <5% | 1.60% | ✅ |
| **MaxDD** | **<5%** | **-3.12%** | ✅ |
| 盈亏比 | >2x | 2.58x | ✅ |
| Sortino | >1.5 | 15.7 | ✅ |
| Calmar | >2 | 3.21 | ✅ |

> v5.21纯多头MaxDD=-10.11%（目标<5%未达成）。原因：2022-2024年价格下跌35%，纯多头无法做空对冲。**解决方案：买入看跌期权保护**，保留上行收益同时压缩MaxDD。

---

## 贸易政策影响矩阵

| 关税等级 | CBOT影响 | 仓位上限 | 情景 |
|---------|---------|---------|------|
| ≥25%（全面贸易战）| 需求归零 | cap 10% | BOOM |
| 10-25%（升级） | 显著压力 | cap 30% | TENSION |
| 3-10%（摩擦） | 温和压力 | cap 60% | TENSION |
| 0-3%（正常） | 中性 | 无限制 | PEACE |

**当前（2026-03）：关税13%（部分减免）→ 层级2 → cap 60%**

---

## 数据源速查

| 数据类型 | 来源 | 更新频率 | 工具 |
|---------|------|---------|------|
| CBOT行情 | CME Group / Barchart | 日内 | batch_web_search |
| WASDE供需 | USDA官网 | 每月12日 | extract_content_from_websites |
| 出口检验 | USDA FAS | 周度 | batch_web_search |
| 贸易政策 | Reuters / Argus Media | 实时 | batch_web_search |
| 天气/La Nina | NOAA CPC | 周度 | batch_web_search |
| 媒体情绪 | Reuters/Bloomberg/X/新华社 | 分钟级 | batch_web_search |
| 巴西产量 | CONAB / USDA FAS | 双周 | batch_web_search |

---

## 快速命令

```bash
# 运行v5.21回测
python3 /workspace/skills/soybean-price-analysis/scripts/soy_v521_model.py

# 查看实时数据
cat /workspace/soybean_live_data/soy_live_data.json

# 打开交互助手
# https://whu0zc7z4sec.space.minimaxi.com
```
