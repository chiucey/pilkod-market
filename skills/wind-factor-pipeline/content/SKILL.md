---
name: wind-factor-pipeline
description: WindPy驱动的全自动量化选股因子计算Pipeline。当用户要求使用Wind进行量化选股、因子计算（龙虎榜/主力资金/涨停封板/题材热度/相对强弱/换手率）、截面打分排名、候选股筛选、复盘追踪时使用。
---

# WindPy 量化因子计算 Pipeline

全自动因子计算与选股系统，基于 WindPy 数据接口。

## 核心流程

```
WindPy 数据拉取 → 因子计算模块 → 截面打分与排名 → 候选股输出 → 复盘记录
```

## 使用方式

### 1. 初始化环境

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from WindPy import w

w.start()
trade_date = datetime.today().strftime('%Y-%m-%d')
```

### 2. 获取股票池（过滤ST/停牌）

```python
def get_universe(date: str) -> list[str]:
    """获取当日全A可交易股票池"""
    res = w.wset("sectorconstituent",
                 f"date={date};sectorid=a001010100000000")
    df = pd.DataFrame(res.Data, index=res.Fields).T
    codes = df['wind_code'].tolist()

    # 过滤ST
    st_res = w.wss(codes, "sec_status", f"tradeDate={date}")
    st_df = pd.DataFrame({'code': codes, 'status': st_res.Data[0]})
    clean = st_df[st_df['status'] == '正常上市']['code'].tolist()
    return clean
```

### 3. 因子计算模块

| 因子 | 函数 | 描述 |
|------|------|------|
| 龙虎榜因子 | `get_lhb_factor()` | (机构/游资买入-卖出)/总成交额 |
| 主力资金因子 | `get_moneyflow_factor()` | (超大单+大单净流入)/总成交额 |
| 涨停封板因子 | `get_limitup_factor()` | 封单金额/当日成交额 |
| 题材热度因子 | `get_sector_heat_factor()` | 个股所属题材涨停数/题材总股票数 |
| 相对强弱因子 | `get_relative_strength_factor()` | 个股涨跌幅-行业指数涨跌幅 |
| 换手率因子 | `get_turnover_factor()` | 高斯函数模拟黄金区间(2%-8%) |

### 4. 综合评分

```python
def cross_section_score(date: str) -> pd.DataFrame:
    """主函数：计算当日截面综合得分"""
    universe = get_universe(date)

    # 计算各因子并标准化（百分位排名）
    df_ranked = df.rank(pct=True)

    # 加权合成
    weights = {
        'lhb': 0.20,
        'moneyflow': 0.15,
        'limitup': 0.10,
        'sector': 0.20,
        'rs': 0.15,
        'turnover': 0.10,
    }

    # 筛选条件：综合得分前5% + 市值>20亿
    candidates = df[df['score_pct'] >= 0.95 & (df['mktcap'] >= 20)]
    return candidates
```

### 5. 复盘追踪

```python
def record_performance(date: str, candidates: pd.DataFrame):
    """T日选股 → T+1至T+5日超额收益追踪"""
    # 计算组合收益 vs 全A等权基准
    excess = port_return - bench_return
    # 保存到 factor_performance_log.csv
```

## 一键运行

```python
if __name__ == "__main__":
    date = datetime.today().strftime('%Y-%m-%d')
    candidates = cross_section_score(date)
    record_performance(date, candidates)
    w.stop()
```

## 参考资料

完整代码请参考 `references/factor_pipeline.py`
