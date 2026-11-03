# A 股开盘 9:30 集合竞价 阶段专属参考

> **使用场景**: 本参考专门给 9:30 集合竞价阶段 (cron 任务) 使用, 与 15:05 收盘任务的差异:
> - **9:30 阶段**: 数据仍在快速变化 (每分钟都在变), 北向通道暂停, 量能信号弱, 涨停规模通常 10-30 (未达 §27/§29 标准)
> - **15:05 阶段**: 数据已稳定, 北向 + 主力净流入 + 量能齐全, 涨停规模通常 30-100+ (可触发 §24/§27/§29/§31)

---

## 1. 9:30 阶段 5 大数据源 + fallback 链 (2026-07-01 实战稳定版)

```
优先级 1: 腾讯 qt.gtimg.cn (6 大指数) — 9:30 实测 100% 稳定
   ↓
优先级 2: Sina Market_Center.getHQNodeData (3-5% 涨幅股 + 涨停股) — 9:30 实测 100% 稳定 (注意 §42 STRINGS 字段)
   ↓
优先级 3: 浏览器 quote.eastmoney.com/ztb/ (涨跌停对比 + 涨停列表 + 炸板率 + 赚钱效应 + EM 系统建议) — 9:30 实测 100% 稳定 (15-30s 一次成功)
   ↓
优先级 4: 浏览器 data.eastmoney.com/bkzj/hy.html (沪/深 涨跌家数 + 行业 Top/Bottom) — 9:30 实测 100% 稳定 (15-30s 一次成功)
   ↓
Fallback 1: EastMoney push2.eastmoney.com (行业板块 + 概念板块) — 9:30 实测 30-50% 失败率, 先重试 1-2 次
   ↓
Fallback 2: Sina K-line (MACD, 反映 T-1 状态) — 9:30 阶段不更新, 仅作参考
```

**9:30 阶段 绝对禁止**:
- ❌ push2 涨/跌统计接口 (fs=m:0+s:3,m:1+s:2) — 高频 52 错误, 改用 bkzj/hy.html
- ❌ Sina 北向资金接口 (hk2hold) — 9:30-15:00 北向通道暂停, 无数据
- ❌ 依赖量能数据判断模式 — 9:30 集合竞价阶段量能信号弱, 10:30+ 才能可靠判断

---

## 2. §37 中性观望 灰区模式 (2026-07-01 09:30 实战新增)

### 触发条件 (优先级最高的判据)

1. **5 涨 1 跌 (上证极度疲弱 -0.5% ~ +0.5% 区间)** — 既非 §15 撕裂 (需 6 跌 0 涨) 也非 §31 严格 (需 5 涨 1 跌 + 上证独跌/疲弱 + 涨停 30-100)
2. **跌停 0-5** — 排除 §15 (跌停 > 30)
3. **涨停 < 30** (集合竞价阶段典型 13-29) — 排除 §27/§29 (需涨停 ≥ 30)
4. **V-reversal < 70%** — 排除 §26/§27/§29/§31/§32 (需 V > 60% 或 > 70% 或 > 90%)
5. **bullish_pct < 0.55** (多数红盘) — 排除 §31/§31 变体 (需 bearish_pct ≥ 0.55)
6. **强弱差距 < 1.0%** (上证与最强指数差距 < 1.0%) — 排除 §31 变体 (需 ≥ 1.0%)

**四要素同时满足时, 按 5 指标打分单独判定**, 不套用任何严格 V-reversal 模式.

### 仓位推导链 (7/1 实战)

```
Step 1: §37 触发 (5 涨 1 跌 + 上证极度疲弱 + 涨停 < 30 + V 极低 + 多数红盘)
Step 2: 5 指标打分 = 涨跌停比 3 + V 1 + 6 指数 2 + 行业主线 2 + 相对强度 3 = 11/15 (中档)
Step 3: §6.12 极度透支检测 → 科创 50 5 日 +15.5% ≥ 12% → 触发极度透支硬约束
Step 4: §6.12 硬约束 = "仓位上限下调一档" → 中档 30-40% (上限 40%) → 整体下调 10pct
Step 5: 最终仓位 = 20-30% (弱档上限偏保守, 中档下限 + §6.12 极度透支硬约束)
```

### 报告必须明确

1. **模式判定**: "未命中 §15-§36 任何严格 V-reversal 模式, 触发新的 §37 中性观望灰区 (5 涨 1 跌 + 上证极度疲弱 + 涨停 < 30 + V 极低 + 多数红盘)"
2. **5 指标打分**: "5 指标 11/15 (中档 9-12 区间) + §6.12 极度透支硬约束"
3. **不参考 EM 系统**: "EM 系统 XX% (9:30 阶段机械判定, 不参考) vs 规则建议 20-30%, 差异 ZZpct"
4. **10:30 验证后再调整**: "全天量能需 10:30+ 才能可靠判断, 验证后再决定是否加仓"

