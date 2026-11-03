# Jack Stock Pick - 杨永兴隔夜套利法

A股尾盘选股策略，严格执行八步筛选法

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas requests akshare
```

### 2. 运行选股

```bash
python scripts/stock_picker.py
```

### 3. 查看结果

结果会显示在终端，同时保存到 `results/jack_stock_pick_YYYYMMDD.csv`

---

## ⚙️ 数据源配置

修改 `scripts/stock_picker.py` 顶部配置：

```python
# 可选: "akshare"(数据最全), "sina"(最稳定), "tushare"(需Token)
DATA_SOURCE = "akshare"
```

| 数据源 | 优点 | 缺点 | 适用场景 |
|--------|------|------|----------|
| **akshare** | 数据最全（换手/量比/市值） | 偶尔不稳定 | 推荐首选 |
| **sina** | 最稳定，无需安装AKShare | 缺少换手/量比/市值数据 | 备用方案 |
| **tushare** | 数据质量最高 | 需注册Token | 专业用户 |

---

## 📊 八步筛选条件

1. 时间窗口：下午2:30之后
2. 主板股票：60开头（上海）或00开头（深圳）
3. 涨幅：3%~5%
4. 活性：近20个交易日内有过涨停
5. 量比：> 1
6. 换手率：5%~10%
7. 市值：50亿~200亿
8. 分时走势：创当天新高后回踩分时均线不破（需人工判断）

---

## ⚠️ 生死铁律

**次日早盘必须清仓**，除非：
- 缩量涨停
- 一字涨停

---

## 📁 文件说明

- `scripts/stock_picker.py` - 主程序（多数据源支持）
- `scripts/test_with_mock_data.py` - 测试脚本（模拟数据）
- `results/` - 筛选结果保存目录

---

## 📝 更新日志

**2025-04-19**
- ✅ 修复涨停筛选逻辑（排除今天涨停）
- ✅ 增加交易日自动判断
- ✅ 支持多数据源（AKShare/新浪财经/Tushare）
- ✅ 修复涨停数据代码匹配问题
