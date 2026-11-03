# 多数据源交叉验证体系

## 模块五：多数据源交叉验证体系

### 功能描述

通过多个免费数据源交叉验证，确保数据的可靠性和准确性。

---

## 免费数据源汇总

| 市场 | 数据类型 | 数据源1 | 数据源2 | 数据源3 | 备注 |
|------|----------|---------|---------|---------|------|
| **A股** | 实时价格 | Baostock | akshare | 腾讯财经 | Baostock无需注册,最稳定 |
| **A股** | 财务数据 | Baostock | akshare | 东方财富 | 年报/季报,分红,杜邦分析 |
| **A股** | 技术指标 | Baostock | akshare | 东方财富 | K线/均线 |
| **港股** | 实时价格 | akshare | AASTOCKS | 腾讯财经 | 需代码转换 |
| **港股** | 财务数据 | akshare | 东方财富 | AASTOCKS | - |
| **全局** | 宏观数据 | akshare | 国家统计局API | 美联储FRED | - |
| **全局** | 舆情数据 | 雪球 | 东财股吧 | 同花顺 | 需第三方接口 |

> ⚠️ **重要提示**: 港股数据请优先使用akshare、腾讯财经或其他国内可访问源

---

## 数据源优先级配置

```python
MARKET_CONFIG = {
    "A股": {
        "实时价格": {
            "primary": {"source": "baostock", "weight": 0.5},
            "backup": [
                {"source": "akshare", "weight": 0.3},
                {"source": "tencent", "weight": 0.2}
            ]
        },
        "财务数据": {
            "primary": {"source": "baostock", "weight": 0.5},
            "backup": [
                {"source": "akshare", "weight": 0.3},
                {"source": "eastmoney", "weight": 0.2}
            ]
        },
        "技术指标": {
            "primary": {"source": "baostock", "weight": 0.5},
            "backup": [
                {"source": "akshare", "weight": 0.5}
            ]
        }
    },
    "港股": {
        "实时价格": {
            "primary": {"source": "akshare", "weight": 0.4},
            "backup": [
                {"source": "aastocks", "weight": 0.25},
                {"source": "tencent", "weight": 0.2},
                {"source": "eastmoney", "weight": 0.15}
            ]
        },
        "财务数据": {
            "primary": {"source": "akshare", "weight": 0.5},
            "backup": [
                {"source": "eastmoney", "weight": 0.3},
                {"source": "aastocks", "weight": 0.2}
            ]
        }
    }
}
```

---

## 交叉验证算法

```python
class CrossValidator:

    # 价格差异阈值
    DIFF_THRESHOLDS = {
        "price": 0.005,      # 价格差异>0.5%标记
        "volume": 0.10,       # 成交量差异>10%标记
        "financial": 0.01,    # 财务数据差异>1%标记
        "ratio": 0.05         # 比率类差异>5%标记
    }

    def validate_price(self, prices: dict) -> dict:
        """
        价格交叉验证
        prices格式: {"baostock": 1856.0, "akshare": 1855.8}
        返回: 验证结果、最优价格、数据质量评分
        """
        values = list(prices.values())
        mean = sum(values) / len(values)

        max_diff = max(abs(v - mean) / mean for v in values)

        # 数据质量评分
        if max_diff < 0.001:
            quality = "high"   # <0.1%差异
        elif max_diff < 0.005:
            quality = "medium" # <0.5%差异
        else:
            quality = "low"    # >0.5%差异

        # 加权平均价格
        weights = {"baostock": 0.35, "akshare": 0.35, "eastmoney": 0.15, "sina": 0.15}
        valid_prices = {k: v for k, v in prices.items() if v > 0}
        total_weight = sum(weights.get(k, 0.1) for k in valid_prices.keys())
        weighted_price = sum(
            prices[k] * (weights.get(k, 0.1) / total_weight)
            for k in valid_prices.keys()
        )

        return {
            "validated_price": round(weighted_price, 2),
            "mean_price": round(mean, 2),
            "max_diff_pct": round(max_diff * 100, 3),
            "data_quality": quality,
            "sources_used": list(valid_prices.keys()),
            "is_valid": max_diff < self.DIFF_THRESHOLDS["price"],
            "warnings": [
                f"{k}差异{round(abs(prices[k]-mean)/mean*100,2)}%"
                for k in prices.keys() if abs(prices[k]-mean)/mean > self.DIFF_THRESHOLDS["price"]
            ]
        }
```

---

## 数据质量报告

```markdown
## 数据质量报告

### 交叉验证结果
| 数据类型 | 来源1 | 来源2 | 差异 | 质量评级 |
|----------|--------|--------|------|----------|
| 实时价格 | ¥70.49 | ¥70.48 | 0.01% | ✅ 高 |
| 成交量 | 2.72亿 | 2.71亿 | 0.37% | ✅ 高 |
| ROE | 20.30% | - | - | ⚠️ 单源 |

### 综合数据质量: 92/100 (A级)

### 数据源使用情况
- Baostock: 70% (主数据源)
- akshare: 20% (验证)
- 备用: 10% (备用)
```

---

## 数据新鲜度标识

> ⚠️ **重要**: 所有数据必须标注新鲜度,过期数据需重新获取

```
数据采集时间: YYYY-MM-DD HH:MM:SS
财务数据更新: YYYY-MM-DD（最近财报发布日期）
情绪数据: YYYY-MM-DD HH:MM（最近采集时间）
```

---

## 服务降级策略

当主数据源不可用时,按以下顺序切换:

```
1. Baostock (A股主选)
   ↓ 不可用
2. akshare
   ↓ 不可用
3. 新浪财经/网易财经
   ↓ 不可用
4. 返回"数据获取失败"
   提示: "数据源暂时不可用,请稍后重试"
```

---

## 版本

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.6 | 2026-04-20 | 去除美股,专注A股/港股,添加腾讯财经/东方财富备用源 |
