---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 20e8ae7f15a285f002945718907f788f
    PropagateID: 20e8ae7f15a285f002945718907f788f
    ReservedCode1: 3045022100aea74314da908568cb63c009303a3885d9ed64c096a0e52bc74ab3fe01f49a84022062c7bfe116ef05fb7c306c47b196b891c0adecce010e977d88b05c161678a473
    ReservedCode2: 3046022100cf9a99bc131949b3f7032333ce027fe0555b9c23535ccaa458682117a8cd0a13022100e40c1f4435607a922c0c0adc1fa9e8f393942c7b8212d87878085827462fa67a
category: finance
description: A股技术分析工具 — 持仓诊断与个股深度分析。功能：持仓批量分析（支持用户提供的持仓数据）、个股技术分析（名称→自动查代码→获取数据→输出完整报告）。涵盖RSI(Wilder)、MACD、MA、BOLL、量能分析、交易评分、市场阶段判断、止损止盈建议。
name: A股技术面分析
tags:
    - A股
    - 技术分析
    - RSI
    - MACD
    - BOLL
    - 持仓管理
---

# A股技术分析工具

## 核心功能

1. **持仓批量分析** — 用户传入持仓表（含名称/数量/成本/现价），批量计算所有标的，输出诊断报告
2. **个股深度分析** — 用户提供股票名称，自动查代码并分析，输出完整技术报告

## 数据源

### 实时行情
```
https://qt.gtimg.cn/q={code}
```
返回 GBK 编码的管道分隔数据，字段索引（从1起）：
- f[1] = 股票名称
- f[3] = 当前价格
- f[4] = 昨日收盘价
- f[6] = 成交量（手）
- f[33] = 今日最高价
- f[34] = 今日最低价
- f[2] = 股票代码

**重要**：同一标的在腾讯行情可能存在 `sh6xxxxx` 和 `sz00xxxx` 两种前缀混用的情况，查询时需取 `f[2]` 字段中的纯数字部分作为 key 去重。

解析伪代码：
```python
rt = subprocess.run(f'curl -s "https://qt.gtimg.cn/q={codes_str}"', shell=True, capture_output=True)
rt_text = rt.stdout.decode('gbk').strip()
for part in [p.strip() for p in rt_text.split('";') if p.strip()]:
    if '~' not in part: continue
    inner = part.split('"')[1] if '"' in part else ''
    if '~' not in inner: continue
    f = inner.split('~')
    code_num = f[2]
    name = f[1]
    price = float(f[3])
    prev = float(f[4])
    high = float(f[33]) if f[33] else price
    low = float(f[34]) if f[34] else price
    realtime[code_num] = {'name': name, 'price': price, 'prev': prev, 'high': high, 'low': low}
```

### K线数据（前复权日线）
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayhfq&param={symbol},day,,,300,qfq
```
- symbol 支持格式：`sh600498`、`sz002342`（前缀必须小写）
- 字段：day, open, close, high, low, volume（前复权）
- 返回数据按时间升序排列
- 取 300 条历史数据（覆盖约14个月）

解析伪代码：
```python
cmd = f'curl -s "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayhfq&param={code},day,,,300,qfq"'
r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
raw = r.stdout.strip().replace('kline_dayhfq=', '')
data = json.loads(raw)
# 匹配 key（腾讯行情 key 可能带 sh/sz 前缀，转换为纯数字匹配）
for k in data['data']:
    kn = k.lower().replace('sz', '').replace('sh', '')
    tn = code.lower().replace('sz', '').replace('sh', '')
    if kn == tn:
        key = k
        break
