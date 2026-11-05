# 多数据源交叉验证体系

## 模块五：多数据源交叉验证体系

### 功能描述

通过多个免费数据源交叉验证，确保数据的可靠性和准确性。

---

## 免费数据源汇总

| 市场 | 数据类型 | 数据源1 | 数据源2 | 数据源3 | 备注 |
|------|----------|---------|---------|---------|------|
| **A股** | 实时价格 | Baostock | akshare | 新浪财经 | Baostock无需注册,最稳定 |
| **A股** | 日线数据 | Baostock | akshare | - | - |
| **A股** | 分钟数据 | Baostock | akshare | - | - |
| **A股** | 财务数据 | Baostock | akshare | 同花顺 | Baostock最全面 |
| **A股** | 个股资料 | Baostock | akshare | 东方财富 | - |
| **港股** | 实时价格 | akshare | 港交所 | - | - |
| **港股** | 日线数据 | akshare | - | - | - |
| **港股** | 财务数据 | akshare | - | - | - |
| **美股** | 实时价格 | akshare | Yahoo Finance | - | - |
| **美股** | 日线数据 | akshare | - | - | - |
| **美股** | 基本面 | Yahoo Finance | - | - | - |

---

## 交叉验证流程

```
┌─────────────────────────────────────────────────────────────┐
│                      数据获取                                │
├─────────────────────────────────────────────────────────────┤
│  源1: Baostock  ──┐                                         │
│                    ├──> 交叉验证 ──> 数据融合 ──> 输出       │
│  源2: akshare  ───┘         │                               │
│                               │                              │
│  源3: 新浪财经  ─────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 验证规则

### 1. 数据一致性检查

```python
def validate_data_consistency(data_sources):
    """
    检查多个数据源的数据一致性

    规则:
    - 如果差异 < 1%, 以Baostock为准
    - 如果差异 1%-5%, 取平均值并标注
    - 如果差异 > 5%, 需人工确认
    """
    results = []

    for key in common_keys:
        values = [ds[key] for ds in data_sources if key in ds]
        if not values:
            continue

        avg = sum(values) / len(values)
        max_diff = max(values) - min(values)
        max_diff_pct = max_diff / avg * 100

        if max_diff_pct < 1:
            validated_value = values[0]  # Baostock优先
            status = "CONSISTENT"
        elif max_diff_pct < 5:
            validated_value = avg
            status = "MINOR_DIFF"
        else:
            validated_value = avg
            status = "MAJOR_DIFF"

        results.append({
            "key": key,
            "values": values,
            "validated": validated_value,
            "diff_pct": max_diff_pct,
            "status": status
        })

    return results
```

### 2. 异常值检测

```python
def detect_outliers(values, threshold=3):
    """
    使用Z-score方法检测异常值

    规则:
    - Z-score > 3 视为异常
    - 异常值剔除后重新计算
    """
    import statistics

    if len(values) < 3:
        return values, []

    mean = statistics.mean(values)
    stdev = statistics.stdev(values)

    outliers = []
    valid_values = []

    for v in values:
        z_score = abs((v - mean) / stdev) if stdev > 0 else 0
        if z_score > threshold:
            outliers.append(v)
        else:
            valid_values.append(v)

    if outliers:
        # 用有效值均值替代异常值
        validated = statistics.mean(valid_values) if valid_values else mean
    else:
        validated = mean

    return validated, outliers
```

### 3. 时效性检查

```python
def check_data_freshness(data, market="A"):
    """
    检查数据时效性

    A股:
    - 交易时段: 9:30-15:00
    - 日线数据更新: 16:00-17:00

    港股:
    - 交易时段: 9:30-12:00, 13:00-16:00
    - 日线数据更新: 17:00左右

    美股:
    - 交易时段: 21:30-次日4:00(夏令时)
    - 日线数据更新: 次日5:00左右
    """
    from datetime import datetime, time

    now = datetime.now()
    current_time = now.time()

    if market == "A":
        market_open = time(9, 30)
        market_close = time(15, 0)
        daily_update = time(16, 0)
    elif market == "HK":
        market_open = time(9, 30)
        market_close = time(16, 0)
        daily_update = time(17, 0)
    elif market == "US":
        market_open = time(21, 30)
        market_close = time(4, 0)
        daily_update = time(5, 0)

    # 检查数据日期
    if data.get("date"):
        data_date = data["date"]
        if data_date == now.date():
            freshness = "🟢 最新"
        elif data_date == (now - timedelta(days=1)).date():
            freshness = "🟡 昨日"
        else:
            freshness = "🔴 过期"
    else:
        freshness = "未知"

    return freshness
