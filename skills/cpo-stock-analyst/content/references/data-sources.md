# 数据源配置参考（v3.5增强版）

## 核心原则

**重要**: 每次生成分析报告前，必须先获取实时数据！使用实时数据源替代历史收盘数据。

---

## 实时数据获取方法

### 1. AKShare（推荐 - 实时+历史）

AKShare是最佳的数据获取方案，提供实时行情和历史数据。

```python
import akshare as ak

# ==================== 实时行情接口 ====================

# 获取全市场实时行情（含所有A股）
df = ak.stock_zh_a_spot_em()
# 返回：代码、名称、最新价、涨跌幅、成交量、成交额、市值等

# 获取上证指数实时数据
df = ak.stock_individual_spot_xq(symbol="SH000001")
# 返回：实时点位、涨跌幅、成交量等

# 获取深证成指实时数据
df = ak.stock_individual_spot_xq(symbol="SZ399001")

# 获取创业板实时数据
df = ak.stock_individual_spot_xq(symbol="SZ399006")

# 获取科创50实时数据
df = ak.stock_individual_spot_xq(symbol="SH000688")

# 获取沪深300实时数据
df = ak.stock_individual_spot_xq(symbol="SH000300")

# ==================== 指数实时行情 ====================

# 获取所有指数实时行情
df = ak.stock_zh_index_spot_em()
# 返回：指数代码、名称、点位、涨跌幅等

# ==================== 分时数据（盘中实时） ====================

# 获取上证1分钟分时数据
df = ak.stock_zh_a_minute(symbol='sh000001', period='1')

# 获取上证5分钟分时数据
df = ak.stock_zh_a_minute(symbol='sh000001', period='5')

# ==================== 行业板块实时 ====================

# 获取行业板块实时行情
df = ak.stock_board_industry_name_em()
# 返回：板块名称、涨跌幅、资金流向等

# ==================== ETF实时行情 ====================

# 获取ETF实时数据
df = ak.stock_zh_a_spot_em()  # 筛选ETF
# 或使用东方财富接口

# ==================== 历史数据（用于技术分析） ====================

# 获取指数日线数据
df = ak.stock_zh_index_daily(symbol="sh000001", start_date="20260101", end_date="20260408")

# 获取股票日线数据（前复权）
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260101", end_date="20260408", adjust="qfq")
```

### 2. 新浪财经接口（实时）

```python
# 实时行情API
# 指数实时: https://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688

# 返回格式
# var hq_str_sh000001="上证指数,3948.495,1.50,58.47,5650000,...";

# 解析方式
import requests

def get_sina_realtime(codes):
    """获取新浪实时行情"""
    url = f"https://hq.sinajs.cn/list={codes}"
    headers = {"Referer": "https://finance.sina.com.cn"}
    response = requests.get(url, headers=headers)
    return response.text

# 示例
codes = "sh000001,sz399001,sz399006,sh000688,sz159915,sh512480"
data = get_sina_realtime(codes)
```

### 3. 东方财富接口（实时+资金流）

```python
# 实时行情（东方财富）
# http://push2.eastmoney.com/api/qt/clist/get

# 北向资金实时
# http://push2.eastmoney.com/api/qt/kamt.rtmin/get

# 龙虎榜数据
# http://push2.eastmoney.com/api/qt/clist/get?fid=f62&po=1&pz=20&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A90+t%3A2&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205
```

---

## 数据源优先级配置（v3.4）

```python
DATA_SOURCE_PRIORITY = {
    # ===== 实时数据（盘中必须使用） =====
    "realtime": {
        1: {
            "name": "AKShare",
            "api": "stock_individual_spot_xq",
            "reliability": 0.95,
            "usage": "获取个股/指数实时行情",
            "note": "盘中必用，支持上证、深证、创业板、科创50"
        },
        2: {
            "name": "AKShare全市场",
            "api": "stock_zh_a_spot_em",
            "reliability": 0.90,
            "usage": "获取全市场实时行情快照"
        },
        3: {
            "name": "新浪财经",
            "api": "hq.sinajs.cn",
            "reliability": 0.85,
            "usage": "备用实时数据源"
        }
    },

    # ===== 历史数据（用于技术分析） =====
    "historical": {
        1: {
            "name": "AKShare",
            "api": "stock_zh_index_daily",
            "reliability": 0.95,
            "usage": "指数日线数据"
        },
        2: {
            "name": "AKShare",
            "api": "stock_zh_a_hist",
            "reliability": 0.90,
            "usage": "个股日线数据"
        },
        3: {
            "name": "MCP接口",
            "api": "stocks_price",
            "reliability": 0.85,
            "usage": "历史日线回补"
        }
    },

    # ===== 资金流数据 =====
    "capital_flow": {
        1: {
            "name": "东方财富",
            "api": "push2.eastmoney.com",
            "reliability": 0.90,
            "usage": "北向资金、融资融券"
        },
        2: {
            "name": "AKShare",
            "api": "stock_money_flow",
            "reliability": 0.85
        }
    },

    # ===== 基本面数据 =====
    "fundamentals": {
        1: {
            "name": "东方财富",
            "api": "eastmoney",
            "reliability": 0.90
        },
        2: {
            "name": "Tushare",
            "api": "pro_api",
            "reliability": 0.95,
            "note": "需要Token和积分"
        }
    }
}
```