klines = data['data'][key].get('qfqday') or data['data'][key].get('day') or []
daily = []; closes = []; vols = []
for item in klines:
    d = {'day': item[0], 'open': float(item[1]), 'close': float(item[2]),
         'high': float(item[3]), 'low': float(item[4]), 'volume': float(item[5])}
    daily.append(d); closes.append(d['close']; vols.append(d['volume'])
```

**注意**：不同数据源（腾讯/ifzq/同花顺）的历史价格可能有细微差异，导致RSI绝对值不同，但趋势一致。分析以趋势判断为主。

### 股票代码查询
使用 `mcp_matrix_batch_web_search` 搜索 `{股票名称} 股票代码 A股`，从搜索结果的 snippet/title 中提取股票代码（如 `sh600498`、`sz002342`）。

---

## 核心指标计算

### 1. RSI — 必须用 Wilder 递推法

**常见错误**：用简单平均（`sum(gains[:p]) / p`）算RSI会导致结果偏大。必须用 Wilder 平滑：

```python
def calc_rsi_wilder(c, p=14):
    if len(c) < p + 1:
        return None
    deltas = [c[i+1] - c[i] for i in range(len(c) - 1)]
    gains = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]
    # 第p天用简单平均初始化
    ag = sum(gains[:p]) / p
    al = sum(losses[:p]) / p
    # 第p天之后用Wilder递推
    for i in range(p, len(gains)):
        ag = (ag * (p - 1) + gains[i]) / p
        al = (al * (p - 1) + losses[i]) / p
    if al == 0:
        return 100.0
    return round(100 - 100 / (1 + ag / al), 2)
```

公式解释（以 p=14 为例）：
- AG_t = (AG_{t-1} × 13 + Gain_t) / 14
- AL_t = (AL_{t-1} × 13 + Loss_t) / 14
- RSI = 100 - 100 / (1 + AG/AL)

### 2. MACD（标准参数 12/26/9）

```python
def ema(d, p):
    k = 2 / (p + 1)
    r = [d[0]]
    for i in range(1, len(d)):
        r.append(d[i] * k + r[-1] * (1 - k))
    return r

def macd(c):
    ef = ema(c, 12)
    es = ema(c, 26)
    dif = [f - s for f, s in zip(ef, es)]
    dea = ema(dif, 9)
    m = (dif[-1] - dea[-1]) * 2  # MACD柱 = (DIF - DEA) * 2
    return {
        'dif': round(dif[-1], 3),
        'dea': round(dea[-1], 3),
        'macd': round(m, 3)  # 正=红柱，负=绿柱
    }
```

### 3. BOLL 布林带（参数 20）

```python
def boll(c, p=20):
    if len(c) < p:
        return None
    m_v = sum(c[-p:]) / p
    s = sqrt(sum((x - m_v) ** 2 for x in c[-p:]) / p)
    return {
        'u': round(m_v + 2 * s, 3),   # 上轨
        'm': round(m_v, 3),            # 中轨 = MA20
        'l': round(m_v - 2 * s, 3)     # 下轨
    }
```

### 4. 均线

```python
def ma(c, p):
    return round(sum(c[-p:]) / p, 3) if len(c) >= p else None
```

---

## 评分系统

### 量能评分（30分）

| 量比（vs 5日均量） | 量能区 | v_min | v_max | 得分公式 |
|---|---|---|---|---|
| ≥ 2.0 | 放量区 | 2.0 | 3.0 | min(30, vol_ratio/v_max×30) |
| ≥ 1.5 | 温和放量区 | 1.5 | 2.0 | min(30, vol_ratio/v_max×30) |
| ≥ 1.0 | 正常区 | 1.0 | 1.5 | min(30, vol_ratio/v_max×30) |
| < 1.0 | 缩量区 | 0.3 | 1.0 | max(0, vol_ratio/v_min×10) |

### RSI评分（25分）
- RSI ≥ 50 → 25分（满分）
- RSI < 50 → max(0, RSI/50 × 15)

### 突破确认评分（25分）
- 距近1年高点突破% > 0 → min(25, 突破% × 2.5)
- 距近1年高点突破% ≤ 0 → max(0, 突破% × 2.5 + 12.5)
- 即：创新高给25分创新低给0分

### 板块强弱（15分）
- 固定给 15 分（因无实时板块数据，简化处理）

### 总分与操作建议

| 总分 | 建议 | 仓位上限 |
|---|---|---|
| ≥ 80 | 强烈买入 | 8成 |
| ≥ 60 | 买入 | 6成 |
| ≥ 40 | 观望 | 3成 |
| ≥ 20 | 减仓 | 0成 |
| < 20 | 空仓 | 0成 |

---

## 市场阶段判断

优先级判断顺序（逐一匹配）：

```
1. RSI > 75 或 价格 > BOLL上轨+0.1
   → 主升浪末期 ⚠️ 注意减仓