### 错配防御 (§37 vs 其他模式)

| 错配 | 原因 | 防御 |
|---|---|---|
| §37 错配为 §15 撕裂 | 5 涨 1 跌看似 "权重弱 + 个股强" | §15 需 6 跌 0 涨 + 跌停 > 30, §37 是 5 涨 1 跌 (方向相反) + 跌停 0 |
| §37 错配为 §31 严格 | 5 涨 1 跌看似 "上证独跌" | §31 需涨停 30-100, §37 涨停 < 30; §31 需 V > 90%, §37 V < 70% |
| §37 错配为 §31 变体 | 上证极度疲弱看似 "上证疲弱" | §31 变体需 idx_red=6 (6 涨 0 涨), §37 是 5 涨 1 跌; §31 变体需涨停 30-100, §37 涨停 < 30 |
| §37 错配为 §30 试探 | 涨停 < 30 看似 "试探" | §30 需 V > 90% + 3 涨 3 跌, §37 V < 70% + 5 涨 1 跌 |
| §37 错配为 §32 普涨预热 | 5 涨 1 跌看似 "上证独跌 + 普涨" | §32 需 V 60-90% + 涨停 100+, §37 V < 70% + 涨停 < 30 |
| §37 错配为 §33 灰区 | "未命中任何严格模式" 看似 §33 | §33 需 6 跌 0 涨, §37 是 5 涨 1 跌 (方向相反) |

---

## 3. §6.12 透支叠加 5 档位 实战映射表 (2026-07-01 实战补全)

| 基础档位 | 5 指标打分 | 基础仓位 | §6.12 极度透支叠加 | 实战案例 |
|---|---|---|---|---|
| 弱档 | < 9 | ≤ 25% | ≤ 15% (整体下调 10pct) | 理论, 未实测 |
| **中档** | **9-12** | **30-40%** | **20-30% (整体下调 10pct, 弱档上限偏保守)** | **7/1 09:30 实战 (§37 + 5 指标 11/15 + 科创 50 5 日 +15.5%)** |
| 强档 | ≥ 13 | 50-60% | 40-50% (整体下调 10pct, 强档下限偏保守) | 6/30 收盘实战 (§36 + 5 指标 15/15 + 科创 50 5 日 +15.22%) |
| §31 变体自身规则 | — | 40-45% | 维持 40-45% (自身规则已隐含 8 折) | 6/24 + 6/25 实战 (§31 变体 + 科创 50 5 日 +13.14%) |
| §36 minor exception | — | 50-60% | 下调一档到 40-50% | 6/30 实战 (§36 + 5 指标 15/15 + 科创 50 5 日 +15.22%) |

**铁律**: §6.12 极度透支 = "仓位上限下调一档" 严格执行 = 整体下调 10pct, 不论基础档位.

**绝对禁止**:
- 弱档场景给 ≤ 15% 过度保守 (实际弱档场景通常 bearish_pct 高 + V 极低 + 涨停稀缺, 5 指标自然落到弱档, §6.12 叠加意义不大)
- 中档场景给 > 25% 偏激进 (中档 + 极度透支严格执行 = 20-30% 上限, 不能给 25-30% 或 30-35%)
- 强档场景给 > 50% (强档 + 极度透支严格执行 = 40-50% 上限, 不能给 45-55% 或 50-60%)

---

## 4. 9:30 push2 行业数据 §43 修正规则 (2026-07-01 实战修正)

**原 §43 (6/29 实测)**: "9:30 阶段 push2 行业板块数据是噪声 (涨幅 0.02-0.06%, 主力净流入全部 0 亿元)"

**7/1 实战修正**: 9:30 阶段 push2 行业数据**不是总是噪声**, 实际依赖 9:30 集合竞价 vs 9:30+ 之后的不同时机.

**修正规则**:
- **真实信号 (可信赖)**: 涨幅 ≥ 0.5% 且净流入 ≥ 1 亿 (主力资金已流入, 集合竞价后第一分钟 push2 板块榜已刷新)
- **噪声 (旧 §43 描述)**: 涨幅 0.02-0.06% 且净流入 0 (集合竞价后第一分钟, 数据未刷新)
- **实操**: 9:30 抓取行业数据后**先检查涨幅/净流入是否在真实区间**, 真实数据可直接用, 噪声数据标 "⚠️ 数据缺失" 按 §2.5 处理

**7/1 09:30 实测真实信号 (可信赖)**: 半导体 +1.61% +10.20亿, 元件 +1.21% +6.07亿, 物流 +1.83% +1.66亿, 通信设备 +0.87% +2.59亿, 军工电子Ⅱ +1.44% +2.53亿