```

---

## 数据源优先级

### A股数据源优先级

| 数据类型 | 第一优先 | 第二优先 | 第三优先 |
|----------|----------|----------|----------|
| 实时价格 | Baostock | akshare | 新浪财经 |
| 日线数据 | Baostock | akshare | - |
| 分钟数据 | Baostock | akshare | - |
| 财务数据 | Baostock | akshare | 同花顺 |
| 基本面 | Baostock | akshare | 公司公告 |
| 估值指标 | Baostock | akshare | 东方财富 |
| 股东信息 | Baostock | - | - |
| 机构持仓 | 基金季报 | 上市公司公告 | - |

### 港股数据源优先级

| 数据类型 | 第一优先 | 第二优先 |
|----------|----------|----------|
| 实时价格 | akshare | 港交所 |
| 日线数据 | akshare | - |
| 财务数据 | akshare | - |
| 基本面 | akshare | 港交所 |

### 美股数据源优先级

| 数据类型 | 第一优先 | 第二优先 |
|----------|----------|----------|
| 实时价格 | akshare | Yahoo Finance |
| 日线数据 | akshare | - |
| 基本面 | Yahoo Finance | - |

---

## 数据融合策略

### 简单平均法

```python
def simple_average(values):
    """简单平均"""
    return sum(values) / len(values)
```

### 加权平均法

```python
def weighted_average(values, weights):
    """加权平均"""
    return sum(v * w for v, w in zip(values, weights))

# 示例权重
weights = {
    "baostock": 0.5,
    "akshare": 0.3,
    "sina": 0.2
}
```

### 中位数法

```python
def median_value(values):
    """取中位数,抗异常"""
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 0:
        return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
    else:
        return sorted_values[n//2]
```

---

## 验证报告模板

```markdown
# 数据交叉验证报告

验证时间: YYYY-MM-DD HH:mm:ss
股票代码: XXXXXX
股票名称: XXXXXX

---

## 验证摘要

| 数据类型 | 数据源数 | 差异率 | 验证状态 |
|----------|----------|--------|----------|
| 实时价格 | 3 | 0.2% | 🟢 通过 |
| 日线数据 | 2 | 0.1% | 🟢 通过 |
| 财务数据 | 2 | 0.5% | 🟢 通过 |

---

## 详细验证结果

### 1. 实时价格验证

| 数据源 | 最新价格 | 更新时间 |
|--------|----------|----------|
| Baostock | ¥72.50 | 15:00:05 |
| akshare | ¥72.48 | 15:00:08 |
| 新浪财经 | ¥72.52 | 15:00:03 |

**验证结论**: 🟢 通过
**融合结果**: ¥72.50 (Baostock优先)

### 2. PE验证

| 数据源 | PE(TTM) | PE(预期) |
|--------|----------|----------|
| Baostock | 28.5 | 24.2 |
| akshare | 28.6 | 24.3 |

**验证结论**: 🟢 通过
**融合结果**: PE_TTM=28.5, PE_Forward=24.2

### 3. 财务数据验证

| 指标 | Baostock | akshare | 差异 |
|------|----------|---------|------|
| 营收(亿) | 3456.78 | 3456.80 | 0.002% |
| 净利(亿) | 298.56 | 298.55 | 0.003% |
| 毛利率 | 26.5% | 26.5% | 0% |

**验证结论**: 🟢 通过
**融合结果**: 使用Baostock数据

---

## 数据质量评估

### 综合评分
| 维度 | 评分 |
|------|------|
| 完整性 | 100分 |
| 一致性 | 98分 |
| 时效性 | 95分 |
| **综合质量** | **97分** |

### 建议
- 数据质量良好,可用于分析
- 建议持续关注数据更新情况

---

## 数据异常记录

| 日期 | 数据类型 | 异常描述 | 处理方式 |
|------|----------|----------|----------|
| - | - | 无异常 | - |
```

---

## 常见问题处理

### 1. 数据源不可用

```python
def handle_source_unavailable(source_name, required_data):
    """
    当数据源不可用时的处理策略

    降级方案:
    1. 尝试备用数据源
    2. 使用最近一次的有效数据
    3. 标注数据可能不准确
    """
    alternatives = {
        "baostock": ["akshare", "sina"],
        "akshare": ["baostock"],
        "sina": ["baostock", "akshare"]
    }

    for alt in alternatives.get(source_name, []):
        if alt_available(alt):
            return fetch_from_source(alt, required_data)

    # 所有源都不可用
    return None, "ALL_SOURCES_UNAVAILABLE"
```

### 2. 数据格式不一致

```python
def normalize_data_format(data, target_format):
    """
    统一数据格式

    日期格式统一: YYYY-MM-DD
    数字格式统一: 保留2位小数
    代码格式统一: 市场前缀+代码
    """
    normalized = {}

    for key, value in data.items():
        if "date" in key.lower():
            normalized[key] = normalize_date(value)
        elif isinstance(value, (int, float)):
            normalized[key] = round(value, 2)
        elif "code" in key.lower():
            normalized[key] = normalize_stock_code(value)
        else:
            normalized[key] = value

    return normalized
```

### 3. 数据延迟处理

```python
def handle_data_delay(source_name, market):
    """
    处理数据延迟情况

    规则:
    - A股盘中: 使用前一交易日数据
    - 非交易时段: 提示数据可能未更新
    """
    if market == "A" and is_trading_hours():
        return "USE_PREVIOUS_DATA"
    elif not is_trading_hours():
        return "DATA_MAY_NOT_UPDATE"
```

---

## API调用示例

### Baostock 多数据获取

```python
import baostock as bs

# 登录
lg = bs.login()

# 获取日线数据
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,code,open,high,low,close,volume",
    start_date='2024-01-01',
    end_date='2024-12-31',
    frequency="d"
)

