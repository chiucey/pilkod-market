# A 股报告算法踩坑与修复模板

> 本文件是 `lark-stock-report` skill 的 **references/** 子文件，记录 `daily_report_v2.py`（A 股策略周报脚本）的算法踩坑与修复代码模板。新 session 加载 skill 时可参考此文件复用修复方案。
>
> 关联：lark-stock-report §2.5（报告可信度硬约束）+ §6.12（已知坑第 12 条）。

---

## 1. 背景

`daily_report_v2.py` 是 A 股策略周报的生成脚本（位于 `/Users/taoyi/.openclaw/workspace-stockTodayAnalysis/daily_report_v2.py`），由 cron 任务 `A股策略周报 - 交易日16:00` 自动调用。脚本核心模块：

| 函数 | 输入 | 输出 | 用途 |
|---|---|---|---|
| `get_index_realtime()` | — | `[{name, code, change, close}]` | 7 个指数收盘/涨跌幅（akshare） |
| `get_kline_data(symbol, days)` | 指数代码 | DataFrame | K 线（akshare） |
| `calculate_ma_and_stats(df)` | K 线 DataFrame | `{current, ma5, ma10, ma20, change_5d/10d/20d, support, resistance}` | MA20 + 5/10/20日收益 |
| `get_industry_data()` | — | DataFrame（行业板块） | **只走 akshare 一个接口（已知缺陷）** |
| `get_sentiment_score(indices, ma_data_dict)` | 7 个指数 + MA20 数据 | `int 0-100` | **情绪温度计（v2 修复版）** |
| `generate_conclusion(indices, ma_data_dict)` | 7 个指数 + MA20 | `List[str]` | 结论摘要（含仓位） |
| `generate_report()` | — | `List[str]` | 完整报告 |

---

## 2. 三个致命算法问题（2026-06-18 实测 → 2026-06-19 修复）

### 2.1 情绪温度计：严重低估透支

**问题代码（v1，已废弃）**：
```python
def get_sentiment_score(self, indices):
    avg_change = sum(i['change'] for i in indices) / len(indices)
    if avg_change > 1: base = 70
    elif avg_change > 0: base = 60
    elif avg_change > -1: base = 45
    else: base = 30
    # ⚠️ 粗估：avg_change * 5 估 5 日涨幅
    change_5d_avg = avg_change * 5
    if change_5d_avg < -5: base -= 10
    elif change_5d_avg > 3: base += 10
    return max(10, min(90, base))
```

**问题**：6/18 实测 avg_change=1.13% → `change_5d_avg` ≈ 5.65% → base = 70+10 = **80（偏热）**。但实际创业板 5日 +11.02%、科创50 5日 +14.93%，**严重透支**，应是 **88（极度贪婪/严重过热）**。

**修复代码（v2，已部署）**：
```python
def get_sentiment_score(self, indices, ma_data_dict=None):
    """情绪温度计 v2：成长端单独加分 + 透支检测"""
    if not indices: return 50
    avg_change = sum(i['change'] for i in indices) / len(indices)

    # 基础分（按当日 7 指数平均）
    if avg_change > 1: base = 70
    elif avg_change > 0: base = 60
    elif avg_change > -1: base = 45
    else: base = 30

    # 成长端单独加分（用 MA20 数据精确算 5 日涨幅）
    if ma_data_dict:
        for growth_name in ('创业板指', '科创50'):
            if growth_name in ma_data_dict:
                change_5d = ma_data_dict[growth_name].get('change_5d', 0)
                if change_5d > 10: base += 10
                elif change_5d > 5: base += 5

    # 透支检测（5 日最大涨幅封顶）
    max_5d = 0
    if ma_data_dict:
        max_5d = max((m.get('change_5d', 0) for m in ma_data_dict.values()), default=0)
    if max_5d >= 12: base = min(base, 88)
    elif max_5d >= 10: base = min(base, 85)
    elif max_5d >= 8: base = min(base, 80)

    return max(10, min(90, base))
```

**调用点修复**（必须传入 `ma_data_dict`）：
```python
# generate_report() 内
ma_data_dict = {}
for idx in indices:
    df = self.get_kline_data(idx['code'], 30)
    ma_data = self.calculate_ma_and_stats(df)
    if ma_data: ma_data_dict[idx['name']] = ma_data

# ✅ 修复：传入 ma_data_dict
sentiment = self.get_sentiment_score(indices, ma_data_dict)
```

### 2.2 仓位建议：右侧追涨

**问题代码（v1，已废弃）**：
```python
# generate_conclusion() 内
if avg_change < -1: conclusions.append("建议仓位：30%-50%，防守为主")
elif avg_change > 1: conclusions.append("建议仓位：50%-70%，适度积极")
else: conclusions.append("建议仓位：40%-60%，中性应对")
```

**问题**：6/18 avg_change=1.13% → "50%-70% 适度积极"。但 5 日 +14.93% 已严重透支，**应是 40%-55% 中性偏上**。这是典型的**右侧追涨**。

**修复代码（v2）**：
```python
# generate_conclusion() 内
max_5d = 0
if ma_data_dict:
    max_5d = max((m.get('change_5d', 0) for m in ma_data_dict.values()), default=0)

if avg_change < -1:
    conclusions.append("建议仓位：30%-50%，防守为主")
elif max_5d >= 10 and avg_change > 0:
    # 【关键修复】5 日涨幅 > 10% 即使当日涨，也给中性仓位
    conclusions.append(f"建议仓位：40%-55%（成长端 5 日 +{max_5d:.1f}% 透支，警惕回踩）")
elif avg_change > 1:
    conclusions.append("建议仓位：50%-70%，适度积极")
else:
    conclusions.append("建议仓位：40%-60%，中性应对")
```

### 2.3 趋势研判：5 日 +15% 仍判偏多

**问题代码（v1，已废弃）**：
```python
# generate_report() 内
for name in ['上证综指', '深证成指', '创业板指', '科创50']:
    ma = ma_data_dict[name]
    trend = "震荡偏多" if ma['change_5d'] > 0 and ma['current'] > ma['ma20'] else "震荡偏弱"
    report.append(f"### {name}")
    report.append(f"- **基准判断**：{trend}")
```

**问题**：6/18 创业板 5日 +11.02% / 科创50 5日 +14.93% **仍判"震荡偏多"**。透支明显。

**修复代码（v2）**：
```python
for name in ['上证综指', '深证成指', '创业板指', '科创50']:
    if name not in ma_data_dict: continue
    ma = ma_data_dict[name]
    change_5d = ma['change_5d']
    # 【关键修复】5 日 >= 10% 改为"短期过热"
    if change_5d >= 10 and ma['current'] > ma['ma20']:
        trend = f"短期过热（5日 +{change_5d:.1f}%，警惕回踩）"
    elif change_5d > 0 and ma['current'] > ma['ma20']:
        trend = "震荡偏多"
    else:
        trend = "震荡偏弱"
    report.append(f"### {name}")
    report.append(f"- **基准判断**：{trend}")
```

### 2.4 仓位建议（generate_report 内）：与 2.2 同源

**修复代码（v2）**：
```python
# generate_report() 仓位建议段落
max_5d = 0
if ma_data_dict:
    max_5d = max((m.get('change_5d', 0) for m in ma_data_dict.values()), default=0)

if sentiment < 40:
    report.append("- **建议仓位：30%–50%（偏谨慎）**")
elif max_5d >= 10 and sentiment >= 60:
    # 【关键修复】5 日 >= 10% + 情绪偏热 → 仓位从 50-70% 下调到 40-55%
    report.append(f"- **建议仓位：40%–55%（中性偏上，成长端 5 日 +{max_5d:.1f}% 透支）**")
elif sentiment > 60:
    report.append("- **建议仓位：50%–70%（偏积极）**")
else:
    report.append("- **建议仓位：40%–60%（中性）**")
```

### 2.5 【2026-06-23 实测新增 bug】当日大跌 vs 近 5 日正收益冲突（**v3 修复**）

**问题**：脚本 v1+v2 的趋势研判逻辑只看 `change_5d > 0 and current > ma20`，**没考虑当日大跌对短期情绪的冲击**。6/23 实测：当日沪指 -1.37% / 深成 -3.17% / 创业板 -3.84%，但近 5 日收益 +0.35% / +1.14% / +2.18% **仍为正** —— 脚本仍判"震荡偏多"（**完全反了**），仓位建议 30-50%（**应下调到 30-40%**）。

**【根因】**：v2 修复只关注 5 日透支（5 日 ≥ 10%），但没考虑**当日单日大跌**对短期情绪的冲击。即使 5 日趋势未坏，单日 -2% 以上的跌幅也是强烈的短期偏空信号。

**v3 修复代码**（必须在重写 stock_report.md 时**手动覆盖**，因为脚本无法识别"防御切换信号"）：

```python
def adjust_trend_v3(name, today_change, change_5d, current, ma20):
    """趋势研判 v3：当日跌幅优先于近 5 日收益"""
    # 1. 当日大跌（> -2%）：即使 5 日仍正，也判"震荡偏空"
    if today_change < -2.0:
        if change_5d > 5:
            return "震荡偏空（单日大跌，5日仍正有支撑，但短期情绪转弱）"
        else:
            return "震荡偏空（单日大跌 + 5日疲弱）"
    # 2. 当日小跌（-2% ~ 0）+ 5 日正：判"震荡偏空"（保守）
    elif today_change < 0 and change_5d > 0:
        return "震荡偏空（单日收阴，5日趋势暂未破坏）"
    # 3. 当日平或涨 + 5 日 ≥ 10%（透支）：判"短期过热"（v2 已有）
    elif change_5d >= 10 and current > ma20:
        return f"短期过热（5日 +{change_5d:.1f}%，警惕回踩）"
    # 4. 当日平或涨 + 5 日正 + 站上 MA20：判"震荡偏多"（v1+v2 原逻辑）
    elif change_5d > 0 and current > ma20:
        return "震荡偏多"
    else:
        return "震荡偏弱"


def adjust_position_v3(today_change, change_5d, sentiment, defensive_rotation=False):
    """仓位建议 v3：防御切换信号 + 单日大跌调整"""
    # 1. 单日大跌（< -2%）：仓位下调到 30-40%
    if today_change < -2.0:
        return "30%-40%（下调10pp，偏谨慎）"
    # 2. 防御风格切换（银行/医药领涨 + 资源/科技杀跌）：仓位下调到 30-40%
    elif defensive_rotation:
        return "30%-40%（防御切换，底仓防御为主）"
    # 3. 5 日 ≥ 10% 透支：40-55%（v2 已有）
    elif change_5d >= 10 and sentiment >= 60:
        return f"40%-55%（成长端 5 日 +{change_5d:.1f}% 透支）"
    # 4. 默认 30-50%
    else:
        return "30%-50%（偏谨慎）"
```

**6/23 实测对比**：

| 指数 | 当日 | 5日 | MA20 站上 | v2 判定 | **v3 判定** |
|---|---|---|---|---|---|
| 上证综指 | -1.37% | +0.35% | 是（4067 < 4106） | 震荡偏多 ❌ | **震荡偏空** ✅（单日 -1.37%） |
| 深证成指 | -3.17% | +1.14% | 是（15543 < 15854） | 震荡偏多 ❌ | **震荡偏空** ✅（单日 -3.17%） |
| 创业板指 | -3.84% | +2.18% | 是（4040 < 4192） | 震荡偏多 ❌ | **震荡偏空** ✅（单日 -3.84%） |
| 科创50 | -1.68% | +8.97% | 是（1756 < 1916） | 震荡偏多 ❌ | **震荡偏空** ✅（单日 -1.68%，5日未达透支阈值） |

**仓位 v3**：6/23 当日 -1.37% + 防御切换（银行流入/电子流出）→ 30-40%（从 v2 的 30-50% 下调 10pp）

**【铁律】16:00 周报任务的 Step 1.5 整体重写 stock_report.md 时必须套用 v3 规则**，不能直接信脚本输出。完整流程见 [`references/a-stock-weekly-cron-16oclock.md` §4.1](./a-stock-weekly-cron-16oclock.md)。

---

## 3. 实测验证脚本（离线测试算法）

**用途**：新算法部署后，必须用以下脚本实测验证。**不要等 cron 跑出来再看**。

### 3.1 6-18 数据复现（验证 v2 算法）

```python
# /tmp/verify_report_algo.py
# 复制到脚本同目录运行：python3 verify_report_algo.py

indices = [
    {'name': '上证综指', 'change': -0.43},
    {'name': '深证成指', 'change': 0.94},
    {'name': '创业板指', 'change': 2.05},
    {'name': '科创50',   'change': 3.84},
    {'name': '沪深300',  'change': 0.21},
    {'name': '中证500',  'change': 0.53},
    {'name': '中证1000', 'change': 0.76},
]
ma_data_dict = {
    '上证综指': {'change_5d': 1.46,  'current': 4090.48, 'ma20': 4067.11},
    '深证成指': {'change_5d': 7.13,  'current': 16030.70, 'ma20': 15504.67},
    '创业板指': {'change_5d': 11.02, 'current': 4252.39,  'ma20': 4010.70},
    '科创50':   {'change_5d': 14.93, 'current': 1911.51,  'ma20': 1747.45},
    '沪深300':  {'change_5d': 3.44,  'current': 4941.60,  'ma20': 4863.05},
    '中证500':  {'change_5d': 6.99,  'current': 8673.09,  'ma20': 8375.96},
    '中证1000': {'change_5d': 6.93,  'current': 8771.02,  'ma20': 8465.00},
}

# 模拟 v2 算法（复制自修复后的脚本）
def get_sentiment_score_v2(indices, ma_data_dict):
    avg_change = sum(i['change'] for i in indices) / len(indices)
    if avg_change > 1: base = 70
    elif avg_change > 0: base = 60
    elif avg_change > -1: base = 45
    else: base = 30
    for growth_name in ('创业板指', '科创50'):
        if growth_name in ma_data_dict:
            change_5d = ma_data_dict[growth_name].get('change_5d', 0)
            if change_5d > 10: base += 10
            elif change_5d > 5: base += 5
    max_5d = max((m.get('change_5d', 0) for m in ma_data_dict.values()), default=0)
    if max_5d >= 12: base = min(base, 88)
    elif max_5d >= 10: base = min(base, 85)
    elif max_5d >= 8: base = min(base, 80)
    return max(10, min(90, base))

sentiment = get_sentiment_score_v2(indices, ma_data_dict)
print(f"情绪温度计: {sentiment}/100 (期望 88)")

# 期望输出: 情绪温度计: 88/100 (期望 88)
```

### 3.2 验证期望值

| 指标 | 期望值 | 修复前值 | 修复后值 |
|---|---|---|---|
| 情绪温度计（6/18 数据） | **88**（极度贪婪） | 80（偏热） | **88** ✅ |
| 仓位建议（6/18 数据） | **40-55%**（中性偏上） | 50-70%（偏积极） | **40-55%** ✅ |
| 创业板趋势研判 | **短期过热**（5日 +11%） | 震荡偏多 | **短期过热** ✅ |
| 科创50趋势研判 | **短期过热**（5日 +14.9%） | 震荡偏多 | **短期过热** ✅ |

### 3.3 其他典型场景测试用例

```python
# 用例 1：温和上涨（5 日 < 8%，应判中性偏积极）
test_温和 = {
    'indices': [{'name': '上证综指', 'change': 0.5}, ...],
    'ma_data_dict': {'上证综指': {'change_5d': 5.0, ...}, ...}
}
# 期望：sentiment ≈ 60-65 (中性偏热)

# 用例 2：单日大跌（应判冷/恐慌）
test_大跌 = {
    'indices': [{'name': '上证综指', 'change': -2.5}, ...],
    'ma_data_dict': {'上证综指': {'change_5d': -5.0, ...}, ...}
}
# 期望：sentiment ≈ 20-30 (偏冷)

# 用例 3：极端透支（5 日 > 15%，应判 88 上限）
test_极端 = {
    'indices': [{'name': '上证综指', 'change': 2.0}, ...],
    'ma_data_dict': {'上证综指': {'change_5d': 15.5, ...}, ...}
}
# 期望：sentiment ≤ 88 (极度贪婪上限)
```

---

## 4. 数据接口 fallback 链（待实现）

`get_industry_data()` / `get_capital_flow_data()` 当前只走 akshare 一个接口。**已知 akshare 连续 3 天限流**（2026-06-16/17/18 实测），限流时无 fallback 导致行业数据缺失。

### 4.1 建议的 fallback 顺序（按成功概率排序）

```python
def get_industry_data_with_fallback(self):
    """行业板块数据获取（akshare → 新浪 → 同花顺 → 东财 → 浏览器抓取）"""
    # 1. akshare (首选)
    try:
        df = ak.stock_board_industry_name_em()
        if df is not None and len(df) > 0:
            return df[['名称', '最新价', '涨跌幅']].head(20)
    except: pass

    # 2. 新浪行业接口 (limit 5 QPS, 一般可用)
    try:
        # 调用 web_fetch / curl 抓取 http://vip.stock.finance.sina.com.cn/...
        ...
    except: pass

    # 3. 同花顺接口 (有反爬)
    try:
        # q.10jqka.com.cn/thsft/api/v1/...
        ...
    except: pass

    # 4. 东财 (限流严格, 必须 em_get() 限流 ≥ 1 秒)
    try:
        # push2.eastmoney.com/api/qt/clist/get?fs=m:90+t:2
        ...
    except: pass

    # 5. 浏览器抓取（最后 fallback, agent 用 vision_analyze）
    # 通过 web_search 搜 "[日期] A股行业板块涨跌幅" 取第一段文字
    # ⚠️ 必须明确标注数据来源 + 时延

    return None  # 所有 fallback 都失败
```

### 4.2 fallback 失败时报告的写法

**绝对禁止**写"结构性行情明显"等无数据支撑的方向性结论。**应该写**：

```markdown
### 结构与广度（行业板块样本 — ⚠️ 数据缺失）
- **【数据缺失】** akshare / 新浪 / 同花顺 / 东财 多个接口连续 3 天限流，X-XX 行业板块数据未获取。
- **【延续参考】** X-YY 行业主线（来源：daily_report_X-YY.md）：商业航天、光模块、人形机器人。**注：数据已失效 N 天，不建议直接套用。**
- **建议**：用户可参考 Wind / Choice 或东方财富 APP 盘后数据（一般 18:00-20:00 更新）。
```

### 4.3 数据源已知问题（2026-06-19 实测）

| 数据源 | 接口 | 限流情况 | 备注 |
|---|---|---|---|
| akshare `stock_board_industry_name_em` | HTTP | **连续 3 天限流** | 6/18 直接返回 None |
| 新浪 `vip.stock.finance.sina.com.cn` | HTTP | `Service not valid` 错误 | 6/19 实测失败 |
| 东财 `push2.eastmoney.com` | HTTPS | **直接空响应**（IP 被屏蔽？） | 6/19 实测失败 |
| 东财 `msearch.eastmoney.com` | HTTPS | 未实测 | 可能可用 |
| 同花顺 `q.10jqka.com.cn` | HTTPS | 未实测 | 有反爬 |
| Bing / Google search | HTTPS | 搜索引擎被屏蔽 | 6/19 curl 无返回 |

---

## 5. cron 任务 prompt 模板（建议增加硬约束）

当前 cron 任务 prompt（hermes cron `A股策略周报 - 交易日16:00`）未明确"数据缺失时如何处理"。建议追加：

```markdown
## 【硬约束】数据缺失时禁止给方向性结论

**核心规则（用户 first-class preference）**：
1. 如果 `get_industry_data()` / `get_capital_flow_data()` 返回空或 None，**报告中严禁写"结构性行情明显"/"成长强于价值"等定性描述**。
2. 必须在报告相应章节明确标 "⚠️ 数据缺失" + 缺失原因 + 接口名 + 用户可查的替代源。
3. 如果数据缺失时仍发 IM 摘要，IM 里**只列指数和市场特征**，**不重复报告里的方向性结论**。
4. 数据补全的 fallback 顺序：akshare → 新浪 → 同花顺 → 东财 → web_search（如 hermes web_search 可用）。

## 【硬约束】算法修复必须用验证脚本

修复 `daily_report_v2.py` 后，**必须**先用 `references/a-stock-report-algorithm-pitfalls.md` §3 的验证脚本离线测试，**再部署到 cron**。
```

---

## 6. 修复版报告范本（参考）

2026-06-19 修复的 6-18 报告是首个完全符合 §2.5 三条铁律的范本：

| 章节 | 原报告（违反铁律） | 修复版（符合铁律） |
|---|---|---|
| §1 结构与广度 | "行业数据获取失败" | "**【数据缺失】** akshare 限流，未获取 6/18 行业数据" |
| §1 结构与广度 | （无后续说明） | "**【延续参考】** 6/17 主线：商业航天/光模块/机器人（注：数据已失效 2 天）" |
| §2 行业主线 | "今日行业表现显示..."（无数据） | "**【数据声明】** 本节不给出行业方向性判断。仅基于已有指数数据做客观陈述" |
| §2 风格判断 | "科创50(+3.84%) 远强于沪深300"（隐含方向性） | "成长 vs 价值：科创50 远强于沪深300（**指数层事实，非方向性判断**）" |
| §3 情绪温度计 | 80/100（偏热） | **88/100（极度贪婪/严重过热）**（带修复说明） |
| §5 仓位建议 | 50%-70%（偏积极） | **40%-55%（中性偏上，成长端 5 日 +14.9% 透支）**（带修复说明） |

**结论摘要**也要明示数据缺失：
> 1. 市场整体震荡偏多，但成长端已严重透支
> 6. **6-17 行业主线作为延续参考，但数据已失效 2 天，不建议直接套用**
> 9. **资金面数据 6-18 缺失，建议用户用 Wind/Choice 盘后数据补齐**

---

## 7. 完整修复 checklist（部署新算法时必走）

每次修改 `daily_report_v2.py` 的算法时，按顺序检查：

- [ ] 1. 在 openclaw 主目录修改 `daily_report_v2.py`
- [ ] 2. 同步到 tyTools 备份：`cp openclaw/daily_report_v2.py tyTools/`
- [ ] 3. `md5 openclaw/daily_report_v2.py tyTools/daily_report_v2.py` 验证一致
- [ ] 4. 用本文件 §3.1 验证脚本测试，至少 3 个典型场景
- [ ] 5. 跑一次完整流水线：cd tyTools && openclaw_venv python3 daily_report_v2.py
- [ ] 6. 检查生成的 `stock_report.md` 情绪温度计 / 仓位建议 / 趋势研判是否合理
- [ ] 7. 写一条 IM 摘要（不投递，只验证内容）
- [ ] 8. 归档到 `daily_report/daily_report_YYYY-MM-DD.md`
- [ ] 9. 同步更新本文件 references/（如有新算法/新坑）
- [ ] 10. 更新 memory + skill §6.12（保持 skill 是最新的）

---

## 8. 相关文件路径

| 文件 | 路径 | 用途 |
|---|---|---|
| 主脚本 | `/Users/taoyi/.openclaw/workspace-stockTodayAnalysis/daily_report_v2.py` | venv 跑这个 |
| 备份脚本 | `/Users/taoyi/gitProjects/GitHub/tyTools/daily_report_v2.py` | git 备份 + 其他工作目录调用 |
| 报告源文件 | `/Users/taoyi/gitProjects/GitHub/tyTools/stock_report.md` | 写入飞书前的中转 |
| 归档目录 | `/Users/taoyi/.openclaw/workspace-stockTodayAnalysis/daily_report/` | 历史报告 |
| 修复版 6/18 报告 | `daily_report/daily_report_2026-06-18.md` | 范本（§6） |
| 验证脚本 | `/tmp/verify_report_algo.py`（临时） | 离线测试 |
| Skill 主文件 | `~/.hermes/skills/productivity/lark-stock-report/SKILL.md` | 本 skill 主入口 |
| Skill §6.12 | SKILL.md §6 已知坑第 12 条 | 简版修复记录 |