**7/1 09:30 实测真实信号 (回避)**: 玻璃玻纤 -2.98% +2932.51万, 能源金属 -1.29% +616.19万, 电网设备 -0.53% +525.94万

---

## 5. 9:30 阶段 浏览器 fallback 标准化 (2026-07-01 实战稳定)

### 5.1 quote.eastmoney.com/ztb/ — 涨跌停 + 涨停列表 + EM 系统建议

```python
# Step 1: 浏览器加载
browser_navigate("https://quote.eastmoney.com/ztb/")

# Step 2: 浏览器 console 提取
browser_console(expression="""
(() => {
  const allText = document.body.innerText;
  const zhangTingDuiBi = allText.match(/涨跌停对比[\\d:：:]+/g);
  const positionSuggest = allText.match(/根据市场表现, 建议仓位为\\s*\\d+\\s*%/);
  const effect = allText.match(/赚钱效应\\s*[\\u4e00-\\u9fff]+/);
  return JSON.stringify({
    zhangTingDuiBi: zhangTingDuiBi,
    positionSuggest: positionSuggest,
    effect: effect,
  });
})()
""")
```

**典型输出** (7/1 实战):
- `zhangTingDuiBi`: `["涨跌停对比19:0"]` (涨停 19 / 跌停 0)
- `positionSuggest`: `["根据市场表现, 建议仓位为 86%"]` (EM 系统建议, 9:30 阶段不参考)
- `effect`: `["赚钱效应 中"]`

### 5.2 data.eastmoney.com/bkzj/hy.html — 沪/深 涨跌家数 + 行业 Top/Bottom

```python
# Step 1: 浏览器加载
browser_navigate("https://data.eastmoney.com/bkzj/hy.html")

# Step 2: 浏览器 console 提取涨跌家数 (沪/深 header)
browser_console(expression="""
(() => {
  const allText = document.body.innerText;
  const shMatch = allText.match(/上证[^\\n]*?涨:\\s*(\\d+)\\s*平:\\s*(\\d+)\\s*跌:\\s*(\\d+)/);
  const szMatch = allText.match(/深证[^\\n]*?涨:\\s*(\\d+)\\s*平:\\s*(\\d+)\\s*跌:\\s*(\\d+)/);
  
  if (shMatch && szMatch) {
    const shUp = parseInt(shMatch[1]);
    const shFlat = parseInt(shMatch[2]);
    const shDown = parseInt(shMatch[3]);
    const szUp = parseInt(szMatch[1]);
    const szFlat = parseInt(szMatch[2]);
    const szDown = parseInt(szMatch[3]);
    const totalUp = shUp + szUp;
    const totalFlat = shFlat + szFlat;
    const totalDown = shDown + szDown;
    const total = totalUp + totalFlat + totalDown;
    return JSON.stringify({
      sh: {up: shUp, flat: shFlat, down: shDown, total: shUp+shFlat+shDown},
      sz: {up: szUp, flat: szFlat, down: szDown, total: szUp+szFlat+szDown},
      total: {up: totalUp, flat: totalFlat, down: totalDown, total: total},
      bullish_pct: (totalUp / total * 100).toFixed(2),
      bearish_pct: (totalDown / total * 100).toFixed(2),
    });
  }
  return JSON.stringify({error: 'no match'});
})()
""")
```

**典型输出** (7/1 实战):
```json
{
  "sh": {"up": 1202, "flat": 143, "down": 998, "total": 2343},
  "sz": {"up": 1604, "flat": 155, "down": 1165, "total": 2924},
  "total": {"up": 2806, "flat": 298, "down": 2163, "total": 5267},
  "bullish_pct": "53.28",
  "bearish_pct": "41.07"
}
```

**注意**: 9:30 阶段北向通道暂停, 涨跌家数直接用沪/深 header, 不需要看 hsgtV2.html (9:30 阶段该页全为休市).

### 5.3 行业 Top/Bottom 抓取 (bkzj/hy.html 同一页)

```python
browser_console(expression="""
(() => {
  const tables = document.querySelectorAll('table');
  const industryData = [];
  tables.forEach(t => {
    const headers = Array.from(t.querySelectorAll('thead th, thead td')).map(h => h.innerText.trim());
    if (headers.some(h => h.includes('名称')) && headers.some(h => h.includes('涨跌幅'))) {
      const rows = t.querySelectorAll('tbody tr');
      rows.forEach(r => {
        const cells = Array.from(r.querySelectorAll('td')).map(c => c.innerText.trim());
        if (cells.length > 0) industryData.push(cells);
      });
    }
  });
  return JSON.stringify(industryData.slice(0, 10), null, 2);
})()
""")
```