2. 价格 > MA5 > MA20 且 RSI > 65
   → 主升浪中期 📈 趋势延续

3. 价格 > MA20 且 RSI > 50 且 MACD柱 > 0
   → 主升浪初期 🚀 放量启动

4. 价格 < MA20
   → 调整期 🔻 等待信号

5. 其他情况
   → 吸筹期 🔄 震荡筑底
```

---

## 止损止盈规则

| 类型 | 计算方式 | 说明 |
|------|---------|------|
| 止损价 | 向下6%（round(price_now × 0.94, 2)） | 通用止损 |
| 止盈1 | +5%（round(price_now × 1.05, 2)） | 第一目标位 |
| 止盈2 | +10%（round(price_now × 1.10, 2)） | 第二目标位 |

**重要**：ST股必须单独设置更严格止损（8-10%），因为涨跌幅限制导致反弹难度更大。

---

## 关键价位计算

### 支撑位（取3个，最近的在前）
从近60日数据中筛选：同一价位±2%范围内出现≥3次的低点，且低于现价，按价格升序取最后3个。

### 压力位（取3个）
从近60日数据中筛选：高于现价的最高价，按价格升序取前3个。

### 近1年高点
`cutoff = (datetime.date.today() - timedelta(days=365)).isoformat()`
过滤后的最高价。

### 近6月区间
`cutoff6m = (datetime.date.today() - timedelta(days=180)).isoformat()`
过滤后的最低价/最高价，计算现价在区间中的百分位。

---

## 持仓批量分析输入格式

用户提供的持仓数据格式：
```
股票名称  持仓数量  成本价  现价  市值  当日盈亏  涨跌幅
巨力索具  1900    23.466  22.110  42,009  -2,569.50  -5.767%
```

注意：用户提供的"现价"可能与实时行情有差异（用户可能是收盘价），以用户提供的现价为准计算盈亏，但技术指标以实时/最新K线数据为准。

---

## 输出格式模板

### 个股分析输出

```
================================================================
  股票名称 (代码) 技术分析
================================================================
数据日期: YYYY-MM-DD

【价格】
  现价: XX.XX  昨收: XX.XX  涨跌: +X.XX (+X.XX%)
  今高: XX.XX  今低: XX.XX
  近5日收益: +X.X%  近30日收益: +X.X%

【均线】
  MA5: XX.XXX  MA10: XX.XXX  MA14: XX.XXX  MA20: XX.XXX  MA60: XX.XXX
  偏离MA20: +X.X%

【RSI】
  RSI(14): XX.X

【MACD】
  DIF: X.XXX  DEA: X.XXX  MACD柱: +X.XXX

【BOLL布林带】
  上轨: XX.XXX  中轨: XX.XXX  下轨: XX.XXX
  距BOLL上轨: +X.X%  距BOLL下轨: +X.X%

【量能】
  今日量比(vs均量5日): X.XX  量能区: XXXX

【关键价位】
  近1年高点: XX.XX  距高点: -X.X%
  近6月区间: [XX, XX]  当前在区间XX%分位
  近20日区间: [XX, XX]
  支撑位: XX.XX / XX.XX / XX.XX
  压力位: XX.XX / XX.XX / XX.XX