# 获取财务数据
rs = bs.query_profit_data(
    code="sh.600519",
    year=2024,
    quarter=4
)

# 获取指标数据
rs = bs.query_dualfactor_data(
    code="sh.600519",
    date='2024-12-31'
)

# 登出
bs.logout()
```

### akshare 多数据获取

```python
import akshare as ak

# 实时行情
df = ak.stock_zh_a_spot_em()

# 历史行情
df = ak.stock_zh_a_hist(
    symbol="000333",
    period="daily",
    start_date="20240101",
    end_date="20241231"
)

# 财务指标
df = ak.stock_financial_analysis_indicator(
    symbol="000333",
    start_year="2022"
)
```

---

## 验证日志

### 日志格式

```json
{
  "log_id": "vld_20260412_001",
  "timestamp": "2026-04-12T15:00:05",
  "stock_code": "000333.SZ",
  "data_type": "realtime_price",
  "sources_checked": ["baostock", "akshare", "sina"],
  "validation_result": {
    "baostock": 72.50,
    "akshare": 72.48,
    "sina": 72.52
  },
  "max_diff_pct": 0.55,
  "final_value": 72.50,
  "status": "PASS"
}
```

---

## 监控告警

### 告警规则

| 告警类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| 数据中断 | 某源连续3次获取失败 | 切换备用源 |
| 数据差异大 | 差异>10% | 人工确认 |
| 数据超时 | 获取耗时>30秒 | 降级处理 |
| 源不可用 | 连续5次不可用 | 标记为不可用 |

### 告警通知

```python
def send_alert(alert_type, message):
    """
    发送告警通知

    渠道:
    - 邮件通知
    - 即时消息
    - 日志记录
    """
    alert = {
        "type": alert_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "severity": "HIGH" if alert_type in ["数据中断", "数据差异大"] else "MEDIUM"
    }

    # 发送邮件
    send_email(alert)

    # 发送消息
    send_im(alert)

    # 记录日志
    log_alert(alert)
```