**典型输出** (7/1 实战 Top 3):
```
["1", "半导体", "...", "1.61%", "6.07亿", ..., "长川科技"]
["2", "元件", "...", "1.21%", "5.50亿", ..., "深南电路"]
["3", "通用设备", "...", "1.13%", "2.49亿", ..., "春晖智控"]
```

---

## 6. 10:30 验证清单 (全天关键时点)

9:30 集合竞价阶段 → 10:30 验证点 是开盘任务的核心节奏. 集合竞价 9:25-9:30 锁定开盘价后, 前 30 分钟 (9:30-10:00) 资金博弈最激烈, 10:30 是首个稳定验证点. **全天量能需 10:30+ 才能可靠判断**.

**4 项关键验证指标**:

1. **量能**: 9:30-10:30 半日量能是否 ≥ 5500 亿 (全天 1.1 万亿预期)?
   - 半日 ≥ 6000 亿 → 全天 1.2 万亿+, 健康
   - 半日 < 5000 亿 → 全天 < 1.0 万亿, 弱势
2. **涨停规模**: 9:30 涨停 19 → 10:30 是否放大到 30+/50+/100+?
   - < 30 维持 9:30 §37 灰区
   - 30-100 触发 §29 强普涨
   - 100+ 触发 §27/§24 普涨确认
3. **6 指数方向**: 9:30 5 涨 1 跌 → 10:30 是否仍维持 5+ 涨?
   - 上证翻红 (≥ 0%) → §31 变体 (上证疲弱) 风险解除
   - 上证跌幅扩大 → 需警惕 §15 撕裂
4. **涨跌家数背离**: 9:30 bullish_pct 53.28% → 10:30 是否仍维持 50%+?
   - bearish_pct 升至 0.55+ → 触发 §31/§15 撕裂, 仓位需进一步下调

**10:30 后的仓位调整建议**:

| 10:30 验证结果 | 仓位调整 |
|---|---|
| 量能 ≥ 1.0 万亿 + 涨停 ≥ 30 + 6 指数仍 5+ 涨 + bullish_pct ≥ 50% | 上修到 30-40% (中档, §6.12 仍生效) |
| 量能 8000-10000 亿 + 涨停 20-30 + 6 指数 4-5 涨 | 维持 20-30% (当前 §37 灰区) |
| 量能 < 8000 亿 + 涨停 < 20 + 6 指数 ≤ 4 涨 + bullish_pct < 45% | 下调到 15-20% (弱档下限, §6.12 + 量能不足) |

---

## 7. 9:30 阶段 关键时间戳规则

- **报告 H1 必须带日期前缀 + 时间戳**: `# 2026-07-01 今日 A 股【开盘】报告` + `**时间**: 2026-07-01 09:32`
- **核心结论 callout 必须包含时间戳**: 让用户知道这是 9:32 数据而非 9:35 / 10:00 / 10:30 数据
- **9:30-10:00 期间**北向通道暂停, 资金面信号弱; **南向是唯一可观察的资金面指标** (数据通常偏弱 1-2 亿)
- **报告中必须明确** "**全天量能需 10:30+ 才能可靠判断**" (与收盘任务区分)

---

## 8. 配套脚本

- `scripts/fetch_open_market_breadth.py` — 9:30 涨跌家数 + 涨跌停 + 行业 Top/Bottom 一次抓全 (浏览器 fallback 标准化)
- `scripts/count_limit_accurate.py` — 精确涨跌停计数 (A 股各种股价限制: 主板≥9.9%, 创业板/科创板≥19.5%, 北交所≥29.5%, ST≥4.9%), §37 阈值判定时使用此脚本的 `limit_up_count` 字段
- `scripts/sina_field_type_safe.py` — Sina `Market_Center.getHQNodeData` 数字字段 STRINGS → floats 包装 (所有 sina 接口处理必须经过此脚本或 to_float() 包装)

---

## 9. 实战参考案例 (2026-07-01)

- **飞书文档 obj_token**: `QvpwdWfLxo3atqxIhGlcsi4qn4b`
- **Wiki 链接**: https://shadow000902.feishu.cn/wiki/AQaEwAHNAiQDFOkPWPNcJbS5nig
- **revision_id**: 8
- **播客 mp3**: `/Users/taoyi/.hermes/audio_cache/podcast_open_2026-07-01.mp3` (2.1MB)
- **模式判定**: 未命中 §15-§36 任何严格模式 + 触发 §37 中性观望灰区 + §6.12 极度透支
- **仓位**: 20-30% (中档 + 极度透支硬约束, 整体下调 10pct)
- **EM 系统对照**: 86% (9:30 阶段机械判定, 不参考) vs 规则建议 20-30%, 差异 56-66pct