【交易评分】
  量能强度: XX.X/30  RSI强度: XX.X/25  突破确认: X.X/25  板块强弱: 15/15
  总分: XX.X/100

【操作建议】
  市场阶段: XXXX — XXXX
  建议: XXXX (仓位上限: X成)
  止损价: XX.XX (距现价 X.X%)
  止盈1: XX.XX (+5%)  止盈2: XX.XX (+10%)
================================================================
```

### 持仓总览输出

**表1：按盈亏排序**
| 名称 | 持仓 | 成本 | 现价 | 市值 | 持仓盈亏 | 盈亏% | RSI | 阶段 | MA20偏离 | 量比 |

**表2：技术指标（按评分排序）**
| 名称 | RSI14 | MA5 | MA14 | MA20 | 偏离% | 量比 | 量能区 | MACD柱 | DIF | DEA |

**表3：布林与止盈止损（按评分排序）**
| 名称 | BOLL上 | BOLL中 | BOLL下 | 近6月高低 | 分位 | 止损 | 止盈1 | 止盈2 | 仓位 | 评分 | 操作 |

**表4：持仓结构（按市值排序）**
| 名称 | 市值 | 占比 |

**底部汇总**：总市值 / 总成本 / 总盈亏（元/百分比）

### 风险分类逻辑

**必须止损（立即处理）**：
- RSI < 30（极度超卖）
- 处于"调整期"阶段且偏离MA20 < -15%
- ST股且跌幅 > 15%

**注意减仓（主升浪末期）**：
- RSI > 75
- 突破BOLL上轨
- 偏离MA20 > 20%
- 近30日涨幅 > 50%
- 近6月分位 > 90%

**继续持有（趋势健康）**：
- RSI 在 50-70 之间
- 偏离MA20 < 15%
- MACD红柱且零轴上方
- 均线多头排列

**低位关注（可补仓）**：
- 近6月分位 < 40%
- RSI 在 40-55 之间
- 处于吸筹期/调整期末端

---

## 常见陷阱与注意事项

1. **量价背离**：涨幅大但量比小（<1.2），说明无量上涨，动能可能衰竭
2. **MACD绿柱+无量反弹**：烽火通信案例，大涨但MACD仍绿柱，无持续性
3. **BOLL上轨突破**：突破后容易快速回落，是减仓信号而非追入信号
4. **ST股特殊性**：涨跌停幅度小（5%）、流动性差、退市风险高，必须单独设更严格止损
5. **数据时间差**：用户提供的"现价"可能是昨收价，技术指标以实时行情为准
6. **不同数据源差异**：腾讯/ifzq/同花顺的前复权数据略有差异，RSI绝对值可能差1-3，但趋势一致
7. **量比计算基准**：使用前复权K线的成交量，不是真实成交量，但比值趋势有效

---

## 完整计算脚本（Python 3）

### 持仓批量分析脚本

```python
import json, subprocess
from math import sqrt
import datetime

holdings = [
    # ("名称", "代码", 持仓数量, 成本价, 用户现价),
    ("巨力索具", "sz002342", 1900, 23.466, 22.110),
    ("北方稀土", "sh600111", 600, 49.740, 54.750),
    # ... 更多持仓
]

codes_str = ",".join([h[1] for h in holdings])
rt = subprocess.run(f'curl -s "https://qt.gtimg.cn/q={codes_str}"', shell=True, capture_output=True)
rt_text = rt.stdout.decode('gbk').strip()
realtime = {}
for part in [p.strip() for p in rt_text.split('";') if p.strip()]:
    if '~' not in part: continue
    inner = part.split('"')[1] if '"' in part else ''
    if '~' not in inner: continue
    f = inner.split('~')
    code_num = f[2]; name = f[1]; price = float(f[3]); prev = float(f[4])
    high = float(f[33]) if f[33] else price; low = float(f[34]) if f[34] else price
    realtime[code_num] = {'name': name, 'price': price, 'prev': prev, 'high': high, 'low': low}