---

## 数据获取工作流程（必须遵循）

### 分析报告数据获取流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    数据获取工作流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  第1步: 获取实时行情数据（盘中必须）                               │
│  ├── 方法: AKShare stock_individual_spot_xq()                    │
│  ├── 获取: 上证、深证、创业板、科创50点位和涨跌幅                  │
│  └── 获取: 热门ETF实时价格                                       │
│                                                                 │
│  第2步: 获取市场整体数据                                         │
│  ├── 方法: AKShare stock_zh_a_spot_em()                         │
│  ├── 获取: 涨跌家数、成交额、涨跌停数量                           │
│  └── 获取: 行业板块涨跌排行                                      │
│                                                                 │
│  第3步: 获取历史数据（用于技术分析）                              │
│  ├── 方法: AKShare stock_zh_index_daily()                       │
│  ├── 获取: 近60日日线数据                                       │
│  └── 计算: 均线、MACD、KDJ等技术指标                            │
│                                                                 │
│  第4步: 获取资金流向数据                                         │
│  ├── 方法: 东方财富北向资金接口                                  │
│  └── 获取: 北向资金净流入、融资融券余额                          │
│                                                                 │
│  第5步: 数据校验与标记                                          │
│  ├── 验证: 实时数据与历史数据一致性                              │
│  ├── 标记: 虚拟数据/推测数据置信度                               │
│  └── 输出: 数据完整性报告                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 数据更新策略

```python
UPDATE_STRATEGY = {
    # ===== 实时数据（盘中） =====
    "realtime_data": {
        "frequency": "盘中每5分钟",
        "sources": ["AKShare", "新浪财经"],
        "priority": "AKShare优先"
    },

    # ===== 日线数据（收盘后） =====
    "daily_data": {
        "frequency": "每日16:00后",
        "time": "16:00-17:00",
        "retry": 3,
        "sources": ["AKShare", "MCP接口"]
    },

    # ===== 资金流数据 =====
    "capital_flow": {
        "frequency": "盘中每小时",
        "sources": ["东方财富", "AKShare"]
    },

    # ===== 基本面数据 =====
    "fundamental_data": {
        "frequency": "每周日02:00",
        "sources": ["Tushare", "东方财富"]
    }
}
```

---

## 数据质量控制

```python
DATA_QUALITY_CONTROL = {
    # 实时数据校验
    "realtime_checks": {
        "price_change_range": [-10, 10],  # 涨跌幅合理范围
        "min_volume": 0,
        "max_update_age": 300  # 数据更新不超过5分钟
    },

    # 历史数据校验
    "historical_checks": {
        "high_low_logic": "high >= close >= low",
        "volume_positive": "volume > 0",
        "price_change_calc": "close - pre_close"
    },

    # 置信度评估
    "confidence_levels": {
        "realtime": 0.95,      # 实时数据高置信度
        "estimated": 0.80,       # 盘中推测数据
        "historical": 0.90,     # 历史数据
        "virtual": 0.60         # 虚拟数据（节假日等）
    }
}
```

---

## 常见问题处理

### Q1: 实时数据获取失败怎么办？
```
1. 切换备用数据源（新浪财经 → 东方财富）
2. 使用MCP接口回补T-1日数据
3. 标记数据来源，评估置信度
```

### Q2: 盘中如何估算涨跌家数？
```
方法: 使用AKShare全市场数据统计
df = ak.stock_zh_a_spot_em()
up_count = len(df[df['涨跌幅'] > 0])
down_count = len(df[df['涨跌幅'] < 0])
```

### Q3: 非交易时间如何获取数据？
```
1. 交易时间内（9:30-15:00）: 使用实时接口
2. 收盘后: 使用当日收盘数据
3. 节假日前: 使用最后交易日数据
4. 标记数据时效性
```

---

## 快速参考表

| 数据需求 | 推荐接口 | 置信度 |
|---------|---------|--------|
| 上证实时点位 | `stock_individual_spot_xq("SH000001")` | 95% |
| 深证实时点位 | `stock_individual_spot_xq("SZ399001")` | 95% |
| 创业板实时 | `stock_individual_spot_xq("SZ399006")` | 95% |
| 全市场快照 | `stock_zh_a_spot_em()` | 90% |
| 指数日线 | `stock_zh_index_daily()` | 90% |
| 板块行情 | `stock_board_industry_name_em()` | 85% |
| 历史日线 | `stock_zh_a_hist()` | 90% |