def get_daily(symbol):
    cmd = f'curl -s "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayhfq&param={symbol},day,,,300,qfq"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        raw = r.stdout.strip().replace('kline_dayhfq=', '')
        data = json.loads(raw)
        for k in data['data']:
            kn = k.lower().replace('sz','').replace('sh','')
            tn = symbol.lower().replace('sz','').replace('sh','')
            if kn == tn: key = k; break
        klines = data['data'][key].get('qfqday') or data['data'][key].get('day') or []
        daily = []; closes = []; vols = []
        for item in klines:
            daily.append({'day': item[0], 'open': float(item[1]), 'close': float(item[2]),
                          'high': float(item[3]), 'low': float(item[4]), 'volume': float(item[5])})
            closes.append(float(item[2])); vols.append(float(item[5]))
        return {'daily': daily, 'closes': closes, 'vols': vols}
    except: return None

def calc_rsi_wilder(c, p=14):
    if len(c) < p + 1: return None
    deltas = [c[i+1]-c[i] for i in range(len(c)-1)]
    gains=[max(d,0) for d in deltas]; losses=[max(-d,0) for d in deltas]
    ag=sum(gains[:p])/p; al=sum(losses[:p])/p
    for i in range(p, len(gains)): ag=(ag*(p-1)+gains[i])/p; al=(al*(p-1)+losses[i])/p
    return round(100-100/(1+ag/al), 2) if al > 0 else 100

def ema(d, p):
    k=2/(p+1); r=[d[0]]
    for i in range(1, len(d)): r.append(d[i]*k+r[-1]*(1-k))
    return r

def macd(c):
    ef=ema(c,12); es=ema(c,26); dif=[f-s for f,s in zip(ef,es)]; dea=ema(dif,9)
    m=(dif[-1]-dea[-1])*2
    return {'dif': round(dif[-1],3), 'dea': round(dea[-1],3), 'macd': round(m,3)}

def boll(c, p=20):
    if len(c) < p: return None
    m_v=sum(c[-p:])/p; s=sqrt(sum((x-m_v)**2 for x in c[-p:])/p)
    return {'u': round(m_v+2*s,3), 'm': round(m_v,3), 'l': round(m_v-2*s,3)}

def ma(c, p): return round(sum(c[-p:])/p, 3) if len(c) >= p else None

results = []
for name, code, shares, cost, user_price in holdings:
    kd = get_daily(code)
    if not kd: continue
    daily=kd['daily']; closes=kd['closes']; vols=kd['vols']
    code_num=code.replace('sh','').replace('sz','')
    rt_data=realtime.get(code_num)
    price_now=rt_data['price'] if rt_data else closes[-1]
    price_yesterday=closes[-2]; latest_day=daily[-1]['day']
    change=price_now-price_yesterday; pct=change/price_yesterday*100
    avg_vol_5=sum(vols[-5:])/5; vol_ratio=vols[-1]/avg_vol_5
    sma5=ma(closes,5); sma10=ma(closes,10); sma14=ma(closes,14); sma20=ma(closes,20); sma60=ma(closes,60)
    rsi_val=calc_rsi_wilder(closes); b=boll(closes); m=macd(closes)
    deviation=round((price_now-sma20)/sma20*100,2) if sma20 else None

    cutoff=(datetime.date.today()-datetime.timedelta(days=365)).isoformat()
    past_year=[d for d in daily if d['day']>=cutoff]
    prev_high=max(d['high'] for d in past_year) if past_year else price_now
    break_pct=(price_now-prev_high)/prev_high*100

    cutoff6m=(datetime.date.today()-datetime.timedelta(days=180)).isoformat()
    past_6m=[d for d in daily if d['day']>=cutoff6m]
    low_6m=min(d['low'] for d in past_6m) if past_6m else price_now
    high_6m=max(d['high'] for d in past_6m) if past_6m else price_now
    pos_6m=(price_now-low_6m)/(high_6m-low_6m)*100 if high_6m!=low_6m else 50

    market_val=shares*price_now; profit=market_val-shares*cost; profit_pct=round(profit/(shares*cost)*100,2)
    stop_loss=round(price_now*0.94,2); tp1=round(price_now*1.05,2); tp2=round(price_now*1.10,2)

    # 阶段
    if rsi_val and rsi_val>75: stage="主升浪末期"
    elif price_now>sma5>sma20 and (rsi_val and rsi_val>65): stage="主升浪中期"
    elif price_now>sma20 and (rsi_val and rsi_val>50) and m['macd']>0: stage="主升浪初期"
    elif price_now<sma20: stage="调整期"
    else: stage="吸筹期"

    # 评分
    if vol_ratio>=2.0: regime="放量区"; v_min,v_max=2.0,3.0
    elif vol_ratio>=1.5: regime="温和放量区"; v_min,v_max=1.5,2.0
    elif vol_ratio>=1.0: regime="正常区"; v_min,v_max=1.0,1.5
    else: regime="缩量区"; v_min,v_max=0.3,1.0
    vol_score=min(30,round(vol_ratio/v_max*30,1)) if vol_ratio>=v_min else max(0,round(vol_ratio/v_min*10,1))
    rsi_score=25 if rsi_val>=50 else max(0,round(rsi_val/50*15,1))
    break_score=min(25,round(break_pct*2.5,1)) if break_pct>0 else max(0,round(break_pct*2.5+12.5,1))
    sector_score=15; total_score=vol_score+rsi_score+break_score+sector_score

    results.append({...})

total_market=sum(r['market_val'] for r in results)
total_cost=sum(r['shares']*r['cost'] for r in results)
total_profit=sum(r['profit'] for r in results)
total_profit_pct=total_profit/total_cost*100

# 输出4张表 + 汇总
```

### 个股分析脚本（单标的）

```python
import json, subprocess
from math import sqrt
import datetime

# 1. 股票名称 → 代码（需用户先用web_search确认代码，此处假设已获取）
code = "sz002342"

# 2. 实时行情
rt = subprocess.run(f'curl -s "https://qt.gtimg.cn/q={code}"', shell=True, capture_output=True)
rt_text = rt.stdout.decode('gbk').strip()
if '~' in rt_text:
    f = rt_text.strip().split('"')[1].split('~')
    name=f[1]; price_now=float(f[3]); prev=float(f[4])
    high=float(f[33]) if f[33] else price_now; low=float(f[34]) if f[34] else price_now

# 3. K线（调用 get_daily，与持仓脚本完全相同）
kd = get_daily(code)
daily=kd['daily']; closes=kd['closes']; vols=kd['vols']
price_now=price_now or closes[-1]
price_yesterday=closes[-2]; latest_day=daily[-1]['day']
avg_vol_5=sum(vols[-5:])/5; vol_ratio=vols[-1]/avg_vol_5

# 4. 计算指标（全部调用前述函数）
# calc_rsi_wilder, ema, macd, boll, ma 全部同上

# 5. 支撑压力位
support_levels=sorted(set([d['low'] for d in daily[-60:]
    if sum(1 for d2 in daily[-60:] if abs(d2['low']-d['low'])<d['low']*0.02)>=3
    and d['low']<price_now]))[-3:]
resistance_levels=sorted(set([d['high'] for d in daily[-60:] if d['high']>price_now]))[:3]

# 6. 输出完整报告（格式模板见上文）
```

---

## 依赖

- Python 3 标准库：`json`, `subprocess`, `math.sqrt`, `datetime`
- 无需安装任何第三方包（腾讯/ifzq接口直接返回文本）
- 可选：`mcp_matrix_batch_web_search`（查股票代码）